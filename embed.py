"""
embed.py — embed chunks with sentence-transformers and store in ChromaDB.
"""

import json

import chromadb
from sentence_transformers import SentenceTransformer

import config

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBED_MODEL_NAME)
    return _model


def get_collection(reset: bool = False):
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    if reset:
        try:
            client.delete_collection(config.CHROMA_COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def embed_all_chunks():
    chunks = json.loads((config.DATA_DIR / "chunks.json").read_text())
    model = get_model()
    col = get_collection(reset=True)

    batch = 64
    for i in range(0, len(chunks), batch):
        part = chunks[i : i + batch]
        vecs = model.encode([c["text"] for c in part]).tolist()
        col.add(
            ids=[c["id"] for c in part],
            embeddings=vecs,
            documents=[c["text"] for c in part],
            metadatas=[
                {"arxiv_id": c["arxiv_id"], "title": c["title"], "url": c["url"], "chunk_index": c["chunk_index"]}
                for c in part
            ],
        )
        print(f"embedded {min(i + batch, len(chunks))}/{len(chunks)}")
    print(f"\nDone. {col.count()} chunks stored in {config.CHROMA_DIR}")


if __name__ == "__main__":
    embed_all_chunks()
