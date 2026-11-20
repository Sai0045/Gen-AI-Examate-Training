import os
from html.parser import HTMLParser

import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FOLDER = os.path.join(BASE_FOLDER, "data", "raw")

CHUNK_SIZE = 150
OVERLAP = 30


class TextGrabber(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.title = ""
        self.skip = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip > 0:
            self.skip -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.skip == 0:
            self.parts.append(data)


def iter_pdf_pages(path):
    name = os.path.basename(path)
    with pdfplumber.open(path) as pdf:
        title = str((pdf.metadata or {}).get("Title", "") or "").strip()
        if not title:
            title = os.path.splitext(name)[0].replace("_", " ")

        for number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                yield {
                    "source": name,
                    "page": number,
                    "title": title,
                    "text": text,
                }


def read_pdf(path):
    return list(iter_pdf_pages(path))


def read_html(path):
    name = os.path.basename(path)
    with open(path, encoding="utf-8", errors="ignore") as f:
        grabber = TextGrabber()
        grabber.feed(f.read())

    title = grabber.title.strip()
    if not title:
        title = os.path.splitext(name)[0].replace("_", " ")

    text = " ".join(" ".join(grabber.parts).split())
    return [{
        "source": name,
        "page": 1,
        "title": title,
        "text": text,
    }]


def iter_documents():
    if not os.path.exists(RAW_FOLDER):
        return

    for name in sorted(os.listdir(RAW_FOLDER)):
        path = os.path.join(RAW_FOLDER, name)
        try:
            if name.lower().endswith(".pdf"):
                yield from iter_pdf_pages(path)
            elif name.lower().endswith((".html", ".htm")):
                yield from read_html(path)
        except (OSError, PDFSyntaxError) as error:
            print("Could not read", name, "-", str(error)[:100])


def read_documents():
    return list(iter_documents())


def iter_chunks(chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    for page in iter_documents():
        words = page["text"].split()
        number = 1
        start = 0

        while start < len(words):
            piece = " ".join(words[start:start + chunk_size])

            if len(piece.split()) >= 15:
                yield {
                    "id": (
                        page["source"]
                        + "-p" + str(page["page"])
                        + "-c" + str(number)
                    ),
                    "text": piece,
                    "source": page["source"],
                    "page": page["page"],
                    "title": page["title"],
                    "chunk_no": number,
                }
                number += 1

            if start + chunk_size >= len(words):
                break

            start += chunk_size - overlap


def make_chunks(chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    return list(iter_chunks(chunk_size, overlap))


def main():
    total = 0
    per_source = {}

    for chunk in iter_chunks():
        total += 1
        source = chunk["source"]
        per_source[source] = per_source.get(source, 0) + 1

    print("Total chunks:", total)
    for source, count in per_source.items():
        print("  ", source, "->", count, "chunks")


if __name__ == "__main__":
    main()
