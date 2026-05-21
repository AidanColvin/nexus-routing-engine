from backend.pipeline.verifier import verify_source_tier

CFG = {"primary": ["pubmed", "sec"], "secondary": ["linkedin"]}


def test_primary_source():
    assert verify_source_tier("pubmed", CFG) == 1.0


def test_secondary_source():
    assert verify_source_tier("linkedin", CFG) == 0.5


def test_unknown_source():
    assert verify_source_tier("random_blog", CFG) == 0.0
