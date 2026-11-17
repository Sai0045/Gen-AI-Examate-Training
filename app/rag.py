from app.chat import parse_json, read_prompt
from app.llm import ask_llm
from app.vectorstore import semantic_search

DONT_KNOW = "I don't know. This is not in the MoHFW documents I have."


def format_passages(hits):
    lines = []
    number = 1
    for h in hits:
        text = " ".join(h["text"].split())
        lines.append("[" + str(number) + "] (" + h["source"] + ", page " + str(h["page"]) + ") " + text)
        number = number + 1
    return "\n\n".join(lines)


def dont_know(retrieved):
    return {"answer": DONT_KNOW, "answerable": False, "citations": [], "retrieved": retrieved}


def answer_question(question, k=3):
    hits = semantic_search(question, k)
    if len(hits) == 0:
        return dont_know(0)

    system_prompt = read_prompt("rag_system.txt")
    task = read_prompt("rag_task.txt")
    task = task.replace("<<PASSAGES>>", format_passages(hits))
    task = task.replace("<<QUESTION>>", question)

    text = ask_llm(system_prompt, task)
    data = parse_json(text)
    if data is None:
        return dont_know(len(hits))

    # the model says the passages do not answer the question
    if str(data.get("answerable")).lower() != "true":
        return dont_know(len(hits))

    # turn the passage numbers into real citations
    citations = []
    used = []
    for n in data.get("citations", []):
        try:
            index = int(n) - 1
        except (TypeError, ValueError):
            continue
        if 0 <= index < len(hits) and index not in used:
            used.append(index)
            hit = hits[index]
            citations.append({"source": hit["source"], "page": hit["page"],
                              "title": hit["title"], "distance": hit["distance"]})

    answer = str(data.get("answer", "")).strip()
    # an answer without a citation cannot be checked, so it is not allowed
    if answer == "" or len(citations) == 0:
        return dont_know(len(hits))

    return {"answer": answer, "answerable": True, "citations": citations, "retrieved": len(hits)}