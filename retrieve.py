"""
retrieve.py — retrieval + grounded generation with citations.

1. Embed the question with the same model used for the chunks.
2. Pull the top-k most similar chunks from ChromaDB.
3. Ask the local LLM (Ollama) to answer ONLY from those chunks, citing [n].
4. Append a Sources list built from the retrieved chunks (always accurate).
"""

import sys

import ollama

import config
from embed import get_model, get_collection

SYSTEM_PROMPT = (
    "You are PaperMind, a research assistant for papers on LLM reasoning, "
    "tool use, and agents. Answer ONLY using the numbered context passages "
    "provided. If the passages do not contain the answer, say you don't have "
    "enough information in the corpus. Do not make anything up. Cite sources "
    "inline with their number in square brackets, like [1] or [2][3]. "
    "Be concise and clear."
)


def retrieve_chunks(query: str, top_k: int = config.TOP_K_RESULTS):
    """Return a list of (text, metadata, distance) for the best-matching chunks."""
    model = get_model()
    col = get_collection()
    if col.count() == 0:
        return []
    qv = model.encode([query]).tolist()
    res = col.query(query_embeddings=qv, n_results=top_k)
    return list(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]))


def build_context(retrieved):
    """Number each distinct paper; label every chunk with its paper number."""
    paper_nums, sources, blocks = {}, [], []
    for text, meta, _ in retrieved:
        title = meta["title"]
        if title not in paper_nums:
            paper_nums[title] = len(paper_nums) + 1
            sources.append({"n": paper_nums[title], "title": title, "url": meta["url"]})
        blocks.append(f"[{paper_nums[title]}] {title}\n{text}")
    return "\n\n---\n\n".join(blocks), sources


def answer_question(query: str, top_k: int = config.TOP_K_RESULTS) -> dict:
    """Returns {"answer": str, "sources": [{"n", "title", "url"}, ...]}."""
    retrieved = retrieve_chunks(query, top_k)
    if not retrieved:
        return {
            "answer": "The corpus is empty. Run ingest.py, chunk.py and embed.py first.",
            "sources": [],
        }

    context, sources = build_context(retrieved)
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        resp = client.chat(
            model=config.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context passages:\n\n{context}\n\nQuestion: {query}",
                },
            ],
            options={"num_ctx": config.OLLAMA_NUM_CTX, "temperature": 0.2},
        )
        answer = resp["message"]["content"].strip()
    except Exception as e:
        return {
            "answer": f"Could not reach Ollama ({e}). Open the Ollama app, or run `ollama serve`, then try again.",
            "sources": sources,
        }
    return {"answer": answer, "sources": sources}


def format_sources(sources) -> str:
    return "\n".join(f"[{s['n']}] {s['title']} - {s['url']}" for s in sources)


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or input("Ask PaperMind a question: ")
    out = answer_question(q)
    print("\n" + out["answer"])
    if out["sources"]:
        print("\nSources:\n" + format_sources(out["sources"]))
