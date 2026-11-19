from app.records import load_records
from app.smart_search import SmartSearch


def test_smart_search_finds_bcg():
    records = load_records()
    engine = SmartSearch(records)

    results = engine.search("BCG vaccine")

    assert len(results) > 0
    assert any("BCG" in result["vaccine"] for result in results)


def test_smart_search_returns_scores():
    records = load_records()
    engine = SmartSearch(records)

    results = engine.search("polio vaccine")

    assert len(results) > 0
    assert all("score" in result for result in results)
    assert all(result["score"] > 0 for result in results)


def test_smart_search_respects_top_k():
    records = load_records()
    engine = SmartSearch(records)

    results = engine.search("vaccine", top_k=2)

    assert len(results) <= 2


def test_smart_search_returns_empty_for_unrelated_query():
    records = load_records()
    engine = SmartSearch(records)

    results = engine.search("xyznonexistenttopic123")

    assert results == []
