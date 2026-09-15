import os

# Search terms for arXiv
ARXIV_QUERY = "LLM reasoning OR agentic systems OR chain-of-thought OR multi-agent"
MAX_PAPERS = 20

# Paths
DATA_DIR = "data"
RAW_PDF_DIR = os.path.join(DATA_DIR, "raw_pdfs")
PARSED_DIR = os.path.join(DATA_DIR, "parsed")

# Chunking
CHUNK_SIZE = 500       # tokens/words per chunk
CHUNK_OVERLAP = 50

# Embedding
EMBED_MODEL = "all-MiniLM-L6-v2"

# Vector DB
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
COLLECTION_NAME = "papermind_papers"

# Generation
OLLAMA_MODEL = "qwen2.5"

os.makedirs(RAW_PDF_DIR, exist_ok=True)
os.makedirs(PARSED_DIR, exist_ok=True)
