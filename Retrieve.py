"""
retrieve.py — Milestone 3: retrieval + grounded generation with citations.

Given a user question:
1. Embed the query with the same model used for chunks.
2. Pull the top-k most similar chunks from ChromaDB.
3. Feed those chunks to the LLM (Ollama) as context, with a prompt that
   forces it to cite which paper each part of the answer came from.
"""

import ollama

from config import OLLAMA_MODEL
from embed import get_model, get_collection

SYSTEM_PROMPT = """You are PaperMind, a research assistant for LLM reasoning and \
agentic systems papers. Answer ONLY using the provided context chunks. \
If the context doesn't contain the answer, say so — don't make things up. \
After each claim, cite the source using the paper title in brackets, e.g. [Title]."""


def retrieve_chunks(query: str, top_k: int = 5):
    """Embed the query and pull the top_k most relevant chunks from ChromaDB."""
    model = get_model()
    collection = get_collection()

    query_vector = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_vector, n_results=top_k)

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    return list(zip(chunks, metadatas))


def build_context(retrieved: list) -> str:
    """Format retrieved chunks into a context block, tagged by source title."""
    blocks = []
    for text, meta in retrieved:
        blocks.append(f"[Source: {meta['title']}]\n{text}")
    return "\n\n---\n\n".join(blocks)


def answer_question(query: str, top_k: int = 5) -> str:
    retrieved = retrieve_chunks(query, top_k)
    if not retrieved:
        return "No relevant papers found in the corpus yet. Try ingesting more papers first."

    context = build_context(retrieved)

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return response["message"]["content"]


if __name__ == "__main__":
    q = input("Ask PaperMind a question: ")
    print("\n" + answer_question(q))
