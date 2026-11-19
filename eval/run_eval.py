
import json
import os
import time

from chromadb.errors import ChromaError

from app.rag import answer_question

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Both configurations use the same ChromaDB index.
# Only the number of retrieved chunks (top-k) changes.
CONFIGS = [
    {"name": "A", "k": 3},
    {"name": "B", "k": 6},
]


def is_dont_know(answer):
    return "i don't know" in answer.lower()


def normalize_text(text):
    """Convert different Unicode hyphens into a normal hyphen."""
    text = str(text).lower()

    for symbol in ["‑", "–", "—", "−"]:
        text = text.replace(symbol, "-")

    return text


def has_all(answer, keywords):
    """Check that at least one alternative from every keyword group exists."""
    text = normalize_text(answer)

    for key in keywords:
        found = False

        # Alternatives are separated by |
        for option in key.split("|"):
            option = normalize_text(option.strip())

            if option in text:
                found = True
                break

        if not found:
            return False

    return True


def short(text):
    """Make answers shorter so they fit in the Markdown report."""
    return " ".join(str(text).split()).replace("|", "/")[:200]


def run_config(config, rows):
    results = []

    for row in rows:
        status = "ERROR"
        answer = ""
        cited = 0

        try:
            result = answer_question(row["question"], config["k"])

            answer = result["answer"]
            cited = len(result["citations"])

            if row["answerable"]:
                if not is_dont_know(answer) and has_all(answer, row["keywords"]):
                    status = "PASS"
                else:
                    status = "FAIL"

            else:
                if is_dont_know(answer):
                    status = "PASS"
                else:
                    status = "FAIL"

        except (RuntimeError, OSError, ValueError, ChromaError) as e:
            answer = "ERROR: " + str(e)[:150]
            status = "ERROR"

        results.append({
            "id": row["id"],
            "answerable": row["answerable"],
            "answer": answer,
            "cited": cited,
            "status": status
        })

        print(
            "Config", config["name"],
            "Question", row["id"],
            "->", status
        )

        # Pause between API requests to reduce rate-limit pressure.
        time.sleep(5)

    return results


def main():
    dataset_path = os.path.join(
        BASE_FOLDER, "eval", "eval_set.json"
    )

    with open(dataset_path, encoding="utf-8") as f:
        rows = json.load(f)

    summary = []
    details = []

    # Run both top-k configurations.
    for config in CONFIGS:
        print("\nStarting configuration", config["name"])

        results = run_config(config, rows)

        good = sum(
            1 for r in results
            if r["answerable"] and r["status"] == "PASS"
        )

        total_good = sum(
            1 for r in results if r["answerable"]
        )

        refused = sum(
            1 for r in results
            if not r["answerable"] and r["status"] == "PASS"
        )

        total_refuse = sum(
            1 for r in results if not r["answerable"]
        )

        errors = sum(
            1 for r in results if r["status"] == "ERROR"
        )

        passed = sum(
            1 for r in results if r["status"] == "PASS"
        )

        cited = sum(
            1 for r in results
            if r["answerable"]
            and r["status"] == "PASS"
            and r["cited"] > 0
        )

        summary.append({
            "config": config,
            "good": good,
            "total_good": total_good,
            "refused": refused,
            "total_refuse": total_refuse,
            "passed": passed,
            "errors": errors,
            "cited": cited
        })

        details.append((config, results))

    # Do not declare a winner if either configuration has errors.
    comparison_valid = all(
        item["errors"] == 0 for item in summary
    )

    # Prepare the Markdown report.
    lines = [
        "# RAG Evaluation Report",
        "",
        "Dataset: 15 questions (12 answerable and 3 unanswerable).",
        "",
        "PASS: Expected keywords are present, or an unanswerable question is correctly refused.",
        "FAIL: The model returned an answer that did not meet the evaluation criteria.",
        "ERROR: The API or evaluation request failed. Errors are not counted as failures.",
        "",
        "Note: This is a simple keyword-based evaluation. Answers should also be reviewed for factual accuracy.",
        "",
        "## Summary",
        "",
        "| Config | Top-k | Answerable passed | Refusals passed | Total passed | Errors | Passed with citation |",
        "|---|---:|---:|---:|---:|---:|---:|"
    ]

    for item in summary:
        config = item["config"]

        lines.append(
            "| " + config["name"]
            + " | " + str(config["k"])
            + " | " + str(item["good"]) + "/" + str(item["total_good"])
            + " | " + str(item["refused"]) + "/" + str(item["total_refuse"])
            + " | " + str(item["passed"]) + "/15"
            + " | " + str(item["errors"])
            + " | " + str(item["cited"])
            + " |"
        )

    lines.append("")

    if comparison_valid:
        best = max(summary, key=lambda item: item["passed"])

        if summary[0]["passed"] == summary[1]["passed"]:
            lines.append("Result: Both configurations have the same total score.")
        else:
            lines.append(
                "Best configuration by total passed: Config "
                + best["config"]["name"]
            )
    else:
        lines.append(
            "Comparison inconclusive: At least one configuration "
            "contains API or execution errors. Rerun after resolving them."
        )

    lines.append("")

    # Add individual question results.
    for config, results in details:
        lines.append(
            "## Config " + config["name"]
            + " details (top-k " + str(config["k"]) + ")"
        )

        lines.append("")
        lines.append("| # | Result | Answer | Citations |")
        lines.append("|---:|---|---|---:|")

        for result in results:
            lines.append(
                "| " + str(result["id"])
                + " | " + result["status"]
                + " | " + short(result["answer"])
                + " | " + str(result["cited"])
                + " |"
            )

        lines.append("")

    # Save the report.
    report_path = os.path.join(
        BASE_FOLDER, "eval", "eval_results.md"
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\nSaved eval/eval_results.md")

    if comparison_valid:
        print("Both configurations completed without errors.")
    else:
        print("Evaluation comparison is inconclusive due to errors.")


if __name__ == "__main__":
    main()
