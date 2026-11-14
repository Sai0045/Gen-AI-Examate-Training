import os

import chromadb

from app.chunking import make_chunks
from app.embed import embed_texts

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_FOLDER, "data", "chroma")
COLLECTION_NAME = "teekatimer"


def get_client():
    return chromadb.PersistentClient(path=DB_FOLDER)


def get_collection():
    return get_client().get_or_create_collection(name=COLLECTION_NAME)


def reset_collection():
    # start from an empty collection so it always matches the current chunking
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_chunks(chunks, batch_size=64):
    collection = reset_collection()
    total = len(chunks)
    for start in range(0, total, batch_size):
        batch = chunks[start:start + batch_size]
        texts = [c["text"] for c in batch]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=texts,
            embeddings=embed_texts(texts),
            metadatas=[{"source": c["source"], "page": c["page"],
                        "title": c["title"], "chunk_no": c["chunk_no"]} for c in batch],
        )
        print("indexed", min(start + batch_size, total), "of", total)
    return collection.count()


def semantic_search(query, k=3):
    collection = get_collection()
    if collection.count() == 0:
        raise RuntimeError("The collection is empty. Run: python -m app.vectorstore")

    found = collection.query(query_embeddings=embed_texts([query]), n_results=k)
    results = []
    for i in range(len(found["ids"][0])):
        meta = found["metadatas"][0][i]
        results.append({
            "text": found["documents"][0][i],
            "source": meta["source"],
            "page": meta["page"],
            "title": meta["title"],
            "distance": round(float(found["distances"][0][i]), 3),
        })
    return results


def main():
    chunks = make_chunks()
    if len(chunks) == 0:
        print("No chunks found. Put PDFs in data/raw first.")
        return
    print("Indexing", len(chunks), "chunks, this can take a few minutes")
    count = index_chunks(chunks)
    print("Done. The collection now holds", count, "chunks")


if __name__ == "__main__":
    main()