"""
add_pdf.py — add a local PDF to the corpus.

Usage:
    python add_pdf.py path/to/paper.pdf --id 2403.12036 --title "Paper title"
Then re-run: python chunk.py && python embed.py
"""

import argparse
import json
import shutil

import pymupdf

import config

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--id", required=True, help="arXiv id, or any unique id")
ap.add_argument("--title", required=True)
ap.add_argument("--url", default=None)
ap.add_argument("--published", default="")
args = ap.parse_args()

records = json.loads(config.METADATA_PATH.read_text()) if config.METADATA_PATH.exists() else []
if any(r["arxiv_id"] == args.id for r in records):
    raise SystemExit(f"{args.id} is already in the corpus.")

dest = config.RAW_PDF_DIR / f"{args.id.replace('/', '_')}.pdf"
shutil.copy(args.pdf, dest)
with pymupdf.open(dest) as doc:
    pages = len(doc)

records.append({
    "arxiv_id": args.id,
    "title": args.title,
    "authors": [],
    "abstract": "",
    "pdf_url": args.url or f"https://arxiv.org/abs/{args.id}",
    "published": args.published,
    "pdf_path": str(dest),
    "num_pages": pages,
})
config.METADATA_PATH.write_text(json.dumps(records, indent=2))
print(f"Added {args.id} ({pages} pages). Total in corpus: {len(records)}")
print("Now run: python chunk.py && python embed.py")
