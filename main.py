"""
main.py — Streamlit chat interface for PaperMind.

Run with:
    streamlit run main.py

Ingestion/chunking/embedding are run separately (ingest.py, chunk.py, embed.py).
This file only serves the "ask questions" experience.
"""

import streamlit as st

import config
from embed import get_collection
from retrieve import answer_question

st.set_page_config(page_title="PaperMind", page_icon="🔍")


@st.cache_resource
def corpus_stats():
    col = get_collection()
    metas = col.get(include=["metadatas"])["metadatas"]
    return col.count(), len({m["title"] for m in metas})


st.title("🔍 PaperMind")
st.caption("RAG agent for LLM reasoning & agentic systems research")

n_chunks, n_papers = corpus_stats()
with st.sidebar:
    st.header("Corpus")
    st.metric("Papers", n_papers)
    st.metric("Chunks", n_chunks)
    st.caption(f"LLM: {config.OLLAMA_MODEL}")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


def show_sources(sources):
    if sources:
        with st.expander("Sources"):
            for s in sources:
                st.markdown(f"**[{s['n']}]** [{s['title']}]({s['url']})")


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        show_sources(msg.get("sources"))

if question := st.chat_input("Ask about LLM reasoning / agentic systems research..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching papers..."):
            out = answer_question(question)
        st.markdown(out["answer"])
        show_sources(out["sources"])

    st.session_state.messages.append(
        {"role": "assistant", "content": out["answer"], "sources": out["sources"]}
    )
