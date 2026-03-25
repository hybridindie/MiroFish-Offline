from app.services.graph_researcher import GraphResearcherService


class FakeStorage:
    def __init__(self):
        self.persisted = []

    def get_all_nodes(self, graph_id, limit=2000):
        return [
            {"uuid": "n1", "name": "OnlyFans", "labels": ["Platform"]},
            {"uuid": "n2", "name": "Creator A", "labels": ["Creator"]},
            {"uuid": "n3", "name": "Fanvue", "labels": ["Platform"]},
        ]

    def get_all_edges(self, graph_id):
        return [
            {
                "source_node_uuid": "n2",
                "target_node_uuid": "n1",
                "name": "POSTS_ON",
            }
        ]

    def add_researched_relations(self, graph_id, relations):
        self.persisted = relations
        return len(relations)


class FakeLLM:
    def chat_json(self, messages, temperature, max_tokens, expected_keys):
        return {
            "relations": [
                {
                    "source": "Creator A",
                    "target": "OnlyFans",
                    "type": "POSTS_ON",
                    "fact": "Creator A posts content on OnlyFans.",
                    "confidence": 0.9,
                },
                {
                    "source": "Creator A",
                    "target": "Fanvue",
                    "type": "POSTS_ON",
                    "fact": "Creator A also posts on Fanvue.",
                    "confidence": 0.82,
                },
                {
                    "source": "Ghost Entity",
                    "target": "Fanvue",
                    "type": "POSTS_ON",
                    "fact": "Invalid because source does not exist.",
                    "confidence": 0.99,
                },
                {
                    "source": "Creator A",
                    "target": "Fanvue",
                    "type": "SPONSORS",
                    "fact": "Invalid because relation type is not allowed.",
                    "confidence": 0.95,
                },
            ]
        }


def test_graph_researcher_filters_and_persists_relations():
    storage = FakeStorage()
    researcher = GraphResearcherService(storage=storage, llm_client=FakeLLM())

    stats = researcher.enrich_graph(
        graph_id="g1",
        ontology={
            "entity_types": ["Creator", "Platform"],
            "relation_types": ["POSTS_ON"],
        },
        max_relations=10,
        min_confidence=0.6,
    )

    assert stats["candidates"] == 4
    assert stats["accepted"] == 1
    assert stats["persisted"] == 1
    assert storage.persisted[0]["source"] == "Creator A"
    assert storage.persisted[0]["target"] == "Fanvue"
    assert storage.persisted[0]["type"] == "POSTS_ON"