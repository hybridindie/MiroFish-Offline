"""
Graph researcher service.

Runs a post-build enrichment pass that proposes additional ontology-valid
relations between already extracted entities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from ..config import Config
from ..storage.graph_storage import GraphStorage
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('mirofish.graph_researcher')


class GraphResearcherService:
    """Generate additional high-confidence relations over an existing graph."""

    def __init__(self, storage: GraphStorage, llm_client: Optional[LLMClient] = None):
        self.storage = storage
        self.llm = llm_client or LLMClient()

    @staticmethod
    def _relation_types_from_ontology(ontology: Dict[str, Any]) -> List[str]:
        relation_types = ontology.get('relation_types', ontology.get('edge_types', []))
        names: List[str] = []
        for item in relation_types:
            if isinstance(item, dict):
                name = str(item.get('name', '')).strip()
            else:
                name = str(item).strip()
            if name:
                names.append(name)
        return names

    def enrich_graph(
        self,
        graph_id: str,
        ontology: Dict[str, Any],
        max_entities: int = Config.GRAPH_RESEARCHER_MAX_ENTITIES,
        max_relations: int = Config.GRAPH_RESEARCHER_MAX_RELATIONS,
        min_confidence: float = Config.GRAPH_RESEARCHER_MIN_CONFIDENCE,
    ) -> Dict[str, int]:
        nodes = self.storage.get_all_nodes(graph_id, limit=max_entities)
        edges = self.storage.get_all_edges(graph_id)

        if len(nodes) < 2:
            return {'candidates': 0, 'accepted': 0, 'persisted': 0}

        relation_types = self._relation_types_from_ontology(ontology)
        if not relation_types:
            return {'candidates': 0, 'accepted': 0, 'persisted': 0}

        node_name_map: Dict[str, Dict[str, Any]] = {}
        uuid_to_name: Dict[str, str] = {}
        for node in nodes:
            name = str(node.get('name', '')).strip()
            if not name:
                continue
            node_name_map[name.lower()] = node
            node_uuid = str(node.get('uuid', '')).strip()
            if node_uuid:
                uuid_to_name[node_uuid] = name

        if len(node_name_map) < 2:
            return {'candidates': 0, 'accepted': 0, 'persisted': 0}

        existing_pairs: Set[Tuple[str, str, str]] = set()
        for edge in edges:
            source_uuid = str(edge.get('source_node_uuid', '')).strip()
            target_uuid = str(edge.get('target_node_uuid', '')).strip()
            source = uuid_to_name.get(source_uuid, '').lower()
            target = uuid_to_name.get(target_uuid, '').lower()
            rel_type = str(edge.get('name', '')).strip().upper()
            if source and target and rel_type:
                existing_pairs.add((source, target, rel_type))

        entity_lines: List[str] = []
        for node in node_name_map.values():
            labels = node.get('labels', [])
            entity_type = labels[0] if labels else 'Entity'
            entity_lines.append(f"- {node.get('name', '')} ({entity_type})")

        system_prompt = """You are a graph researcher. Propose additional high-confidence relations to enrich an existing graph.

Rules:
1. Use ONLY entity names from the provided entity catalog.
2. Use ONLY relation types from the provided allowed relation types.
3. Do not invent entities.
4. Avoid generic or weak links; keep only materially useful relations.
5. Return ONLY JSON with schema:
{
  "relations": [
    {"source": "...", "target": "...", "type": "...", "fact": "...", "confidence": 0.0}
  ]
}
"""

        user_prompt = f"""Entity Catalog:
{chr(10).join(entity_lines)}

Allowed Relation Types:
{', '.join(relation_types)}

Existing Relations (avoid duplicates):
{chr(10).join(sorted([f"- {s} --[{t}]--> {d}" for s, d, t in existing_pairs]))[:4000]}

Generate up to {max_relations} additional relations with confidence >= {min_confidence}.
"""

        response = self.llm.chat_json(
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
            expected_keys=['relations'],
        )

        candidates = response.get('relations', [])
        if not isinstance(candidates, list):
            return {'candidates': 0, 'accepted': 0, 'persisted': 0}

        allowed_relation_types = {rt.upper() for rt in relation_types}
        accepted: List[Dict[str, Any]] = []

        for item in candidates:
            if not isinstance(item, dict):
                continue

            source = str(item.get('source', '')).strip()
            target = str(item.get('target', '')).strip()
            rel_type = str(item.get('type', '')).strip().upper()
            fact = str(item.get('fact', '')).strip()

            try:
                confidence = float(item.get('confidence', 0.0))
            except (TypeError, ValueError):
                confidence = 0.0

            if not source or not target or not rel_type or not fact:
                continue
            if source.lower() == target.lower():
                continue
            if source.lower() not in node_name_map or target.lower() not in node_name_map:
                continue
            if rel_type not in allowed_relation_types:
                continue
            if confidence < min_confidence:
                continue
            if (source.lower(), target.lower(), rel_type) in existing_pairs:
                continue

            accepted.append({
                'source': source,
                'target': target,
                'type': rel_type,
                'fact': fact,
                'confidence': confidence,
            })

            if len(accepted) >= max_relations:
                break

        persisted = self.storage.add_researched_relations(graph_id, accepted)

        logger.info(
            "[researcher] graph=%s candidates=%d accepted=%d persisted=%d",
            graph_id,
            len(candidates),
            len(accepted),
            persisted,
        )

        return {'candidates': len(candidates), 'accepted': len(accepted), 'persisted': persisted}