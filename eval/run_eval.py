import json
import os
import time

from app.rag import answer_question

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# both configurations use the same index (150 word chunks), only the top-k differs
CONFIGS = [
    {"name": "A", "k": 3},
    {"name": "B", "k": 6},
]


def is_dont_know(answer):
    return "i don't know" in answer.lower()


def has_all(answer, keywords):
    text = answer.lower()
    for key in keywords:
        found = False
        for option in key.lower().split("|"):
            if option in text:
                found = True
        if not found:
            return False
    return True


def short(text):
    return " ".join(str(text).split()).replace("|", "/")[:150]


def run_config(config, rows):
    results = []
    for row in rows:
        error = False
        try:
            result = answer_question(row["question"], config["k"])
            answer = result["answer"]
            cited = len(result["citations"])
        except Exception as e:
            answer = "ERROR: " + str(e)[:100]
            cited = 0
            error = True

        if error:
            passed = False
        elif row["answerable"]:
            passed = (not is_dont_know(answer)) and has_all(answer, row["keywords"])
        else:
            passed = is_dont_know(answer)

        results.append({"id": row["id"], "answerable": row["answerable"],
                        "answer": answer, "cited": cited, "passed": passed})
        print("config", config["name"], "question", row["id"], "->", "PASS" if passed else "FAIL")
        time.sleep(2)
    return results


def main():
    with open(os.path.join(BASE_FOLDER, "eval", "eval_set.json"), encoding="utf-8") as f:
        rows = json.load(f)

    summary = []
    details = []
    for config in CONFIGS:
        results = run_config(config, rows)
        good = sum(1 for r in results if r["answerable"] and r["passed"])
        total_good = sum(1 for r in results if r["answerable"])
        refused = sum(1 for r in results if (not r["answerable"]) and r["passed"])
        total_refuse = sum(1 for r in results if not r["answerable"])
        cited = sum(1 for r in results if r["answerable"] and r["passed"] and r["cited"] > 0)
        summary.append({"config": config, "good": good, "total_good": total_good,
                        "refused": refused, "total_refuse": total_refuse,
                        "all": good + refused, "cited": cited})
        details.append((config, results))

    best = summary[0]
    for item in summary:
        if item["all"] > best["all"]:
            best = item

    lines = ["# RAG evaluation (15 questions, 2 configurations)", "",
             "A row passes when an answerable question gets an answer that contains the expected facts, "
             "or when an unanswerable question gets I don't know. The check is a simple keyword match, so read the answers too.", "",
             "## Summary", "",
             "| Config | Top-k | Answerable passed | Refusals passed | Total | Passed with citation |",
             "|---|---|---|---|---|---|"]
    for item in summary:
        c = item["config"]
        lines.append("| " + c["name"] + " | " + str(c["k"])
                     + " | " + str(item["good"]) + "/" + str(item["total_good"])
                     + " | " + str(item["refused"]) + "/" + str(item["total_refuse"])
                     + " | " + str(item["all"]) + "/15 | " + str(item["cited"]) + " |")
    lines.append("")
    lines.append("Best configuration by total score: " + best["config"]["name"])
    lines.append("")

    for config, results in details:
        lines.append("## Config " + config["name"] + " details (top-k " + str(config["k"]) + ")")
        lines.append("")
        lines.append("| # | Result | Answer |")
        lines.append("|---|---|---|")
        for r in results:
            lines.append("| " + str(r["id"]) + " | " + ("PASS" if r["passed"] else "FAIL") + " | " + short(r["answer"]) + " |")
        lines.append("")

    with open(os.path.join(BASE_FOLDER, "eval", "eval_results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Saved eval/eval_results.md")


if __name__ == "__main__":
    main()