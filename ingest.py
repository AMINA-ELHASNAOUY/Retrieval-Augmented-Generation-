"""
ingest.py — Milestone 1: arXiv ingestion + PDF download.

Fetches papers matching config.ARXIV_SEARCH_QUERY, downloads the PDFs, and
appends new papers to data/metadata.json (already-ingested papers are skipped).

Usage:
    python ingest.py                      # default query, default count
    python ingest.py --max 20             # grab up to 20 new papers
    python ingest.py --query 'all:"ReAct agent"' --max 5
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

import arxiv
import pymupdf

import config


@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    pdf_url: str
    published: str
    pdf_path: str | None = None
    num_pages: int = 0


def base_id(short_id: str) -> str:
    """'2401.12345v2' -> '2401.12345' so re-runs don't duplicate new versions."""
    return re.sub(r"v\d+$", "", short_id)


def load_metadata() -> list[dict]:
    if config.METADATA_PATH.exists():
        return json.loads(config.METADATA_PATH.read_text())
    return []


def save_metadata(records: list[dict]) -> None:
    config.METADATA_PATH.write_text(json.dumps(records, indent=2))


def fetch_arxiv_metadata(query: str, max_results: int) -> list[Paper]:
    client = arxiv.Client(page_size=min(max_results, 100), delay_seconds=5, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers: list[Paper] = []
    for r in client.results(search):
        papers.append(
            Paper(
                arxiv_id=base_id(r.get_short_id()),
                title=" ".join(r.title.split()),
                authors=[a.name for a in r.authors],
                abstract=" ".join(r.summary.split()),
                pdf_url=r.pdf_url,
                published=str(r.published.date()),
            )
        )
    return papers


def download_pdf(paper: Paper) -> Path:
    dest = config.RAW_PDF_DIR / f"{paper.arxiv_id.replace('/', '_')}.pdf"
    if not dest.exists():
        req = urllib.request.Request(
            paper.pdf_url, headers={"User-Agent": "PaperMind/0.1 (research assistant)"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        time.sleep(3)  # be polite to arXiv
    paper.pdf_path = str(dest)
    return dest


def ingest_batch(query: str, max_results: int) -> None:
    records = load_metadata()
    known = {r["arxiv_id"] for r in records}
    print(f"Already have {len(known)} papers.")
    print(f"Querying arXiv (max {max_results}): {query}")

    found = fetch_arxiv_metadata(query, max_results)
    new = [p for p in found if p.arxiv_id not in known]
    print(f"Found {len(found)} papers, {len(new)} are new.\n")

    ok = 0
    for i, paper in enumerate(new, 1):
        print(f"[{i}/{len(new)}] {paper.arxiv_id} - {paper.title[:70]}")
        try:
            pdf_path = download_pdf(paper)
            with pymupdf.open(pdf_path) as doc:
                paper.num_pages = len(doc)
            records.append(asdict(paper))
            save_metadata(records)  # save as we go
            ok += 1
            print(f"    OK ({paper.num_pages} pages)")
        except Exception as e:
            print(f"    FAILED: {e}")

    print(f"\nDone. {ok}/{len(new)} new papers added. Total in corpus: {len(records)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default=config.ARXIV_SEARCH_QUERY)
    ap.add_argument("--max", type=int, default=config.ARXIV_MAX_RESULTS)
    args = ap.parse_args()
    ingest_batch(args.query, args.max)
