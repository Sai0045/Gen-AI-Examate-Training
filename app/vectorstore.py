
import os
from itertools import islice

import chromadb
from chromadb.errors import NotFoundError

from app.chunking import iter_chunks
from app.embed import embed_texts

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_FOLDER, "data", "chroma")
COLLECTION_NAME = "teekatimer"


def get_client():
    return chromadb.PersistentClient(path=DB_FOLDER)


def get_collection():
    return get_client().get_or_create_collection(name=COLLECTION_NAME)


def reset_collection():
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except NotFoundError:
        pass
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_chunks(chunks, batch_size=8):
    collection = get_collection()
    total = 0
    chunks = iter(chunks)

    while True:
        batch = list(islice(chunks, batch_size))
        if not batch:
            break

        existing = set(
            collection.get(ids=[c["id"] for c in batch])["ids"]
        )

        batch = [c for c in batch if c["id"] not in existing]

        if not batch:
            continue

        texts = [c["text"] for c in batch]

        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=texts,
            embeddings=embed_texts(texts),
            metadatas=[
                {
                    "source": c["source"],
                    "page": c["page"],
                    "title": c["title"],
                    "chunk_no": c["chunk_no"],
                }
                for c in batch
            ],
        )

        total += len(batch)
        print("Indexed", total, "new chunks")

    return collection.count()


def semantic_search(query, k=3):
    collection = get_collection()

    if collection.count() == 0:
        raise RuntimeError(
            "The collection is empty. Run: python -m app.vectorstore"
        )

    found = collection.query(
        query_embeddings=embed_texts([query]),
        n_results=k,
    )

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
    print("Starting memory-efficient indexing...")
    count = index_chunks(iter_chunks())
    print("Done. The collection now holds", count, "chunks")


if __name__ == "__main__":

    main()
