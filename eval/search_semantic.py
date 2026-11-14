import os

from app.vectorstore import semantic_search

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_questions():
    questions = []
    with open(os.path.join(BASE_FOLDER, "eval", "questions.md"), encoding="utf-8-sig") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5 and parts[1].isdigit():
                questions.append(parts[2])
    return questions


def one_line(text):
    return " ".join(str(text).split())


def main():
    lines = ["# Semantic search results", "",
             "Top 3 chunks from the Chroma collection for each test question. A lower distance means a closer match.", ""]
    number = 1
    for q in read_questions():
        lines.append("## Q" + str(number) + ": " + q)
        for hit in semantic_search(q, 3):
            lines.append("- " + hit["source"] + ", page " + str(hit["page"])
                         + " (distance " + str(hit["distance"]) + "): "
                         + one_line(hit["text"])[:200])
        lines.append("")
        print("done question", number)
        number = number + 1

    with open(os.path.join(BASE_FOLDER, "eval", "search_results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Saved eval/search_results.md")


if __name__ == "__main__":
    main()