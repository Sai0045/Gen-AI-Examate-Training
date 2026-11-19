from app.records import count_by, get_by_id, load_records, search


def test_load_records_returns_records():
    records = load_records()

    assert isinstance(records, list)
    assert len(records) > 0


def test_load_records_assigns_unique_ids():
    records = load_records()

    ids = [record["id"] for record in records]

    assert len(ids) == len(set(ids))
    assert all(isinstance(record_id, int) for record_id in ids)


def test_search_is_case_insensitive():
    records = [
        {"id": 1, "vaccine": "BCG"},
        {"id": 2, "vaccine": "OPV"},
    ]

    results = search(records, "bcg")

    assert len(results) == 1
    assert results[0]["vaccine"] == "BCG"


def test_count_by_groups_records():
    records = [
        {"vaccine": "BCG"},
        {"vaccine": "OPV"},
        {"vaccine": "BCG"},
    ]

    counts = count_by(records, "vaccine")

    assert counts == {"BCG": 2, "OPV": 1}


def test_get_by_id_returns_matching_record():
    records = [
        {"id": 1, "vaccine": "BCG"},
        {"id": 2, "vaccine": "OPV"},
    ]

    result = get_by_id(records, 2)

    assert result == {"id": 2, "vaccine": "OPV"}


def test_get_by_id_returns_none_for_missing_id():
    records = [{"id": 1, "vaccine": "BCG"}]

    assert get_by_id(records, 99) is None
