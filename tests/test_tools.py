from datetime import date

import pytest

from app.tools import (
    add_months,
    add_years,
    age_to_date,
    parse_date,
    vaccine_due_dates,
)


def test_parse_date_accepts_iso_string():
    assert parse_date("2026-01-15") == date(2026, 1, 15)


def test_parse_date_rejects_invalid_string():
    with pytest.raises(ValueError):
        parse_date("15-01-2026")


def test_age_to_date_calculates_weeks():
    assert age_to_date(date(2026, 1, 1), 6, "weeks") == date(2026, 2, 12)


def test_add_months_handles_month_end():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_add_years_handles_leap_day():
    assert add_years(date(2024, 2, 29), 1) == date(2025, 2, 28)


def test_vaccine_calendar_rejects_future_dob():
    with pytest.raises(ValueError, match="future"):
        vaccine_due_dates("2027-01-01", today="2026-11-24")
