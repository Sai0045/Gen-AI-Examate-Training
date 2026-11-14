import os
from html.parser import HTMLParser

import pdfplumber

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FOLDER = os.path.join(BASE_FOLDER, "data", "raw")

CHUNK_SIZE = 150  # words in one chunk
OVERLAP = 30      # words shared with the previous chunk


class TextGrabber(HTMLParser):
    # collects the visible text and the title of an html page
    def __init__(self):
        super().__init__()
        self.parts = []
        self.title = ""
        self.skip = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip = self.skip + 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip > 0:
            self.skip = self.skip - 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = self.title + data
        elif self.skip == 0:
            self.parts.append(data)


def read_pdf(path):
    name = os.path.basename(path)
    pages = []
    with pdfplumber.open(path) as pdf:
        title = str((pdf.metadata or {}).get("Title", "") or "").strip()
        if title == "":
            title = os.path.splitext(name)[0].replace("_", " ")
        number = 1
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip() != "":
                pages.append({"source": name, "page": number, "title": title, "text": text})
            number = number + 1
    return pages


def read_html(path):
    name = os.path.basename(path)
    with open(path, encoding="utf-8", errors="ignore") as f:
        grabber = TextGrabber()
        grabber.feed(f.read())
    title = grabber.title.strip()
    if title == "":
        title = os.path.splitext(name)[0].replace("_", " ")
    text = " ".join(" ".join(grabber.parts).split())
    return [{"source": name, "page": 1, "title": title, "text": text}]


def read_documents():
    pages = []
    if not os.path.exists(RAW_FOLDER):
        return pages
    for name in sorted(os.listdir(RAW_FOLDER)):
        path = os.path.join(RAW_FOLDER, name)
        try:
            if name.lower().endswith(".pdf"):
                pages.extend(read_pdf(path))
            elif name.lower().endswith((".html", ".htm")):
                pages.extend(read_html(path))
        except Exception as e:
            print("Could not read", name, "-", str(e)[:100])
    return pages


def split_words(text, size, overlap):
    words = text.split()
    pieces = []
    start = 0
    while start < len(words):
        pieces.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
        start = start + size - overlap
    return pieces


def make_chunks(chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    for page in read_documents():
        number = 1
        for piece in split_words(page["text"], chunk_size, overlap):
            # skip tiny pieces such as page numbers
            if len(piece.split()) < 15:
                continue
            chunks.append({
                "id": page["source"] + "-p" + str(page["page"]) + "-c" + str(number),
                "text": piece,
                "source": page["source"],
                "page": page["page"],
                "title": page["title"],
                "chunk_no": number,
            })
            number = number + 1
    return chunks


def main():
    chunks = make_chunks()
    per_source = {}
    for c in chunks:
        per_source[c["source"]] = per_source.get(c["source"], 0) + 1

    print("Total chunks:", len(chunks))
    for source, count in per_source.items():
        print("  ", source, "->", count, "chunks")
    if len(chunks) > 0:
        first = chunks[0]
        print("Example:", first["id"], "| title:", first["title"])
        print(first["text"][:150])


if __name__ == "__main__":
    main()