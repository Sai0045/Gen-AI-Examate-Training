from fastapi.testclient import TestClient

from app import rag
from app.main import app

client = TestClient(app)


def test_ask_returns_answer_with_citation(monkeypatch):
    fake_hits = [
        {
            "text": "BCG vaccine is given at birth.",
            "source": "MoHFW",
            "page": 10,
            "title": "Immunization Schedule",
            "distance": 0.2,
        }
    ]

    monkeypatch.setattr(rag, "semantic_search", lambda question, k: fake_hits)

    monkeypatch.setattr(
        rag,
        "ask_llm",
        lambda system_prompt, task: (
            '{"answerable": true, '
            '"answer": "BCG is given at birth.", '
            '"citations": [1]}'
        ),
    )

    response = client.post(
        "/ask",
        json={"question": "When is BCG given?", "k": 3},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["answer"] == "BCG is given at birth."
    assert data["answerable"] is True
    assert len(data["citations"]) == 1


def test_ask_returns_fallback_when_no_documents_found(monkeypatch):
    monkeypatch.setattr(rag, "semantic_search", lambda question, k: [])

    response = client.post(
        "/ask",
        json={"question": "Unrelated question", "k": 3},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["answerable"] is False
    assert data["citations"] == []
    assert "I don't know" in data["answer"]
