# 🔍 PaperMind — RAG Agent for LLM Reasoning & Agent Research

![Status](https://img.shields.io/badge/status-working%20prototype-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An AI research assistant that reads arXiv papers on LLM reasoning and agentic systems, and answers questions with cited sources. Built from scratch to understand how retrieval-augmented generation works under the hood. It runs fully locally: no API keys, no cloud costs.

## 💡 What is this?

Most "chat with your PDFs" demos are thin wrappers around an API call. This project builds the full pipeline manually (ingestion, parsing, chunking, embedding, vector search, and grounded generation) on a focused corpus of papers about chain-of-thought, tool use, and LLM agents.

The goal is twofold:

1. A working tool I actually use to study current ML research
2. A from-scratch demonstration of how RAG systems are engineered, not just consumed

## 🏗️ Architecture

┌─────────────┐ ┌──────────────┐ ┌───────────────┐
│ arXiv API │ --> │ PDF Parser │ --> │ Chunker │
│ (ingest.py)│ │ (PyMuPDF) │ │ (chunk.py) │
└─────────────┘ └──────────────┘ └───────┬───────┘
│
▼
┌─────────────┐ ┌──────────────┐ ┌───────────────┐
│ User │ --> │ Embedder │ <-- │ ChromaDB │
│ Query │ │ (MiniLM) │ │ (embed.py) │
└──────┬──────┘ └──────────────┘ └───────────────┘
│
▼
┌─────────────────────────────┐
│ Ollama LLM (retrieve.py) │
│ Retrieval + Cited Answer │
└─────────────────────────────┘


## 🚀 Features

| Feature | Status |
|---|---|
| arXiv ingestion with download retry/backoff | ✅ Done |
| PDF parsing & word-window chunking with overlap | ✅ Done |
| Local embeddings (sentence-transformers) | ✅ Done |
| Vector search (ChromaDB) | ✅ Done |
| Grounded generation with source list | ✅ Done |
| Chat UI (Streamlit) | ✅ Done |
| Expandable corpus (custom arXiv queries, `add_pdf.py` for local PDFs) | ✅ Done |
| Demo GIF / screenshots | 🔲 Planned |
| Retrieval quality evaluation | 🔲 Planned |

## 🛠️ Tech Stack

- **Ingestion:** arXiv API (`arxiv` package)
- **Parsing:** PyMuPDF
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`, local)
- **Vector DB:** ChromaDB (persistent, local)
- **Generation:** Ollama (default `qwen2.5:1.5b`, swappable)
- **UI:** Streamlit
- **Language:** Python 3.12

## ⚙️ Setup

```bash
git clone https://github.com/AMINA-ELHASNAOUY/Retrieval-Augmented-Generation-.git
cd Retrieval-Augmented-Generation-
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install [Ollama](https://ollama.com) and pull a model:

```bash
ollama pull qwen2.5:1.5b
```

## ▶️ Usage

Build the corpus:

```bash
python ingest.py --max 12                 # fetch papers from arXiv
python chunk.py                           # split into overlapping chunks
python embed.py                           # embed + store in ChromaDB
```

Ask questions:

```bash
streamlit run main.py                     # chat UI
python retrieve.py "What is chain-of-thought prompting?"   # CLI
```

Use a custom arXiv query:

```bash
python ingest.py --max 12 --query '(cat:cs.CL OR cat:cs.AI) AND abs:"LLM agents"'
```

Add a PDF you already have:

```bash
python add_pdf.py path/to/paper.pdf --id 2201.11903 --title "Paper title"
python chunk.py && python embed.py
```

Use a larger model (better cited answers, slower on a laptop):

```bash
ollama pull qwen2.5:7b
OLLAMA_MODEL=qwen2.5:7b streamlit run main.py
```

## ⚠️ Known Limitations

- The corpus is small, so answers are only as good as the papers ingested.
- arXiv search results can include off-topic papers; query wording matters.
- Some arXiv PDF downloads fail (404/406); `ingest.py` retries transient errors and skips permanent ones.
- Small local models can paraphrase loosely. Check the cited sources.

## 📍 Roadmap

- [x] Milestone 1: arXiv ingestion + PDF parsing
- [x] Milestone 2: Chunking + local embedding + ChromaDB storage
- [x] Milestone 3: Retrieval + LLM generation with source citations
- [x] Milestone 4: Streamlit chat interface
- [ ] Milestone 5: Polish (demo GIF, retrieval evaluation, larger corpus)

## 📄 License

MIT. See [LICENSE](LICENSE).
