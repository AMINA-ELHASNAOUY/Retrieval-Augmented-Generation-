"""
config.py — central configuration for PaperMind.

All tunable constants live here. Values can be overridden with a .env file
(copy .env.example to .env).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# --- Paths -------------------------------------------------------------
DATA_DIR = BASE_DIR / "data"
RAW_PDF_DIR = DATA_DIR / "raw_pdfs"
METADATA_PATH = DATA_DIR / "metadata.json"
CHROMA_DIR = Path(os.getenv("CHROMA_DB_PATH", DATA_DIR / "chroma_db"))
if not CHROMA_DIR.is_absolute():
    CHROMA_DIR = (BASE_DIR / CHROMA_DIR).resolve()

for d in (DATA_DIR, RAW_PDF_DIR, CHROMA_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- arXiv ingestion -----------------------------------------------------
ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]
_TOPICS = [
    'all:"chain-of-thought"',
    'all:"LLM reasoning"',
    'all:"agentic"',
    'all:"tool use"',
    'all:"multi-agent"',
]
ARXIV_SEARCH_QUERY = (
    "(" + " OR ".join(f"cat:{c}" for c in ARXIV_CATEGORIES) + ")"
    + " AND (" + " OR ".join(_TOPICS) + ")"
)
ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "10"))

# --- Chunking (measured in words) ------------------------------------------
# MiniLM only reads ~256 tokens, so keep chunks well under that.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "40"))

# --- Embeddings ------------------------------------------------------------
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- Vector store ----------------------------------------------------------
CHROMA_COLLECTION_NAME = "papermind_papers"

# --- Generation ------------------------------------------------------------
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "4096"))

TOP_K_RESULTS = 5
