"""
ingest.py — Milestone 1: arXiv ingestion pipeline.

Searches arXiv for papers matching a query/category, downloads the PDFs,
and stores lightweight metadata (title, authors, abstract, arxiv_id, pdf_path)
so later stages (chunking, embedding) know what they're working with.
"""

import json
import arxiv

from config import ARXIV_MAX_RESULTS, ARXIV_CATEGORY, PDF_DIR, METADATA_PATH


def search_papers(query: str, max_results: int = ARXIV_MAX_RESULTS):
    """Search arXiv and return a list of arxiv.Result objects."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    return list(search.results())


def download_paper(result: arxiv.Result) -> str:
    """Download a single paper's PDF into PDF_DIR. Returns the local file path."""
    safe_id = result.get_short_id().replace("/", "_")
    filename = f"{safe_id}.pdf"
    filepath = PDF_DIR / filename

    if not filepath.exists():
        result.download_pdf(dirpath=str(PDF_DIR), filename=filename)

    return str(filepath)


def build_metadata(result: arxiv.Result, pdf_path: str) -> dict:
    return {
        "arxiv_id": result.get_short_id(),
        "title": result.title.strip(),
        "authors": [a.name for a in result.authors],
        "abstract": result.summary.strip(),
        "published": result.published.isoformat(),
        "pdf_path": pdf_path,
        "url": result.entry_id,
    }


def ingest(query: str = "LLM reasoning agentic systems", max_results: int = ARXIV_MAX_RESULTS):
    """Full ingestion run: search -> download -> save metadata.json"""
    print(f"Searching arXiv for: '{query}' (category filter: {ARXIV_CATEGORY})")
    results = search_papers(query, max_results)
    print(f"Found {len(results)} papers.")

    all_metadata = []
    for i, result in enumerate(results, 1):
        print(f"[{i}/{len(results)}] Downloading: {result.title[:60]}...")
        pdf_path = download_paper(result)
        all_metadata.append(build_metadata(result, pdf_path))

    METADATA_PATH.write_text(json.dumps(all_metadata, indent=2))
    print(f"\nDone. Saved metadata for {len(all_metadata)} papers to {METADATA_PATH}")
    return all_metadata


if __name__ == "__main__":
    ingest()
