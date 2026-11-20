
from uuid import uuid4

from chromadb.errors import ChromaError
from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from app.chat import chat_answer
from app.chunking import make_chunks
from app.graph import agent_graph
from app.records import load_records
from app.smart_search import SmartSearch
from app.vectorstore import get_collection, index_chunks

app = FastAPI(title="TeekaTimer")


@app.on_event("startup")
def build_rag_index_if_empty():
    collection = get_collection()
    if collection.count() == 0:
        chunks = make_chunks()
        if chunks:
            print("Building RAG index from source documents...")
            count = index_chunks(chunks)
            print(f"RAG index ready: {count} chunks indexed.")
        else:
            print("Warning: No source documents found for RAG indexing.")

records = load_records()
engine = SmartSearch(records)

SAFETY_NOTE = (
    "This is information from official MoHFW documents, not medical advice. "
    "Please confirm with your ANM, anganwadi worker or doctor."
)


class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    version: str = "v2"


class AskRequest(BaseModel):
    question: str
    k: int = 3


class AgentRequest(BaseModel):
    question: str
    thread_id: str | None = None
    approved: bool | None = None


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

    if len(hits) == 0 or hits[0]["score"] < 0.1:
        return {
            "answer": "I don't know. This is not in the MoHFW immunization schedule I have.",
            "matches": [],
            "note": SAFETY_NOTE,
        }

    top = hits[0]

    answer = (
        top["vaccine"]
        + ": due " + top["due_age"]
        + " (latest: " + top["latest_age"] + "). "
        + "Dose " + top["dose"]
        + ", " + top["route_site"] + ". "
        + "Protects against: " + top["protects_against"] + "."
    )

    return {
        "answer": answer,
        "matches": hits,
        "note": SAFETY_NOTE,
    }


@app.post("/chat")
def chat(body: ChatRequest):
    if body.version not in ("v1", "v2"):
        raise HTTPException(
            status_code=400,
            detail="version must be v1 or v2"
        )

    try:
        result = chat_answer(engine, body.question, body.version)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    result["note"] = SAFETY_NOTE
    return result


@app.get("/search/semantic")
def semantic(q: str, k: int = 3):
    try:
        from app.vectorstore import semantic_search
        results = semantic_search(q, k)
    except (RuntimeError, OSError, ChromaError) as e:
        raise HTTPException(
            status_code=503,
            detail="Semantic search is not ready: " + str(e)[:150]
        )

    return {"query": q, "results": results}


@app.post("/ask")
def ask_rag(body: AskRequest):
    try:
        from app.rag import answer_question
        result = answer_question(body.question, body.k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)[:200])
    except (OSError, ChromaError, ValueError) as e:
        raise HTTPException(
            status_code=503,
            detail="RAG is not ready: " + str(e)[:150]
        )

    result["note"] = SAFETY_NOTE
    return result


@app.post("/agent")
def ask_agent(body: AgentRequest):
    thread_id = body.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        if body.thread_id is None:
            # First request: select a tool and pause for approval.
            result = agent_graph.invoke(
                {
                    "question": body.question,
                    "decision": None,
                    "result": None,
                    "approved": False,
                },
                config=config,
            )
        else:
            # Second request: resume after the approval decision.
            if body.approved is None:
                raise HTTPException(
                    status_code=400,
                    detail="Please provide approved as true or false."
                )

            result = agent_graph.invoke(
                Command(resume=body.approved),
                config=config,
            )

        # The graph is waiting for user approval.
        if "__interrupt__" in result:
            return {
                "thread_id": thread_id,
                "status": "approval_required",
                "approval": result["__interrupt__"][0].value,
                "note": SAFETY_NOTE,
            }

        # The user rejected tool execution.
        if not result.get("approved"):
            return {
                "thread_id": thread_id,
                "status": "rejected",
                "result": None,
                "note": SAFETY_NOTE,
            }

        # The approved tool has executed.
        return {
            "thread_id": thread_id,
            "status": "completed",
            "result": result.get("result"),
            "note": SAFETY_NOTE,
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (RuntimeError, TypeError, OSError, ChromaError):
        raise HTTPException(
            status_code=503,
            detail="The agent service is temporarily unavailable."
        )
