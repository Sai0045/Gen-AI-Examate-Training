import json
import os

from app.llm import ask_llm

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FOLDER = os.path.join(BASE_FOLDER, "prompts")


def read_prompt(name):
    with open(os.path.join(PROMPT_FOLDER, name), encoding="utf-8-sig") as f:
        return f.read()


def format_records(hits):
    lines = []
    for r in hits:
        lines.append("- " + r["vaccine"] + " | due: " + r["due_age"]
                     + " | latest age: " + r["latest_age"] + " | dose: " + r["dose"]
                     + " | route and site: " + r["route_site"]
                     + " | protects against: " + r["protects_against"])
    return "\n".join(lines)


def parse_json(text):
    # the model should send only JSON, but sometimes adds extra words around it
    try:
        return json.loads(text)
    except ValueError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except ValueError:
            pass
    return None


def chat_answer(engine, question, version="v2"):
    hits = engine.search(question, top_k=5)
    sources = [h["vaccine"] for h in hits]

    # nothing found at all, so do not even ask the LLM
    if len(hits) == 0:
        return {
            "answer": "I don't know. This is not in the MoHFW immunization schedule I have.",
            "confidence": "low",
            "follow_up": "Please ask your ANM, anganwadi worker or doctor.",
            "sources": [],
        }

    system_prompt = read_prompt("system.txt")
    task = read_prompt("task_" + version + ".txt")
    task = task.replace("<<RECORDS>>", format_records(hits))
    task = task.replace("<<QUESTION>>", question)

    text = ask_llm(system_prompt, task)
    data = parse_json(text)
    if data is None:
        data = {"answer": text.strip(), "confidence": "low", "follow_up": ""}

    confidence = str(data.get("confidence", "low")).lower()
    if confidence not in ("high", "medium", "low"):
        confidence = "low"

    return {
        "answer": str(data.get("answer", "")),
        "confidence": confidence,
        "follow_up": str(data.get("follow_up", "")),
        "sources": sources,
    }
