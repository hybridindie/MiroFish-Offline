"""
Graph building service.
Uses GraphStorage (Neo4j) to replace Zep Cloud API.
"""

import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from ..config import Config
from ..models.task import TaskManager, TaskStatus
from ..storage import GraphStorage
from .text_processor import TextProcessor

logger = logging.getLogger('mirofish.graph_builder')


@dataclass
class GraphInfo:
    """Graph information"""
    graph_id: str
    node_count: int
    edge_count: int
    entity_types: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": self.entity_types,
        }


class GraphBuilderService:
    """
    Graph building service
    Build knowledge graph through GraphStorage interface
    """

    def __init__(self, storage: GraphStorage):
        self.storage = storage
        self.task_manager = TaskManager()
        self._active_ontology: Optional[Dict[str, Any]] = None

    def build_graph_async(
        self,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str = "MiroFish Graph",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 3
    ) -> str:
        """
        Build graph asynchronously

        Args:
            text: Input text to process
            ontology: Ontology definition (from ontology generator output)
            graph_name: Name for the graph
            chunk_size: Text chunk size
            chunk_overlap: Chunk overlap size
            batch_size: Number of chunks to send per batch

        Returns:
            Task ID
        """
        # Create task
        task_id = self.task_manager.create_task(
            task_type="graph_build",
            metadata={
                "graph_name": graph_name,
                "chunk_size": chunk_size,
                "text_length": len(text),
            }
        )

        # Execute build in background thread
        thread = threading.Thread(
            target=self._build_graph_worker,
            args=(task_id, text, ontology, graph_name, chunk_size, chunk_overlap, batch_size)
        )
        thread.daemon = True
        thread.start()

        return task_id

    def _build_graph_worker(
        self,
        task_id: str,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int
    ):
        """Graph build worker thread"""
        try:
            self.task_manager.update_task(
                task_id,
                status=TaskStatus.PROCESSING,
                progress=5,
                message="Starting graph building..."
            )

            # 1. Create graph
            graph_id = self.create_graph(graph_name)
            self.task_manager.update_task(
                task_id,
                progress=10,
                message=f"Graph created: {graph_id}"
            )

            # 2. Set ontology
            self.set_ontology(graph_id, ontology)
            self.task_manager.update_task(
                task_id,
                progress=15,
                message="Ontology set"
            )

            # 3. Text chunking
            chunks = TextProcessor.split_text(text, chunk_size, chunk_overlap)
            total_chunks = len(chunks)
            self.task_manager.update_task(
                task_id,
                progress=20,
                message=f"Text split into {total_chunks} chunks"
            )

            # 4. Send data in batches (NER + embedding + Neo4j insert — synchronous)
            episode_uuids = self.add_text_batches(
                graph_id=graph_id,
                chunks=chunks,
                batch_size=batch_size,
                ontology=ontology,
                progress_callback=lambda msg, prog: self.task_manager.update_task(
                    task_id,
                    progress=20 + int(prog * 0.6),  # 20-80%
                    message=msg
                )
            )

            # 5. Wait for processing (no-op for Neo4j — already synchronous)
            self.storage.wait_for_processing(episode_uuids)

            self.task_manager.update_task(
                task_id,
                progress=85,
                message="Data processing completed, getting graph information..."
            )

            # 6. Get graph information
            graph_info = self._get_graph_info(graph_id)

            # Completed
            self.task_manager.complete_task(task_id, {
                "graph_id": graph_id,
                "graph_info": graph_info.to_dict(),
                "chunks_processed": total_chunks,
            })

        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.task_manager.fail_task(task_id, error_msg)

    def create_graph(self, name: str) -> str:
        """Create graph"""
        return self.storage.create_graph(
            name=name,
            description="MiroFish Social Simulation Graph"
        )

    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]):
        """
        SetGraphOntology

        Simply stores ontology as JSON in the Graph node.
        No more dynamic Pydantic class creation (was Zep-specific).
        The NER extractor reads this ontology to guide extraction.
        """
        self.storage.set_ontology(graph_id, ontology)
        self._active_ontology = ontology

    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        ontology: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
        max_workers: Optional[int] = None
    ) -> List[str]:
        """
        Add text chunks to graph in parallel, return uuid list of all episodes.

        Chunks within each batch are submitted concurrently up to `max_workers`
        threads (default: Config.GRAPH_BUILD_WORKERS). NER and embedding calls
        are I/O-bound against Ollama so parallelism gives a real speedup.
        Progress callbacks and error propagation are thread-safe.
        """
        total_chunks = len(chunks)
        total_batches = (total_chunks + batch_size - 1) // batch_size
        effective_ontology = ontology if ontology is not None else self._active_ontology
        workers = max_workers if max_workers is not None else Config.GRAPH_BUILD_WORKERS

        logger.info(
            "[graph_build] Starting: %d chunks, %d batches "
            "(batch_size=%d, workers=%d)",
            total_chunks, total_batches, batch_size, workers
        )

        # Results indexed by original chunk position so ordering is preserved.
        results: Dict[int, str] = {}
        _done_lock = threading.Lock()
        _done_count = [0]  # chunks completed so far (for progress reporting)
        first_error: list = []  # [exception] — populated by first failing thread

        def _process_chunk(chunk_idx: int, chunk: str) -> tuple:
            """Submit one chunk; returns (chunk_idx, episode_id)."""
            chunk_preview = chunk[:80].replace('\n', ' ')
            logger.info(
                "[graph_build] Chunk %d/%d (%d chars): \"%s...\"",
                chunk_idx + 1, total_chunks, len(chunk), chunk_preview
            )
            t0 = time.time()
            episode_id = self.storage.add_text(graph_id, chunk, ontology=effective_ontology)
            elapsed = time.time() - t0
            logger.info(
                "[graph_build] Chunk %d/%d done in %.1fs",
                chunk_idx + 1, total_chunks, elapsed
            )
            return chunk_idx, episode_id

        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1

            if progress_callback:
                progress = i / total_chunks
                progress_callback(
                    f"Processing batch {batch_num}/{total_batches} "
                    f"({len(batch_chunks)} chunks, {workers} worker(s))...",
                    progress
                )

            with ThreadPoolExecutor(max_workers=min(workers, len(batch_chunks))) as executor:
                futures = {
                    executor.submit(_process_chunk, i + j, chunk): (i + j)
                    for j, chunk in enumerate(batch_chunks)
                }
                for future in as_completed(futures):
                    try:
                        chunk_idx, episode_id = future.result()
                        results[chunk_idx] = episode_id
                        with _done_lock:
                            _done_count[0] += 1
                            done_so_far = _done_count[0]
                        if progress_callback:
                            progress_callback(
                                f"Chunk {done_so_far}/{total_chunks} complete "
                                f"(batch {batch_num}/{total_batches})",
                                done_so_far / total_chunks
                            )
                    except Exception as e:
                        chunk_idx = futures[future]
                        logger.error(
                            "[graph_build] Chunk %d/%d FAILED: %s",
                            chunk_idx + 1, total_chunks, e
                        )
                        if not first_error:
                            first_error.append(e)
                            # Cancel not-yet-started futures and stop waiting.
                            for f in futures:
                                f.cancel()
                            break

            if first_error:
                if progress_callback:
                    progress_callback(f"Batch {batch_num} failed: {first_error[0]}", 0)
                raise first_error[0]

        # Return episode UUIDs in original chunk order.
        episode_uuids = [results[k] for k in sorted(results)]

        logger.info(f"[graph_build] All {total_chunks} chunks processed successfully")
        return episode_uuids

    def _get_graph_info(self, graph_id: str) -> GraphInfo:
        """Get graph information"""
        info = self.storage.get_graph_info(graph_id)
        return GraphInfo(
            graph_id=info["graph_id"],
            node_count=info["node_count"],
            edge_count=info["edge_count"],
            entity_types=info.get("entity_types", []),
        )

    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        """Get complete graph data (including details)"""
        return self.storage.get_graph_data(graph_id)

    def delete_graph(self, graph_id: str):
        """Delete graph"""
        self.storage.delete_graph(graph_id)
