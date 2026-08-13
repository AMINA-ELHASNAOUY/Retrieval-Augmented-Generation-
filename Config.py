"""
config.py — Central config loader.
Every other module pulls settings from here instead of reading os.environ directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- LLM backend ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# --- Embeddings ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- Vector store ---
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
COLLECTION_NAME = "papermind_papers"

# --- arXiv ingestion ---
ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", 50))
ARXIV_CATEGORY = os.getenv("ARXIV_CATEGORY", "cs.CL")

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# --- Paths ---
DATA_DIR = Path("data")
PDF_DIR = DATA_DIR / "pdfs"
METADATA_PATH = DATA_DIR / "papers_metadata.json"

# Make sure the data dirs exist when this is imported
PDF_DIR.mkdir(parents=True, exist_ok=True)
