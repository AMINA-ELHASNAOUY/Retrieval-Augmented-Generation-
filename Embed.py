"""
embed.py — Milestone 2: local embeddings + ChromaDB storage.

Embeds every chunk with sentence-transformers (all-MiniLM-L6-v2, runs locally,
no API cost) and stores vectors + metadata in a persistent ChromaDB collection.
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

from config import METADATA_PATH, CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL

_model = None


def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_all_papers():
    """Read chunked metadata.json, embed every chunk, upsert into ChromaDB."""
    metadata = json.loads(METADATA_PATH.read_text())
    model = get_model()
    collection = get_collection()

    for paper in metadata:
        chunks = paper.get("chunks", [])
        if not chunks:
            print(f"Skipping (no chunks): {paper['title'][:60]}")
            continue

        print(f"Embedding {len(chunks)} chunks for: {paper['title'][:60]}...")
        vectors = model.encode(chunks).tolist()

        ids = [f"{paper['arxiv_id']}_chunk{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "arxiv_id": paper["arxiv_id"],
                "title": paper["title"],
                "url": paper["url"],
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        collection.upsert(
            ids=ids,
            embeddings=vectors,
            documents=chunks,
            metadatas=metadatas,
        )

    print(f"\nDone. Vector store persisted at {CHROMA_DB_PATH}")


if __name__ == "__main__":
    embed_all_papers()
