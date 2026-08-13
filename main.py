"""
main.py — Milestone 4: Streamlit chat interface.

Entry point for the app. Run with:
    streamlit run src/main.py

Chat UI on top of retrieve.answer_question(). Ingestion/chunking/embedding
are run separately (see ingest.py / chunk.py / embed.py) — this file only
serves the "ask questions" experience.
"""

import streamlit as st
from retrieve import answer_question

st.set_page_config(page_title="PaperMind", page_icon="🔍")

st.title("🔍 PaperMind")
st.caption("RAG agent for LLM reasoning & agentic systems research")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask about LLM reasoning / agentic systems research..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching papers..."):
            answer = answer_question(question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
