"""
Neo4jStorage — Neo4j Community Edition implementation of GraphStorage.

Replaces all Zep Cloud API calls with local Neo4j Cypher queries.
Includes: CRUD, NER/RE-based text ingestion, hybrid search, retry logic.
"""

import json
import re
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable

from neo4j import GraphDatabase, Session as Neo4jSession
from neo4j.exceptions import (
    TransientError,
    ServiceUnavailable,
    SessionExpired,
)

from ..config import Config
from .graph_storage import GraphStorage
from .embedding_service import EmbeddingService
from .ner_extractor import NERExtractor
from .search_service import SearchService
from . import neo4j_schema

logger = logging.getLogger('mirofish.neo4j_storage')


class Neo4jStorage(GraphStorage):
    """Neo4j CE implementation of the GraphStorage interface."""

    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 1  # seconds

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None,
        ner_extractor: Optional[NERExtractor] = None,
    ):
        self._uri = uri or Config.NEO4J_URI
        self._user = user or Config.NEO4J_USER
        self._password = password or Config.NEO4J_PASSWORD

        self._driver = GraphDatabase.driver(
            self._uri, auth=(self._user, self._password)
        )
        self._embedding = embedding_service or EmbeddingService()
        self._ner = ner_extractor or NERExtractor()
        self._search = SearchService(self._embedding)

        # Initialize schema (indexes, constraints)
        self._ensure_schema()

    def close(self):
        """Close the Neo4j driver connection."""
        self._driver.close()

    def _ensure_schema(self):
        """Create indexes and constraints if they don't exist."""
        with self._driver.session() as session:
            for query in neo4j_schema.ALL_SCHEMA_QUERIES:
                try:
                    session.run(query)
                except Exception as e:
                    logger.warning(f"Schema query warning (may already exist): {e}")

    # ----------------------------------------------------------------
    # Retry wrapper
    # ----------------------------------------------------------------

    def _call_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry on Neo4j transient errors.
        Replaces 3 different retry patterns from the Zep codebase.
        """
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (TransientError, ServiceUnavailable, SessionExpired) as e:
                last_error = e
                wait = self.RETRY_DELAY_BASE * (2 ** attempt)
                logger.warning(
                    f"Neo4j transient error (attempt {attempt + 1}/{self.MAX_RETRIES}), "
                    f"retrying in {wait}s: {e}"
                )
                time.sleep(wait)
            except Exception:
                raise

        raise last_error  # type: ignore

    # ----------------------------------------------------------------
    # Graph lifecycle
    # ----------------------------------------------------------------

    def create_graph(self, name: str, description: str = "") -> str:
        graph_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        def _create(tx):
            tx.run(
                """
                CREATE (g:Graph {
                    graph_id: $graph_id,
                    name: $name,
                    description: $description,
                    ontology_json: '{}',
                    created_at: $created_at
                })
                """,
                graph_id=graph_id,
                name=name,
                description=description,
                created_at=now,
            )

        with self._driver.session() as session:
            self._call_with_retry(session.execute_write, _create)

        logger.info(f"Created graph '{name}' with id {graph_id}")
        return graph_id

    def delete_graph(self, graph_id: str) -> None:
        def _delete(tx):
            # Delete all entities and their relationships
            tx.run(
                "MATCH (n {graph_id: $gid}) DETACH DELETE n",
                gid=graph_id,
            )
            # Delete graph node
            tx.run(
                "MATCH (g:Graph {graph_id: $gid}) DELETE g",
                gid=graph_id,
            )

        with self._driver.session() as session:
            self._call_with_retry(session.execute_write, _delete)
        logger.info(f"Deleted graph {graph_id}")

    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        def _set(tx):
            tx.run(
                """
                MATCH (g:Graph {graph_id: $gid})
                SET g.ontology_json = $ontology_json
                """,
                gid=graph_id,
                ontology_json=json.dumps(ontology, ensure_ascii=False),
            )

        with self._driver.session() as session:
            self._call_with_retry(session.execute_write, _set)

    def get_ontology(self, graph_id: str) -> Dict[str, Any]:
        with self._driver.session() as session:
            result = session.run(
                "MATCH (g:Graph {graph_id: $gid}) RETURN g.ontology_json AS oj",
                gid=graph_id,
            )
            record = result.single()
            if record and record["oj"]:
                return json.loads(record["oj"])
            return {}

    # ----------------------------------------------------------------
    # Add data (NER → nodes/edges)
    # ----------------------------------------------------------------

    def add_text(
        self,
        graph_id: str,
        text: str,
        ontology: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Process text: NER/RE → batch embed → create nodes/edges → return episode_id."""
        episode_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Reuse pre-fetched ontology when available to avoid one DB read per chunk.
        if ontology is None:
            ontology = self.get_ontology(graph_id)

        # Extract entities and relations
        logger.info(f"[add_text] Starting NER extraction for chunk ({len(text)} chars)...")
        extraction = self._ner.extract(text, ontology)
        entities = extraction.get("entities", [])
        relations = extraction.get("relations", [])

        logger.info(
            f"[add_text] NER done: {len(entities)} entities, {len(relations)} relations"
        )

        # --- Batch embed all texts at once ---
        entity_summaries = [f"{e['name']} ({e['type']})" for e in entities]
        fact_texts = [r.get("fact", f"{r['source']} {r['type']} {r['target']}") for r in relations]

        # Entity embeddings are always computed (needed for vector search).
        entity_embeddings: list = []
        if entity_summaries:
            logger.info(f"[add_text] Embedding {len(entity_summaries)} entities...")
            try:
                entity_embeddings = self._embedding.embed_batch(entity_summaries)
            except Exception as e:
                logger.warning(f"[add_text] Entity embedding failed, using empty vectors: {e}")
                entity_embeddings = [[] for _ in entity_summaries]

        # Relation embeddings may be deferred to save latency during bulk build.
        defer_rel_embed = Config.DEFER_RELATION_EMBEDDINGS
        relation_embeddings: list = []
        if fact_texts and not defer_rel_embed:
            logger.info(f"[add_text] Embedding {len(fact_texts)} relations...")
            try:
                relation_embeddings = self._embedding.embed_batch(fact_texts)
            except Exception as e:
                logger.warning(f"[add_text] Relation embedding failed, using empty vectors: {e}")
                relation_embeddings = [[] for _ in fact_texts]
        elif fact_texts and defer_rel_embed:
            logger.debug("[add_text] Relation embeddings deferred (DEFER_RELATION_EMBEDDINGS=true)")
            relation_embeddings = [[] for _ in fact_texts]

        logger.info(f"[add_text] Embedding done, writing to Neo4j...")

        with self._driver.session() as session:
            # Create episode node
            def _create_episode(tx):
                tx.run(
                    """
                    CREATE (ep:Episode {
                        uuid: $uuid,
                        graph_id: $graph_id,
                        data: $data,
                        processed: true,
                        created_at: $created_at
                    })
                    """,
                    uuid=episode_id,
                    graph_id=graph_id,
                    data=text,
                    created_at=now,
                )

            self._call_with_retry(session.execute_write, _create_episode)

            # MERGE entities in one UNWIND write (upsert by graph_id + name_lower)
            entity_rows: List[Dict[str, Any]] = []
            labels_by_type: Dict[str, List[str]] = {}
            for idx, entity in enumerate(entities):
                ename = entity["name"]
                etype = entity.get("type", "Entity")
                attrs = entity.get("attributes", {})
                summary_text = entity_summaries[idx]
                embedding = entity_embeddings[idx] if idx < len(entity_embeddings) else []
                name_lower = ename.lower()

                entity_rows.append({
                    "name_lower": name_lower,
                    "uuid": str(uuid.uuid4()),
                    "name": ename,
                    "summary": summary_text,
                    "attrs_json": json.dumps(attrs, ensure_ascii=False),
                    "embedding": embedding,
                })

                if etype and etype != "Entity":
                    labels_by_type.setdefault(etype, []).append(name_lower)

            entity_uuid_map: Dict[str, str] = {}
            if entity_rows:
                def _merge_entities(tx):
                    result = tx.run(
                        """
                        UNWIND $rows AS row
                        MERGE (n:Entity {graph_id: $gid, name_lower: row.name_lower})
                        ON CREATE SET
                            n.uuid = row.uuid,
                            n.name = row.name,
                            n.summary = row.summary,
                            n.attributes_json = row.attrs_json,
                            n.embedding = row.embedding,
                            n.created_at = $now
                        ON MATCH SET
                            n.summary = CASE WHEN n.summary = '' OR n.summary IS NULL
                                THEN row.summary ELSE n.summary END,
                            n.attributes_json = row.attrs_json,
                            n.embedding = row.embedding
                        RETURN row.name_lower AS name_lower, n.uuid AS uuid
                        """,
                        gid=graph_id,
                        rows=entity_rows,
                        now=now,
                    )
                    return {record["name_lower"]: record["uuid"] for record in result}

                entity_uuid_map = self._call_with_retry(session.execute_write, _merge_entities)

            # Add entity type labels in grouped UNWIND writes (one query per label type)
            for etype, name_lowers in labels_by_type.items():
                try:
                    # Sanitize the label coming from LLM output: escape backticks by
                    # doubling them (Neo4j convention) so they cannot break the query.
                    safe_etype = re.sub(r'[^\w ]', '', etype).strip().replace(' ', '_') or 'Unknown'
                    def _add_label_group(tx, _name_lowers=name_lowers, _safe_etype=safe_etype):
                        tx.run(
                            f"""
                            UNWIND $name_lowers AS nl
                            MATCH (n:Entity {{graph_id: $gid, name_lower: nl}})
                            SET n:`{_safe_etype}`
                            """,
                            gid=graph_id,
                            name_lowers=_name_lowers,
                        )

                    self._call_with_retry(session.execute_write, _add_label_group)
                except Exception as e:
                    logger.warning("Failed to add label '%s' to %d entities: %s", safe_etype, len(name_lowers), e)

            # Create relations in one UNWIND write
            relation_rows: List[Dict[str, Any]] = []
            for idx, relation in enumerate(relations):
                source_name = relation["source"]
                target_name = relation["target"]
                source_uuid = entity_uuid_map.get(source_name.lower())
                target_uuid = entity_uuid_map.get(target_name.lower())

                if not source_uuid or not target_uuid:
                    logger.warning(
                        "Skipping relation %s->%s: entity not found in extraction results",
                        source_name,
                        target_name,
                    )
                    continue

                relation_rows.append({
                    "src_uuid": source_uuid,
                    "tgt_uuid": target_uuid,
                    "uuid": str(uuid.uuid4()),
                    "name": relation["type"],
                    "fact": relation["fact"],
                    "fact_embedding": relation_embeddings[idx] if idx < len(relation_embeddings) else [],
                    "episode_id": episode_id,
                })

            if relation_rows:
                def _create_relations(tx):
                    tx.run(
                        """
                        UNWIND $rows AS row
                        MATCH (src:Entity {uuid: row.src_uuid})
                        MATCH (tgt:Entity {uuid: row.tgt_uuid})
                        CREATE (src)-[r:RELATION {
                            uuid: row.uuid,
                            graph_id: $gid,
                            name: row.name,
                            fact: row.fact,
                            fact_embedding: row.fact_embedding,
                            attributes_json: '{}',
                            episode_ids: [row.episode_id],
                            created_at: $now,
                            valid_at: null,
                            invalid_at: null,
                            expired_at: null
                        }]->(tgt)
                        """,
                        gid=graph_id,
                        rows=relation_rows,
                        now=now,
                    )

                self._call_with_retry(session.execute_write, _create_relations)

        logger.info(f"[add_text] Chunk done: episode={episode_id}")
        return episode_id

    def add_text_batch(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        progress_callback: Optional[Callable] = None,
    ) -> List[str]:
        """Batch-add text chunks with progress reporting."""
        episode_ids = []
        total = len(chunks)

        for i, chunk in enumerate(chunks):
            if not chunk or not chunk.strip():
                continue
            episode_id = self.add_text(graph_id, chunk)
            episode_ids.append(episode_id)

            if progress_callback:
                progress = (i + 1) / total
                progress_callback(progress)

            logger.info(f"Processed chunk {i + 1}/{total}")

        return episode_ids

    def embed_pending_relations(self, graph_id: str) -> int:
        """
        Back-fill relation embeddings that were stored as empty vectors.

        Use this after a build completed with DEFER_RELATION_EMBEDDINGS=true
        to compute and persist fact embeddings without blocking the build.

        Returns:
            Number of relations updated.
        """
        # Fetch all relations with empty/missing fact_embedding
        def _fetch_pending(tx):
            result = tx.run(
                """
                MATCH ()-[r:RELATION {graph_id: $gid}]->()
                WHERE r.fact_embedding IS NULL OR size(r.fact_embedding) = 0
                RETURN r.uuid AS uuid, r.fact AS fact
                """,
                gid=graph_id,
            )
            return [(record["uuid"], record["fact"] or "") for record in result]

        with self._driver.session() as session:
            pending = self._call_with_retry(session.execute_read, _fetch_pending)

        if not pending:
            logger.info("[embed_pending_relations] No pending relations for graph %s", graph_id)
            return 0

        uuids = [p[0] for p in pending]
        facts = [p[1] for p in pending]
        logger.info(
            "[embed_pending_relations] Computing embeddings for %d relations in graph %s",
            len(pending), graph_id
        )

        try:
            embeddings = self._embedding.embed_batch(facts)
        except Exception as e:
            logger.error("[embed_pending_relations] Embedding failed: %s", e)
            return 0

        # Write embeddings back in one UNWIND transaction
        rows = [{"uuid": u, "embedding": emb} for u, emb in zip(uuids, embeddings)]
        def _write_embeddings(tx):
            result = tx.run(
                """
                UNWIND $rows AS row
                MATCH ()-[r:RELATION {graph_id: $gid, uuid: row.uuid}]->()
                SET r.fact_embedding = row.embedding
                RETURN count(r) AS updated
                """,
                rows=rows,
                gid=graph_id,
            )
            record = result.single()
            return record["updated"] if record else 0

        with self._driver.session() as session:
            updated_count = self._call_with_retry(session.execute_write, _write_embeddings)

        logger.info("[embed_pending_relations] Updated %d relations", updated_count)
        return updated_count

    def add_researched_relations(
        self,
        graph_id: str,
        relations: List[Dict[str, Any]],
    ) -> int:
        """Persist researcher-generated relations using entity names as anchors."""
        if not relations:
            return 0

        fact_texts = [str(item.get('fact', '')).strip() for item in relations]
        embeddings: List[List[float]] = []

        if any(fact_texts) and not Config.DEFER_RELATION_EMBEDDINGS:
            try:
                embeddings = self._embedding.embed_batch(fact_texts)
            except Exception as e:
                logger.warning("[researcher] Relation embedding failed, storing empty vectors: %s", e)
                embeddings = [[] for _ in relations]
        else:
            embeddings = [[] for _ in relations]

        rows: List[Dict[str, Any]] = []
        for idx, relation in enumerate(relations):
            source = str(relation.get('source', '')).strip()
            target = str(relation.get('target', '')).strip()
            rel_type = str(relation.get('type', '')).strip()
            fact = str(relation.get('fact', '')).strip()
            confidence = relation.get('confidence')

            if not source or not target or not rel_type or not fact:
                continue

            try:
                confidence_value = float(confidence) if confidence is not None else None
            except (TypeError, ValueError):
                confidence_value = None

            rows.append({
                'source_lower': source.lower(),
                'target_lower': target.lower(),
                'name': rel_type,
                'fact': fact,
                'uuid': str(uuid.uuid4()),
                'fact_embedding': embeddings[idx] if idx < len(embeddings) else [],
                'attributes_json': json.dumps({
                    'origin': 'researcher',
                    'confidence': confidence_value,
                }, ensure_ascii=False),
            })

        if not rows:
            return 0

        now = datetime.now(timezone.utc).isoformat()

        def _write(tx):
            result = tx.run(
                """
                UNWIND $rows AS row
                MATCH (src:Entity {graph_id: $gid, name_lower: row.source_lower})
                MATCH (tgt:Entity {graph_id: $gid, name_lower: row.target_lower})
                MERGE (src)-[r:RELATION {graph_id: $gid, name: row.name, fact: row.fact}]->(tgt)
                ON CREATE SET
                    r.uuid = row.uuid,
                    r.fact_embedding = row.fact_embedding,
                    r.attributes_json = row.attributes_json,
                    r.episode_ids = [],
                    r.created_at = $now,
                    r.valid_at = null,
                    r.invalid_at = null,
                    r.expired_at = null
                RETURN count(r) AS total
                """,
                gid=graph_id,
                rows=rows,
                now=now,
            )
            record = result.single()
            return int(record['total']) if record and record['total'] is not None else 0

        with self._driver.session() as session:
            total = self._call_with_retry(session.execute_write, _write)

        logger.info("[researcher] Persisted %d researched relations for graph %s", total, graph_id)
        return total

    def wait_for_processing(
        self,
        episode_ids: List[str],
        progress_callback: Optional[Callable] = None,
        timeout: int = 600,
    ) -> None:
        """No-op — processing is synchronous in Neo4j."""
        if progress_callback:
            progress_callback(1.0)

    # ----------------------------------------------------------------
    # Read nodes
    # ----------------------------------------------------------------

    def get_all_nodes(self, graph_id: str, limit: int = 2000) -> List[Dict[str, Any]]:
        def _read(tx):
            result = tx.run(
                """
                MATCH (n:Entity {graph_id: $gid})
                RETURN n, labels(n) AS labels
                ORDER BY n.created_at DESC
                LIMIT $limit
                """,
                gid=graph_id,
                limit=limit,
            )
            return [self._node_to_dict(record["n"], record["labels"]) for record in result]

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    def get_node(self, uuid: str) -> Optional[Dict[str, Any]]:
        def _read(tx):
            result = tx.run(
                "MATCH (n:Entity {uuid: $uuid}) RETURN n, labels(n) AS labels",
                uuid=uuid,
            )
            record = result.single()
            if record:
                return self._node_to_dict(record["n"], record["labels"])
            return None

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    def get_node_edges(self, node_uuid: str) -> List[Dict[str, Any]]:
        """O(1) Cypher — NOT full scan + filter like the old Zep code."""
        def _read(tx):
            result = tx.run(
                """
                MATCH (n:Entity {uuid: $uuid})-[r:RELATION]-(m:Entity)
                RETURN r, startNode(r).uuid AS src_uuid, endNode(r).uuid AS tgt_uuid
                """,
                uuid=node_uuid,
            )
            return [
                self._edge_to_dict(record["r"], record["src_uuid"], record["tgt_uuid"])
                for record in result
            ]

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    def get_nodes_by_label(self, graph_id: str, label: str) -> List[Dict[str, Any]]:
        def _read(tx):
            # Dynamic label in query (safe — label comes from ontology, not user input)
            query = f"""
                MATCH (n:Entity:`{label}` {{graph_id: $gid}})
                RETURN n, labels(n) AS labels
            """
            result = tx.run(query, gid=graph_id)
            return [self._node_to_dict(record["n"], record["labels"]) for record in result]

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    # ----------------------------------------------------------------
    # Read edges
    # ----------------------------------------------------------------

    def get_all_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        def _read(tx):
            result = tx.run(
                """
                MATCH (src:Entity)-[r:RELATION {graph_id: $gid}]->(tgt:Entity)
                RETURN r, src.uuid AS src_uuid, tgt.uuid AS tgt_uuid
                ORDER BY r.created_at DESC
                """,
                gid=graph_id,
            )
            return [
                self._edge_to_dict(record["r"], record["src_uuid"], record["tgt_uuid"])
                for record in result
            ]

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    # ----------------------------------------------------------------
    # Search
    # ----------------------------------------------------------------

    def search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10,
        scope: str = "edges",
    ):
        """
        Hybrid search — returns results matching the scope.

        Returns a dict with 'edges' and/or 'nodes' lists
        (callers like zep_tools will wrap into SearchResult).
        """
        result = {"edges": [], "nodes": [], "query": query}

        with self._driver.session() as session:
            if scope in ("edges", "both"):
                result["edges"] = self._search.search_edges(
                    session, graph_id, query, limit
                )

            if scope in ("nodes", "both"):
                result["nodes"] = self._search.search_nodes(
                    session, graph_id, query, limit
                )

        return result

    # ----------------------------------------------------------------
    # Graph info
    # ----------------------------------------------------------------

    def get_graph_info(self, graph_id: str) -> Dict[str, Any]:
        def _read(tx):
            # Count nodes
            node_result = tx.run(
                "MATCH (n:Entity {graph_id: $gid}) RETURN count(n) AS cnt",
                gid=graph_id,
            )
            node_count = node_result.single()["cnt"]

            # Count edges
            edge_result = tx.run(
                "MATCH ()-[r:RELATION {graph_id: $gid}]->() RETURN count(r) AS cnt",
                gid=graph_id,
            )
            edge_count = edge_result.single()["cnt"]

            # Distinct entity types
            label_result = tx.run(
                """
                MATCH (n:Entity {graph_id: $gid})
                UNWIND labels(n) AS lbl
                WITH lbl WHERE lbl <> 'Entity'
                RETURN DISTINCT lbl
                """,
                gid=graph_id,
            )
            entity_types = [record["lbl"] for record in label_result]

            return {
                "graph_id": graph_id,
                "node_count": node_count,
                "edge_count": edge_count,
                "entity_types": entity_types,
            }

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        """
        Full graph dump with enriched edge format (for frontend).
        Includes derived fields: fact_type, source_node_name, target_node_name.
        """
        def _read(tx):
            # Get all nodes
            node_result = tx.run(
                """
                MATCH (n:Entity {graph_id: $gid})
                RETURN n, labels(n) AS labels
                """,
                gid=graph_id,
            )
            nodes = []
            node_map: Dict[str, str] = {}  # uuid -> name
            for record in node_result:
                nd = self._node_to_dict(record["n"], record["labels"])
                nodes.append(nd)
                node_map[nd["uuid"]] = nd["name"]

            # Get all edges with source/target node names (JOIN)
            edge_result = tx.run(
                """
                MATCH (src:Entity)-[r:RELATION {graph_id: $gid}]->(tgt:Entity)
                RETURN r, src.uuid AS src_uuid, tgt.uuid AS tgt_uuid,
                       src.name AS src_name, tgt.name AS tgt_name
                """,
                gid=graph_id,
            )
            edges = []
            for record in edge_result:
                ed = self._edge_to_dict(record["r"], record["src_uuid"], record["tgt_uuid"])
                # Enriched fields for frontend
                ed["fact_type"] = ed["name"]
                ed["source_node_name"] = record["src_name"] or ""
                ed["target_node_name"] = record["tgt_name"] or ""
                # Legacy alias
                ed["episodes"] = ed.get("episode_ids", [])
                edges.append(ed)

            return {
                "graph_id": graph_id,
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges),
            }

        with self._driver.session() as session:
            return self._call_with_retry(session.execute_read, _read)

    # ----------------------------------------------------------------
    # Dict conversion helpers
    # ----------------------------------------------------------------

    @staticmethod
    def _node_to_dict(node, labels: List[str]) -> Dict[str, Any]:
        """Convert Neo4j node to the standard node dict format."""
        props = dict(node)
        attrs_json = props.pop("attributes_json", "{}")
        try:
            attributes = json.loads(attrs_json) if attrs_json else {}
        except (json.JSONDecodeError, TypeError):
            attributes = {}

        # Remove internal fields from dict
        props.pop("embedding", None)
        props.pop("name_lower", None)

        return {
            "uuid": props.get("uuid", ""),
            "name": props.get("name", ""),
            "labels": [l for l in labels if l != "Entity"] if labels else [],
            "summary": props.get("summary", ""),
            "attributes": attributes,
            "created_at": props.get("created_at"),
        }

    @staticmethod
    def _edge_to_dict(rel, source_uuid: str, target_uuid: str) -> Dict[str, Any]:
        """Convert Neo4j relationship to the standard edge dict format."""
        props = dict(rel)
        attrs_json = props.pop("attributes_json", "{}")
        try:
            attributes = json.loads(attrs_json) if attrs_json else {}
        except (json.JSONDecodeError, TypeError):
            attributes = {}

        # Remove internal fields
        props.pop("fact_embedding", None)

        episode_ids = props.get("episode_ids", [])
        if episode_ids and not isinstance(episode_ids, list):
            episode_ids = [str(episode_ids)]

        return {
            "uuid": props.get("uuid", ""),
            "name": props.get("name", ""),
            "fact": props.get("fact", ""),
            "source_node_uuid": source_uuid,
            "target_node_uuid": target_uuid,
            "attributes": attributes,
            "created_at": props.get("created_at"),
            "valid_at": props.get("valid_at"),
            "invalid_at": props.get("invalid_at"),
            "expired_at": props.get("expired_at"),
            "episode_ids": episode_ids,
        }
