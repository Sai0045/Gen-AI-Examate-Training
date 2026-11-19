from app.agent_loop import execute_tool


def test_agent_calculates_vaccine_calendar(monkeypatch):
    fake_result = {
        "date_of_birth": "2026-01-01",
        "today": "2026-11-19",
        "total_doses": 3,
        "doses": [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "upcoming"},
        ],
    }

    monkeypatch.setattr(
        "app.agent_loop.vaccine_due_dates",
        lambda date_of_birth: fake_result,
    )

    decision = {
        "tool": "calculate_vaccine_calendar",
        "date_of_birth": "2026-01-01",
    }

    result = execute_tool(decision, "Calculate vaccine calendar")

    assert result["tool"] == "calculate_vaccine_calendar"
    assert result["total_doses"] == 3
    assert result["status_counts"] == {
        "completed": 2,
        "upcoming": 1,
    }


def test_agent_requests_missing_date_of_birth():
    decision = {
        "tool": "calculate_vaccine_calendar",
        "date_of_birth": None,
    }

    result = execute_tool(decision, "Calculate vaccine calendar")

    assert result["needs_input"] is True
    assert result["calendar"] is None
    assert "date of birth" in result["answer"].lower()


def test_agent_rejects_invalid_date_of_birth():
    decision = {
        "tool": "calculate_vaccine_calendar",
        "date_of_birth": "invalid-date",
    }

    result = execute_tool(decision, "Calculate vaccine calendar")

    assert result["needs_input"] is True
    assert result["calendar"] is None
    assert "valid date" in result["answer"].lower()
