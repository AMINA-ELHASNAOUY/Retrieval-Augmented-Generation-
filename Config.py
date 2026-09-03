"""
config.py — central configuration for PaperMind.

All tunable constants live here so ingest/chunk/embed/retrieve/main
don't hardcode paths or model names.
"""

import os
from pathlib import Path

# --- Paths -------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_PDF_DIR = DATA_DIR / "raw_pdfs"
CHROMA_DIR = DATA_DIR / "chroma_db"

for d in (DATA_DIR, RAW_PDF_DIR, CHROMA_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- arXiv ingestion -----------------------------------------------------
ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]  # NLP, AI, ML
ARXIV_SEARCH_QUERY = (
    "(LLM reasoning) OR (chain-of-thought) OR (agentic systems) OR (tool use)"
)
ARXIV_MAX_RESULTS = 25  # papers per ingestion run

# --- Chunking ------------------------------------------------------------
CHUNK_SIZE = 500        # tokens (approx, via whitespace split)
CHUNK_OVERLAP = 50      # tokens

# --- Embeddings ------------------------------------------------------------
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Vector store ----------------------------------------------------------
CHROMA_COLLECTION_NAME = "papermind_papers"

# --- Generation ------------------------------------------------------------
# Local model served via Ollama. Swap for an API model later if needed.
OLLAMA_MODEL = os.getenv("PAPERMIND_LLM_MODEL", "qwen2.5")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

TOP_K_RESULTS = 5  # chunks retrieved per query
