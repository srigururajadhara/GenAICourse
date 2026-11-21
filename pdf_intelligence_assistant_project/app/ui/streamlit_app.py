from __future__ import annotations

import os
import time

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8001").rstrip("/")
DEFAULT_API_KEY = os.getenv("PDF_ASSISTANT_API_KEY", "local-dev-key-change-before-deployment")

st.set_page_config(page_title="PDF Intelligence Assistant", page_icon="📚", layout="wide")
st.markdown(
    """
    <style>
      :root { --ink:#172b25; --forest:#174c3a; --sage:#dfe9df; --gold:#c49a43; }
      .stApp { background: #f7f8f4; color: var(--ink); }
      section[data-testid="stSidebar"] { background: #edf2eb; border-right: 1px solid #d5dfd3; }
      h1,h2,h3 { color: #174c3a !important; }
      div[data-testid="stMetric"] { background:#fff; border:1px solid #d9e2d8; padding:12px; border-radius:12px; }
      div.stButton > button { background:#174c3a; color:white; border:0; border-radius:9px; }
      div.stButton > button:hover { background:#23664d; color:white; }
      .source-note { border-left:4px solid #c49a43; padding:10px 14px; background:white; border-radius:8px; margin:8px 0; }
      .small-muted { color:#5c6e63; font-size:.86rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "api_key" not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY
if "selected_document" not in st.session_state:
    st.session_state.selected_document = None
if "messages" not in st.session_state:
    st.session_state.messages = {}


def headers():
    return {"Authorization": f"Bearer {st.session_state.api_key}"}


def api_get(path: str):
    return requests.get(f"{API_BASE}{path}", headers=headers(), timeout=20)


def api_post(path: str, **kwargs):
    return requests.post(f"{API_BASE}{path}", headers=headers(), timeout=180, **kwargs)


with st.sidebar:
    st.markdown("## 📚 PDF Intelligence Assistant")
    st.caption("Dual-pipeline · Hybrid RAG · Evidence-first")
    st.text_input("API access key", type="password", key="api_key")
    st.caption(f"API: {API_BASE}")
    if st.button("Check API connection", use_container_width=True):
        try:
            response = api_get("/health/live")
            if response.ok:
                st.success("API is reachable")
            else:
                st.error(f"API returned {response.status_code}")
        except requests.RequestException:
            st.error("Cannot reach the API. Start the FastAPI service first.")
    st.divider()
    st.markdown("### Upload a PDF")
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)
    if st.button("Upload and process", disabled=uploaded is None, use_container_width=True):
        try:
            response = api_post(
                "/api/v1/documents",
                files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
            )
            if response.status_code == 202:
                data = response.json()
                st.session_state.selected_document = data["document_id"]
                st.success("Uploaded. Processing has started.")
                st.rerun()
            else:
                st.error(response.json().get("detail", response.text))
        except requests.RequestException as exc:
            st.error(f"Upload failed: {exc}")
    st.divider()
    st.markdown("### Your documents")
    try:
        docs_response = api_get("/api/v1/documents")
        if docs_response.ok:
            documents = docs_response.json()
        else:
            documents = []
            st.error(docs_response.json().get("detail", "Could not load documents"))
    except requests.RequestException:
        documents = []
        st.info("Start the API to load documents.")

    if documents:
        options = {f"{doc['file_name']} · {doc['status']}": doc["document_id"] for doc in documents}
        labels = list(options)
        selected_label = next((label for label, value in options.items() if value == st.session_state.selected_document), labels[0])
        choice = st.selectbox("Select document", labels, index=labels.index(selected_label))
        st.session_state.selected_document = options[choice]
        if st.button("Refresh document status", use_container_width=True):
            st.rerun()
    else:
        st.caption("No PDFs uploaded yet.")

st.title("Understand any PDF. Ask questions with evidence.")
st.markdown(
    "Upload a document to build two knowledge pipelines: **vector + lexical search** and a **Neo4j knowledge graph**. "
    "Answers and summaries are restricted to the selected PDF and include page references."
)

if not st.session_state.selected_document:
    st.info("Upload a PDF from the left panel to begin. The included sample is `sample_documents_spotify_web_app_architecture.pdf`.")
    st.stop()

selected_id = st.session_state.selected_document
try:
    status_response = api_get(f"/api/v1/documents/{selected_id}")
    if not status_response.ok:
        st.error("Selected document is unavailable in this workspace.")
        st.stop()
    document = status_response.json()
except requests.RequestException:
    st.error("Cannot reach the API.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Document", document["file_name"][:24])
c2.metric("Overall status", document["status"])
c3.metric("Vector pipeline", document["vector_status"])
c4.metric("Knowledge graph", document["graph_status"])

if document["status"] == "EXTRACTION_REVIEW_REQUIRED":
    st.warning("Some pages may contain scanned, low-text or OCR-derived content. Review the extracted passages before allowing either index to be built.")
    if document.get("warning"):
        st.caption(document["warning"])
    try:
        review_response = api_get(f"/api/v1/documents/{selected_id}/chunks")
        review_chunks = review_response.json() if review_response.ok else []
    except requests.RequestException:
        review_chunks = []
        st.error("Could not load extracted passages for review.")
    st.subheader("Extraction review")
    st.caption(f"Review {len(review_chunks)} extracted passages. OCR text can contain recognition errors.")
    for item in review_chunks:
        with st.expander(f"Page {item['page']} · {item.get('section') or 'Document text'}"):
            st.write(item["text"])
    reviewed = st.checkbox("I reviewed the extracted passages and accept their content for indexing.")
    if st.button("Approve extraction and build both indexes", type="primary", disabled=not reviewed):
        approval = api_post(f"/api/v1/documents/{selected_id}/approve-extraction")
        if approval.status_code == 202:
            st.success("Extraction approved. Both indexing pipelines have started.")
            st.rerun()
        st.error(approval.json().get("detail", approval.text))
    st.stop()

if document["status"] in {"UPLOADED", "EXTRACTING", "INDEXING_VECTOR", "INDEXING_GRAPH", "EXTRACTION_APPROVED_PENDING_INDEX"}:
    st.warning("The document is still processing. Refresh the status in the sidebar to see the latest stage.")
    st.progress(0.55 if document["status"] in {"INDEXING_VECTOR", "INDEXING_GRAPH"} else 0.2)
    st.stop()
if document["status"] != "READY":
    st.error(f"Both pipelines must finish successfully before Q&A is enabled. Status: {document['status']}")
    if document.get("warning"):
        st.caption(document["warning"])
    if st.button("Retry ingestion"):
        retry = api_post(f"/api/v1/documents/{selected_id}/retry")
        if retry.ok:
            st.success("Retry queued")
            st.rerun()
        else:
            st.error(retry.json().get("detail", retry.text))
    st.stop()

if document.get("warning"):
    st.warning(document["warning"])

summary_tab, chat_tab, chunks_tab, admin_tab = st.tabs(["Document summary", "Ask the PDF", "Extracted passages", "Document controls"])

with summary_tab:
    st.subheader("Summarize this document")
    summary_mode = st.radio("Summary type", ["Executive", "Detailed", "Section"], horizontal=True)
    section_name = st.text_input("Section heading", placeholder="Required for section summary") if summary_mode == "Section" else None
    if st.button("Generate summary", type="primary"):
        with st.spinner("Building a source-linked summary..."):
            try:
                result = api_post(
                    "/api/v1/summaries",
                    json={"document_id": selected_id, "mode": summary_mode.lower(), "section": section_name},
                )
                if result.ok:
                    st.session_state[f"summary_{selected_id}_{summary_mode}"] = result.json()
                else:
                    st.error(result.json().get("detail", result.text))
            except requests.RequestException as exc:
                st.error(f"Summary request failed: {exc}")
    summary = st.session_state.get(f"summary_{selected_id}_{summary_mode}")
    if summary:
        if summary.get("abstained"):
            st.warning(summary["summary"])
        else:
            st.markdown(summary["summary"])
            for citation in summary.get("citations", []):
                with st.expander(f"Source · Page {citation['page']} · {citation['document_name']}"):
                    st.write(citation["excerpt"])

with chat_tab:
    st.subheader("Ask questions about the selected PDF")
    conversation = st.session_state.messages.setdefault(selected_id, [])
    for message in conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            for citation in message.get("citations", []):
                with st.expander(f"Source · Page {citation['page']} · {citation['document_name']}"):
                    st.write(citation["excerpt"])
                    st.caption(f"Retrieval channels: {', '.join(citation.get('retrieval_sources', []))}")
    question = st.chat_input("Ask something that this PDF can answer...")
    if question:
        conversation.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching vector, keyword and graph evidence..."):
                try:
                    history = [
                        {"role": item["role"], "content": item["content"]}
                        for item in conversation[-8:-1]
                    ]
                    result = api_post(
                        "/api/v1/ask",
                        json={"document_id": selected_id, "question": question, "conversation_history": history},
                    )
                    if result.ok:
                        answer_data = result.json()
                        st.markdown(answer_data["answer"])
                        if answer_data.get("abstained"):
                            st.caption("No sufficient evidence was found in the selected PDF.")
                        for citation in answer_data.get("citations", []):
                            with st.expander(f"Source · Page {citation['page']} · {citation['document_name']}"):
                                st.write(citation["excerpt"])
                                st.caption(f"Channels: {', '.join(citation.get('retrieval_sources', []))}")
                        if answer_data.get("retrieval_warnings"):
                            st.warning("Retrieval warnings: " + "; ".join(answer_data["retrieval_warnings"]))
                        conversation.append({
                            "role": "assistant", "content": answer_data["answer"],
                            "citations": answer_data.get("citations", []),
                        })
                    else:
                        error = result.json().get("detail", result.text)
                        st.error(error)
                        conversation.append({"role": "assistant", "content": f"Request failed: {error}"})
                except requests.RequestException as exc:
                    st.error(f"Question request failed: {exc}")
                    conversation.append({"role": "assistant", "content": "The API could not be reached."})

with chunks_tab:
    st.subheader("Extracted, page-linked passages")
    try:
        chunks_response = api_get(f"/api/v1/documents/{selected_id}/chunks")
        if chunks_response.ok:
            chunk_rows = chunks_response.json()
            st.caption(f"{len(chunk_rows)} passages indexed")
            for chunk in chunk_rows:
                with st.expander(f"Page {chunk['page']} · {chunk.get('section') or 'Document text'} · {chunk['chunk_id'][:8]}"):
                    st.write(chunk["text"])
        else:
            st.error(chunks_response.text)
    except requests.RequestException:
        st.error("Could not load passages.")

with admin_tab:
    st.subheader("Document controls")
    st.write("Delete removes the original PDF, local indexes, canonical extraction and graph records for this document.")
    confirm_delete = st.checkbox("I understand this action deletes this document and its derived indexes")
    if st.button("Delete selected PDF", disabled=not confirm_delete):
        try:
            deletion = requests.delete(f"{API_BASE}/api/v1/documents/{selected_id}", headers=headers(), timeout=60)
            if deletion.status_code == 204:
                st.session_state.selected_document = None
                st.session_state.messages.pop(selected_id, None)
                st.success("Document and derived data deleted.")
                st.rerun()
            else:
                st.error(deletion.json().get("detail", deletion.text))
        except requests.RequestException as exc:
            st.error(f"Deletion failed: {exc}")
