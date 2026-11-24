from ui import storage


def setup_test_database(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        storage,
        "DB_PATH",
        tmp_path / "test_teekatimer.db"
    )
    storage.init_db()


def test_save_and_get_completed_dose(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    storage.save_dose_status(
        "2026-01-01", 1, 1, True
    )

    assert storage.get_completed_doses("2026-01-01") == {
        (1, 1)
    }


def test_unmark_completed_dose(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    storage.save_dose_status(
        "2026-01-01", 1, 1, True
    )

    storage.save_dose_status(
        "2026-01-01", 1, 1, False
    )

    assert storage.get_completed_doses("2026-01-01") == set()


def test_completed_doses_are_separate_by_dob(
    monkeypatch, tmp_path
):
    setup_test_database(monkeypatch, tmp_path)

    storage.save_dose_status(
        "2026-01-01", 1, 1, True
    )

    assert storage.get_completed_doses("2026-01-01") == {
        (1, 1)
    }
    assert storage.get_completed_doses("2026-02-01") == set()


def test_marking_same_dose_twice_does_not_duplicate(
    monkeypatch, tmp_path
):
    setup_test_database(monkeypatch, tmp_path)

    storage.save_dose_status(
        "2026-01-01", 1, 1, True
    )
    storage.save_dose_status(
        "2026-01-01", 1, 1, True
    )

    assert storage.get_completed_doses("2026-01-01") == {
        (1, 1)
    }
