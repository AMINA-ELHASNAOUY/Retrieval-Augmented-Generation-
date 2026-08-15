# Retrieval-Augmented-Generation
# 🔍 PaperMind — RAG Agent for LLM Reasoning & Agent Research

[![Status](https://img.shields.io/badge/status-in%20development-yellow)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

> An AI research assistant that reads arXiv papers on LLM reasoning and agentic systems, and answers questions with cited sources — built from scratch to understand how retrieval-augmented generation actually works under the hood.

---

## 💡 What is this?

Most "chat with your PDFs" demos are thin wrappers around an API call. This project builds the full pipeline manually — parsing, chunking, embedding, vector search, and grounded generation — using a focused corpus of research papers on **LLM reasoning and agentic systems** (chain-of-thought, tool use, multi-agent orchestration).

The goal is twofold:
1. A working tool I actually use to study current ML research
2. A from-scratch demonstration of how RAG systems are engineered, not just consumed

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  arXiv API  │ --> │  PDF Parser  │ --> │  Chunker      │
│  (ingestion)│     │  (PyMuPDF)   │     │  (overlap 50) │
└─────────────┘     └──────────────┘     └───────┬───────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   User      │ --> │  Embedder    │ <-- │  ChromaDB     │
│   Query     │     │  (MiniLM)    │     │  (vector store)│
└──────┬──────┘     └──────────────┘     └───────────────┘
       │
       ▼
┌─────────────────────────────┐
│  LLM (Ollama / API)          │
│  Retrieval + Cited Answer    │
└─────────────────────────────┘
```

---

## 🚀 Core Features

| Feature | Status |
|---|---|
| arXiv ingestion pipeline | 🔲 Planned |
| PDF parsing & chunking | 🔲 Planned |
| Local embeddings (sentence-transformers) | 🔲 Planned |
| Vector search (ChromaDB) | 🔲 Planned |
| Grounded generation with citations | 🔲 Planned |
| Chat UI (Streamlit) | 🔲 Planned |
| Expandable corpus (add papers on demand) | 🔲 Planned |

*(Checklist updates as milestones are completed — no feature is marked done until it's actually working.)*

---

## 🛠️ Tech Stack

- **Ingestion:** arXiv API
- **Parsing:** PyMuPDF
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`, local, free)
- **Vector DB:** ChromaDB
- **Generation:** Ollama (qwen2.5) — swappable for an API model
- **UI:** Streamlit
- **Language:** Python 3.11+

---

## 📍 Roadmap

- [ ] **Milestone 1** — arXiv ingestion + PDF parsing pipeline
- [ ] **Milestone 2** — Chunking + local embedding + ChromaDB storage
- [ ] **Milestone 3** — Retrieval + LLM generation with source citations
- [ ] **Milestone 4** — Streamlit chat interface
- [ ] **Milestone 5** — Corpus expansion + polish (README demo GIF, error handling)

---

## 📖 Why This Project

RAG is one of the most in-demand applied ML skills right now, and reasoning/agentic systems are the fastest-moving subfield in current LLM research. Building this from raw components — rather than a framework like LangChain — was a deliberate choice to actually understand retrieval, chunking trade-offs, and grounding instead of treating them as black boxes.

---

## 📄 License

MIT — see [LICENSE](LICENSE)
