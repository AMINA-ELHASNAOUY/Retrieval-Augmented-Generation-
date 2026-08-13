"""
chunk.py — Milestone 2: PDF parsing + chunking.

Extracts raw text from downloaded PDFs (PyMuPDF) and splits it into
overlapping chunks sized for embedding. Overlap keeps context from being
severed at chunk boundaries.
"""

import json
import fitz  # PyMuPDF

from config import METADATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP


def extract_text(pdf_path: str) -> str:
    """Pull all text out of a PDF, page by page."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """
    Word-based sliding window chunking.
    chunk_size and overlap are measured in words, not characters —
    simpler to reason about and good enough for MiniLM's token limits.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start = end - overlap  # step forward, but re-include the overlap window

    return chunks


def chunk_all_papers():
    """Read metadata.json, chunk every paper's PDF, attach chunks to each record."""
    metadata = json.loads(METADATA_PATH.read_text())

    for paper in metadata:
        print(f"Chunking: {paper['title'][:60]}...")
        text = extract_text(paper["pdf_path"])
        chunks = split_into_chunks(text)
        paper["chunks"] = chunks
        print(f"  -> {len(chunks)} chunks")

    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    print(f"\nDone. Chunks written back into {METADATA_PATH}")
    return metadata


if __name__ == "__main__":
    chunk_all_papers()
