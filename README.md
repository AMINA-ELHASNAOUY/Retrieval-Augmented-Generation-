# 🔍 PaperMind: RAG Agent for LLM Reasoning & Agent Research

![Status](https://img.shields.io/badge/status-working%20prototype-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Runs locally](https://img.shields.io/badge/runs-100%25%20locally-orange)

![PaperMind demo](assets/demo.png)

An AI research assistant that reads arXiv papers on LLM reasoning and agentic systems, and answers questions with cited sources. Built from scratch to understand how retrieval-augmented generation works under the hood. It runs fully locally: no API keys, no cloud costs.

## 💡 What is this?

Most "chat with your PDFs" demos are thin wrappers around an API call. This project builds the full pipeline manually (ingestion, parsing, chunking, embedding, vector search, and grounded generation) on a focused corpus of papers about chain-of-thought, tool use, and LLM agents.

The goal is twofold:

1. A working tool I actually use to study current ML research
2. A from-scratch demonstration of how RAG systems are engineered, not just consumed

## 🏗️ Architecture

```mermaid
flowchart LR
    A[arXiv API<br/>ingest.py] --> B[PDF Parser<br/>PyMuPDF]
    B --> C[Chunker<br/>chunk.py]
    C --> D[Embedder<br/>MiniLM-L6-v2]
    D --> E[(ChromaDB<br/>embed.py)]
    Q[User question] --> F[Query embedding]
    F --> E
    E -->|top-k chunks| G[Ollama LLM<br/>retrieve.py]
    G --> H[Answer + cited sources<br/>Streamlit UI]
```

**Indexing (offline):** `ingest.py` → `chunk.py` → `embed.py`

**Querying (online):** `main.py` / `retrieve.py` embed the question, pull the most similar chunks from ChromaDB, and ask the LLM to answer only from that context.

## 🚀 Features

| Feature | Status |
|---|---|
| arXiv ingestion with download retry/backoff | ✅ Done |
| PDF parsing & word-window chunking with overlap | ✅ Done |
| Local embeddings (sentence-transformers) | ✅ Done |
| Vector search (ChromaDB, persistent) | ✅ Done |
| Grounded generation with numbered source list | ✅ Done |
| Chat UI (Streamlit) | ✅ Done |
| Expandable corpus (custom arXiv queries, `add_pdf.py` for local PDFs) | ✅ Done |
| Configurable via `.env` | ✅ Done |
| Demo screenshot | ✅ Done |

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | arXiv API (`arxiv` package) |
| Parsing | PyMuPDF |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local) |
| Vector DB | ChromaDB (persistent, local) |
| Generation | Ollama (default `qwen2.5:1.5b`, swappable) |
| UI | Streamlit |
| Language | Python 3.12 |

## 📁 Project Structure

| File | Purpose |
|---|---|
| `config.py` | Central settings, read from `.env` with sensible defaults |
| `ingest.py` | Search arXiv, download PDFs (with retry), save metadata |
| `add_pdf.py` | Add a PDF you already have to the corpus |
| `chunk.py` | Extract text and split into overlapping word windows |
| `embed.py` | Embed chunks and store them in ChromaDB |
| `retrieve.py` | Retrieve top-k chunks and generate a cited answer (also a CLI) |
| `main.py` | Streamlit chat interface |

## ⚙️ Setup

```bash
git clone https://github.com/AMINA-ELHASNAOUY/Retrieval-Augmented-Generation-.git
cd Retrieval-Augmented-Generation-
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optional: tweak models, chunk size, etc.
```

Install [Ollama](https://ollama.com) and pull a model:

```bash
ollama pull qwen2.5:1.5b
```

## ▶️ Usage

**1. Build the corpus**

```bash
python ingest.py --max 12     # fetch papers from arXiv
python chunk.py               # split into overlapping chunks
python embed.py               # embed + store in ChromaDB
```

**2. Ask questions**

```bash
streamlit run main.py                                       # chat UI
python retrieve.py "What is chain-of-thought prompting?"    # CLI
```

**Custom arXiv query**

```bash
python ingest.py --max 12 --query '(cat:cs.CL OR cat:cs.AI) AND abs:"LLM agents"'
```

**Add a PDF you already have**

```bash
python add_pdf.py path/to/paper.pdf --id 2201.11903 --title "Paper title"
python chunk.py && python embed.py
```

**Use a larger model** (better cited answers, slower on a laptop)

```bash
ollama pull qwen2.5:7b
OLLAMA_MODEL=qwen2.5:7b streamlit run main.py
```

## 🔧 Configuration

All settings live in `config.py` and can be overridden in a `.env` file (`cp .env.example .env`).

| Variable | Default | What it does |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Local LLM used for answers (`qwen2.5:7b` is better but slower) |
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama is running |
| `OLLAMA_NUM_CTX` | `4096` | Context window passed to the model |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model for chunks and queries |
| `CHROMA_DB_PATH` | `./data/chroma_db` | Where the vector store is persisted |
| `ARXIV_MAX_RESULTS` | `10` | Papers fetched per `ingest.py` run |
| `CHUNK_SIZE` | `200` | Words per chunk |
| `CHUNK_OVERLAP` | `40` | Words shared between neighbouring chunks |

Retrieval returns the top 5 chunks per question (`TOP_K_RESULTS` in `config.py`).

## 🧠 Design Decisions

- **200-word chunks.** all-MiniLM-L6-v2 only reads about 256 tokens, so longer chunks would be silently truncated before embedding.
- **40-word overlap.** Keeps sentences that fall on a chunk boundary retrievable from either side.
- **Word-based splitting.** Simple to reason about and good enough for this embedding model; no tokenizer dependency.
- **Local models only.** Embeddings (sentence-transformers) and generation (Ollama) both run on the laptop: no API keys, no usage costs, papers never leave the machine.
- **Small default LLM.** `qwen2.5:1.5b` keeps answers fast on a MacBook Air; the model is one environment variable away from a larger one.
- **Grounded prompt, low temperature.** The system prompt tells the model to answer only from the retrieved passages, and generation runs at temperature 0.2 to keep it close to the source text.

## 💬 Example Output

```text
$ python retrieve.py "What is chain-of-thought prompting and why does it help?"

Chain-of-thought prompting involves providing a series of intermediate reasoning
steps as a chain of thought, which helps in improving the ability of large language
models to perform complex reasoning. It allows models to decompose multi-step
problems into intermediate steps, enabling additional computation allocation for
more reasoning steps. The chain of thought provides an interpretable window into
the model's reasoning process, facilitating debugging and understanding of the
reasoning path. [...]

Sources:
[1] Chain-of-Thought Prompting Elicits Reasoning in Large Language Models - https://arxiv.org/pdf/2201.11903v6
```

## 📚 Current Corpus

The working corpus has 8 papers on chain-of-thought, tool use, and LLM agents (483 chunks), including *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* (2201.11903) and *Efficient Tool Use with Chain-of-Abstraction Reasoning* (2401.17464). PDFs and the vector store are not committed; rebuild them with the commands above.

## ⚠️ Known Limitations

- The corpus is small, so answers are only as good as the papers ingested.
- arXiv search results can include off-topic papers; query wording matters.
- Some arXiv PDF downloads fail (404/406). `ingest.py` retries transient errors and skips permanent ones.
- Small local models can paraphrase loosely. Check the cited sources.

## 🔭 Future Work

- Retrieval quality evaluation (hit rate / recall@k on a small hand-labelled question set)
- Larger, curated corpus
- Animated demo GIF

## 📄 License

MIT. See [LICENSE](LICENSE).
