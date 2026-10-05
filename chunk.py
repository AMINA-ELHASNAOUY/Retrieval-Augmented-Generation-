"""
chunk.py — extract text from PDFs and split into overlapping word chunks.
Writes data/chunks.json (metadata.json is left untouched).
"""

import json
import re

import pymupdf

import config


def extract_text(pdf_path: str) -> str:
    with pymupdf.open(pdf_path) as doc:
        text = "\n".join(page.get_text() for page in doc)
    # Drop the bibliography: cut at the last "References" heading
    matches = list(re.finditer(r"\n\s*(references|bibliography)\s*\n", text, re.I))
    if matches and matches[-1].start() > len(text) * 0.5:
        text = text[: matches[-1].start()]
    text = re.sub(r"-\n(\w)", r"\1", text)  # fix hyphenated line breaks
    return text


def split_into_chunks(text: str, size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = start + size
        chunk = " ".join(words[start:end])
        if len(chunk.split()) >= 30:  # skip tiny tail fragments
            chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def chunk_all_papers():
    papers = json.loads(config.METADATA_PATH.read_text())
    out = []
    for p in papers:
        chunks = split_into_chunks(extract_text(p["pdf_path"]))
        print(f"{p['arxiv_id']}: {len(chunks)} chunks - {p['title'][:55]}")
        for i, c in enumerate(chunks):
            out.append({
                "id": f"{p['arxiv_id']}_{i}",
                "arxiv_id": p["arxiv_id"],
                "title": p["title"],
                "url": p["pdf_url"],
                "chunk_index": i,
                "text": c,
            })
    (config.DATA_DIR / "chunks.json").write_text(json.dumps(out))
    print(f"\nDone. {len(out)} chunks -> data/chunks.json")


if __name__ == "__main__":
    chunk_all_papers()
