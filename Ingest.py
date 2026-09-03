"""
ingest.py — Milestone 1: arXiv ingestion + PDF parsing.

Pipeline:
    1. Query the arXiv API for recent papers matching our topic query.
    2. Download each paper's PDF (skip ones we already have).
    3. Parse each PDF into raw text with PyMuPDF, keeping per-page text
       so downstream chunking can preserve rough page context.

Run directly to ingest a fresh batch:
    python ingest.py
"""

from __future__ import annotations

import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf as fitz  # PyMuPDF (import name is legacy but this avoids the deprecation warning)

import config

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    pdf_url: str
    published: str
    pdf_path: Path | None = None
    pages: list[str] = field(default_factory=list)  # raw text per page


def _build_query_url(query: str, max_results: int) -> str:
    params = (
        f"search_query=all:{urllib.parse.quote(query)}"
        f"&start=0&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )
    return f"{ARXIV_API_URL}?{params}"


import urllib.parse  # noqa: E402  (kept near usage for clarity)


def fetch_arxiv_metadata(
    query: str = config.ARXIV_SEARCH_QUERY,
    max_results: int = config.ARXIV_MAX_RESULTS,
) -> list[Paper]:
    """Query the arXiv API and return paper metadata (no PDFs yet)."""
    url = _build_query_url(query, max_results)
    with urllib.request.urlopen(url, timeout=30) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    papers: list[Paper] = []

    for entry in root.findall("atom:entry", ATOM_NS):
        arxiv_id = entry.find("atom:id", ATOM_NS).text.strip().split("/")[-1]
        title = entry.find("atom:title", ATOM_NS).text.strip().replace("\n", " ")
        abstract = entry.find("atom:summary", ATOM_NS).text.strip()
        published = entry.find("atom:published", ATOM_NS).text.strip()
        authors = [
            a.find("atom:name", ATOM_NS).text
            for a in entry.findall("atom:author", ATOM_NS)
        ]

        pdf_url = None
        for link in entry.findall("atom:link", ATOM_NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
                break
        if pdf_url is None:
            # fall back to the abs page -> pdf convention
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        papers.append(
            Paper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract,
                pdf_url=pdf_url,
                published=published,
            )
        )

    return papers


def download_pdf(paper: Paper, dest_dir: Path = config.RAW_PDF_DIR) -> Path:
    """Download a paper's PDF if we don't already have it."""
    safe_id = paper.arxiv_id.replace("/", "_")
    dest_path = dest_dir / f"{safe_id}.pdf"

    if dest_path.exists():
        paper.pdf_path = dest_path
        return dest_path

    req = urllib.request.Request(
        paper.pdf_url, headers={"User-Agent": "PaperMind/0.1 (research assistant)"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest_path.write_bytes(resp.read())

    paper.pdf_path = dest_path
    return dest_path


def parse_pdf(pdf_path: Path) -> list[str]:
    """Extract raw text per page from a PDF using PyMuPDF."""
    pages: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pages.append(page.get_text("text"))
    return pages


def ingest_batch(
    query: str = config.ARXIV_SEARCH_QUERY,
    max_results: int = config.ARXIV_MAX_RESULTS,
    delay_seconds: float = 3.0,
) -> list[Paper]:
    """Full Milestone 1 pipeline: fetch metadata, download, parse."""
    print(f"Querying arXiv for: {query!r} (max {max_results})")
    papers = fetch_arxiv_metadata(query, max_results)
    print(f"Found {len(papers)} papers.")

    for i, paper in enumerate(papers, 1):
        print(f"[{i}/{len(papers)}] {paper.arxiv_id} — {paper.title[:70]}")
        try:
            pdf_path = download_pdf(paper)
            paper.pages = parse_pdf(pdf_path)
            print(f"    parsed {len(paper.pages)} pages")
        except Exception as e:
            print(f"    FAILED: {e}")
        # arXiv asks for a few seconds between requests to be polite
        time.sleep(delay_seconds)

    return papers


if __name__ == "__main__":
    result = ingest_batch()
    ok = sum(1 for p in result if p.pages)
    print(f"\nDone. {ok}/{len(result)} papers ingested successfully.")
