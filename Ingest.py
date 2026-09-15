import arxiv
import fitz  # PyMuPDF
import json
import os
from config import ARXIV_QUERY, MAX_PAPERS, RAW_PDF_DIR, PARSED_DIR


def fetch_papers(query=ARXIV_QUERY, max_results=MAX_PAPERS):
    """Query arXiv and download PDFs."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    papers = []
    for result in client.results(search):
        paper_id = result.get_short_id()
        pdf_path = os.path.join(RAW_PDF_DIR, f"{paper_id}.pdf")

        if not os.path.exists(pdf_path):
            print(f"Downloading: {result.title}")
            result.download_pdf(dirpath=RAW_PDF_DIR, filename=f"{paper_id}.pdf")
        else:
            print(f"Already have: {result.title}")

        papers.append({
            "id": paper_id,
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "published": str(result.published.date()),
            "summary": result.summary,
            "pdf_path": pdf_path,
        })

    return papers


def parse_pdf(pdf_path):
    """Extract raw text from a PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def ingest():
    papers = fetch_papers()
    for paper in papers:
        parsed_path = os.path.join(PARSED_DIR, f"{paper['id']}.json")
        if os.path.exists(parsed_path):
            continue

        text = parse_pdf(paper["pdf_path"])
        paper["text"] = text

        with open(parsed_path, "w") as f:
            json.dump(paper, f)

        print(f"Parsed: {paper['title']} ({len(text)} chars)")

    return papers


if __name__ == "__main__":
    ingest()
