from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.records import load_records
from app.smart_search import SmartSearch

app = FastAPI(title="TeekaTimer")

records = load_records()
engine = SmartSearch(records)

SAFETY_NOTE = ("This is information from official MoHFW documents, not medical advice. "
               "Please confirm with your ANM, anganwadi worker or doctor.")


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok", "records": len(records)}


@app.get("/records")
def list_records(limit: int = 10):
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    for r in records:
        if r["id"] == record_id:
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/search")
def search(q: str):
    return {"query": q, "results": engine.search(q)}


@app.post("/questions")
def ask(body: Question):
    hits = engine.search(body.question, top_k=3)

    # no match, or only a very weak match: do not guess about a baby's health
    if len(hits) == 0 or hits[0]["score"] < 0.1:
        return {
            "answer": "I don't know. This is not in the MoHFW immunization schedule I have.",
            "matches": [],
            "note": SAFETY_NOTE,
        }

    top = hits[0]
    answer = (top["vaccine"] + ": due " + top["due_age"] + " (latest: " + top["latest_age"] + "). "
              + "Dose " + top["dose"] + ", " + top["route_site"] + ". "
              + "Protects against: " + top["protects_against"] + ".")
    return {"answer": answer, "matches": hits, "note": SAFETY_NOTE}
