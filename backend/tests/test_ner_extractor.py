from app.storage.ner_extractor import NERExtractor


class FakeLLM:
    pass


def test_validate_and_clean_dedupes_common_org_suffix_variants():
    extractor = NERExtractor(llm_client=FakeLLM())

    raw = {
        "entities": [
            {"name": "Meta", "type": "Organization", "attributes": {}},
            {"name": "meta", "type": "Organization", "attributes": {}},
            {"name": "Meta Incorporated", "type": "Organization", "attributes": {}},
            {"name": "TikTok", "type": "Platform", "attributes": {}},
        ],
        "relations": [],
    }

    cleaned = extractor._validate_and_clean(raw, ontology={"entity_types": ["Organization", "Platform"]})
    names = sorted([entity["name"] for entity in cleaned["entities"]])

    assert names == ["Meta", "TikTok"]


def test_validate_and_clean_remaps_relation_aliases_to_canonical_name():
    extractor = NERExtractor(llm_client=FakeLLM())

    raw = {
        "entities": [
            {"name": "Meta", "type": "Organization", "attributes": {}},
            {"name": "YouTube", "type": "Platform", "attributes": {}},
        ],
        "relations": [
            {
                "source": "Meta Incorporated",
                "target": "YouTube",
                "type": "COMPETES_WITH",
                "fact": "Meta Incorporated competes with YouTube for creators.",
            }
        ],
    }

    cleaned = extractor._validate_and_clean(raw, ontology={"entity_types": ["Organization", "Platform"]})

    assert len(cleaned["relations"]) == 1
    assert cleaned["relations"][0]["source"] == "Meta"
    assert cleaned["relations"][0]["target"] == "YouTube"
