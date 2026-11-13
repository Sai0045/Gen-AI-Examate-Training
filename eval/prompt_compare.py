import os
import time

from app.chat import chat_answer
from app.records import load_records
from app.smart_search import SmartSearch

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_questions():
    questions = []
    with open(os.path.join(BASE_FOLDER, "eval", "questions.md"), encoding="utf-8-sig") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            # a table row looks like: '', '1', 'question', 'expected answer', ''
            if len(parts) >= 5 and parts[1].isdigit():
                questions.append(parts[2])
    # extra question: the search finds BCG, but the answer is not in the records
    questions.append("Can I give the BCG vaccine to my baby who has a fever?")
    return questions


def one_line(text):
    return str(text).replace("\n", " ").replace("|", "/")


def run(engine, question, version):
    try:
        result = chat_answer(engine, question, version)
        return one_line(result["answer"]) + " (" + result["confidence"] + ")"
    except RuntimeError as e:
        return "ERROR: " + one_line(e)


def main():
    engine = SmartSearch(load_records())
    questions = read_questions()
    print("Found", len(questions), "questions")

    rows = []
    number = 1
    for q in questions:
        v1 = run(engine, q, "v1")
        time.sleep(2)
        v2 = run(engine, q, "v2")
        time.sleep(2)
        rows.append("| " + str(number) + " | " + one_line(q) + " | " + v1 + " | " + v2 + " |")
        print("done question", number)
        number = number + 1

    lines = [
        "# Prompt comparison: v1 and v2",
        "",
        "v1 is a short prompt. v2 adds step-by-step rules, a fixed I don't know sentence and a rule for confidence.",
        "",
        "| # | Question | v1 answer (confidence) | v2 answer (confidence) |",
        "|---|----------|------------------------|------------------------|",
    ]
    lines.extend(rows)

    with open(os.path.join(BASE_FOLDER, "eval", "prompt_compare.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Saved eval/prompt_compare.md")


if __name__ == "__main__":
    main()
