from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8001").rstrip("/")
DEFAULT_API_KEY = os.getenv("PDF_ASSISTANT_API_KEY", "local-dev-key-change-before-deployment")
TIMEOUT = (10, 180)

st.set_page_config(
    page_title="Guru PDF Intelligence",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit-native light theme is configured in .streamlit/config.toml. These
# targeted rules style custom surfaces without globally overriding widget text.
st.markdown(
    """
    <style>
      :root {
        --ink: #172033; --muted: #64748b; --line: #e2e8f0;
        --canvas: #f5f7fb; --surface: #ffffff; --brand: #3157d5;
        --brand-dark: #2445b5; --soft-blue: #edf2ff; --soft-green: #ecfdf3;
      }
      .stApp, [data-testid="stAppViewContainer"] { background: var(--canvas); color: var(--ink); }
      [data-testid="stHeader"] { background: rgba(245,247,251,.92); }
      .block-container { max-width: 1440px; padding-top: 1.6rem; padding-bottom: 3rem; }
      [data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }
      [data-testid="stSidebar"] > div { padding-top: 1.2rem; }
      h1,h2,h3,h4 { color: #172033 !important; letter-spacing: -.025em; }
      p, label, li, [data-testid="stMarkdownContainer"] { color: #263247; }
      .muted { color: var(--muted); font-size: .92rem; }
      .brand-lockup { display:flex; gap:12px; align-items:center; padding: 4px 0 16px; }
      .brand-icon { width:42px; height:42px; display:flex; align-items:center; justify-content:center;
        background:#edf2ff; border-radius:13px; font-size:23px; }
      .brand-name { font-weight:750; color:#172033; font-size:1.05rem; line-height:1.2; }
      .brand-sub { color:#64748b; font-size:.76rem; margin-top:3px; }
      .hero { background:linear-gradient(120deg,#fff 0%,#f0f4ff 100%); border:1px solid #e2e8f0;
        border-radius:20px; padding:26px 28px; margin-bottom:20px; }
      .hero-kicker { color:#3157d5; font-size:.76rem; text-transform:uppercase; letter-spacing:.11em; font-weight:750; }
      .hero-title { color:#172033; font-size:2rem; line-height:1.15; font-weight:800; margin:7px 0 8px; }
      .hero-copy { color:#64748b; font-size:1rem; max-width:760px; }
      .surface { background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; }
      .metric-label { color:#64748b; font-size:.82rem; }
      .metric-value { color:#172033; font-size:1.65rem; font-weight:760; margin-top:3px; }
      .doc-card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:15px 16px; height:100%; }
      .doc-name { font-weight:700; color:#172033; overflow-wrap:anywhere; }
      .doc-meta { color:#64748b; font-size:.82rem; margin-top:5px; }
      .status-pill { display:inline-block; border-radius:99px; padding:3px 9px; font-size:.72rem; font-weight:700; background:#eef2f7; color:#475569; }
      .stButton > button, .stDownloadButton > button { border-radius:10px; font-weight:650; min-height:2.55rem; }
      .stButton > button[kind="primary"] { background:#3157d5; border-color:#3157d5; color:white; }
      .stButton > button[kind="primary"]:hover { background:#2445b5; border-color:#2445b5; }
      .stTextInput input, .stTextArea textarea, [data-testid="stChatInput"] textarea,
      [data-baseweb="select"] > div { background:#fff !important; color:#172033 !important; border-color:#cbd5e1 !important; }
      .stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#94a3b8 !important; }
      [data-testid="stChatMessage"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:14px 16px; }
      [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:13px 16px; }
      [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color:#172033 !important; }
      [data-testid="stFileUploader"] { background:#fff; border:1px dashed #a8b7d4; border-radius:14px; padding:10px; }
      [data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:12px; }
      div[role="radiogroup"] label { color:#263247 !important; }
      hr { border-color:#e2e8f0; }
      @media (max-width: 700px) { .hero { padding:20px; } .hero-title { font-size:1.55rem; } }
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
if "page" not in st.session_state:
    st.session_state.page = "Overview"
if "summaries" not in st.session_state:
    st.session_state.summaries = {}

# Apply navigation requested by the previous run BEFORE creating the radio widget.
# Streamlit does not allow changing a widget's keyed state after that widget exists.
if "pending_page" in st.session_state:
    st.session_state.page = st.session_state.pop("pending_page")


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.api_key}"}


def api_request(method: str, path: str, **kwargs: Any) -> requests.Response:
    # Defaults can be overridden by individual calls without passing duplicate
    # keyword arguments (for example, fetch_documents uses a shorter timeout).
    kwargs.setdefault("headers", auth_headers())
    kwargs.setdefault("timeout", TIMEOUT)
    return requests.request(method, f"{API_BASE}{path}", **kwargs)


def response_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        return str(payload.get("detail", payload))
    except (ValueError, AttributeError):
        return response.text[:500] or f"Request failed ({response.status_code})"


def fetch_documents() -> list[dict[str, Any]]:
    response = api_request("GET", "/api/v1/documents", timeout=(8, 30))
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, list) else []


def status_label(value: str) -> str:
    return value.replace("_", " ").title()


def is_ready(document: dict[str, Any]) -> bool:
    return document.get("status") == "READY"


def render_citations(citations: list[dict[str, Any]]) -> None:
    if not citations:
        st.caption("No source passages were returned for this result.")
        return
    st.markdown("**Sources and page references**")
    for index, citation in enumerate(citations, start=1):
        title = f"{index}. {citation.get('document_name', 'Document')} · Page {citation.get('page', '?')}"
        with st.expander(title):
            st.write(citation.get("excerpt", "No excerpt available."))
            channels = citation.get("retrieval_sources", [])
            if channels:
                st.caption("Evidence channels: " + ", ".join(channels))


def render_document_picker(documents: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not documents:
        return None
    by_id = {doc["document_id"]: doc for doc in documents}
    current = st.session_state.selected_document
    if current not in by_id:
        current = documents[0]["document_id"]
        st.session_state.selected_document = current
    labels = {f"{doc['file_name']}  ·  {status_label(doc['status'])}": doc["document_id"] for doc in documents}
    selected_label = next(label for label, doc_id in labels.items() if doc_id == current)
    chosen = st.selectbox("Active document", list(labels), index=list(labels).index(selected_label), label_visibility="collapsed")
    st.session_state.selected_document = labels[chosen]
    return by_id[labels[chosen]]


# Sidebar: navigation, connection and upload. The key is never displayed in plain text.
with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-icon">📘</div><div><div class="brand-name">Guru PDF Intelligence</div><div class="brand-sub">Your documents, understood</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("##### WORKSPACE")
    page = st.radio(
        "Navigation", ["Overview", "My documents", "AI chat", "Smart summary", "Extracted content"],
        key="page", label_visibility="collapsed",
    )
    st.divider()
    st.markdown("##### ADD A DOCUMENT")
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"], help="PDF only · upload size is controlled by the server")
    if st.button("Upload and analyse PDF", type="primary", use_container_width=True, disabled=uploaded is None):
        with st.spinner("Uploading your PDF and starting analysis…"):
            try:
                result = api_request(
                    "POST", "/api/v1/documents",
                    files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                )
                if result.status_code == 202:
                    st.session_state.selected_document = result.json()["document_id"]
                    st.session_state.pending_page = "My documents"
                    st.success("Upload received. Analysis has started.")
                    st.rerun()
                st.error(response_error(result))
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")
    st.divider()
    st.markdown("##### CONNECTION")
    with st.expander("API access settings", expanded=False):
        st.text_input("Workspace API key", type="password", key="api_key", help="Your key is sent only to your configured PDF Assistant API.")
        st.caption(f"API endpoint: {API_BASE}")
        if st.button("Test connection", use_container_width=True):
            try:
                check = requests.get(f"{API_BASE}/health/live", timeout=8)
                if check.ok:
                    st.success("Backend is reachable")
                else:
                    st.error(f"Backend returned {check.status_code}")
            except requests.RequestException:
                st.error("Backend is not reachable")
    st.caption("Guru PDF Intelligence · Evidence-first document assistant")

# Load workspace data once per rerun.
try:
    documents = fetch_documents()
    api_error = None
except requests.HTTPError as exc:
    documents, api_error = [], response_error(exc.response) if exc.response is not None else str(exc)
except requests.RequestException as exc:
    documents, api_error = [], str(exc)

if api_error:
    st.markdown('<div class="hero"><div class="hero-kicker">Workspace connection</div><div class="hero-title">Connect to your document workspace</div><div class="hero-copy">The interface is ready, but the backend could not load your documents. Check the API service and workspace access key.</div></div>', unsafe_allow_html=True)
    st.error(api_error)
    st.stop()

selected_doc = render_document_picker(documents)

if page == "Overview":
    st.markdown(
        '<div class="hero"><div class="hero-kicker">Your AI document workspace</div><div class="hero-title">Understand your PDFs. Find answers faster.</div><div class="hero-copy">Upload a document, get an evidence-linked summary, and ask questions grounded in the pages you provide.</div></div>',
        unsafe_allow_html=True,
    )
    ready_count = sum(is_ready(doc) for doc in documents)
    processing_count = sum(doc.get("status") not in {"READY", "FAILED_RETRYABLE"} for doc in documents)
    failed_count = sum(doc.get("status") == "FAILED_RETRYABLE" for doc in documents)
    m1, m2, m3 = st.columns(3)
    m1.metric("Documents", len(documents))
    m2.metric("Ready to ask", ready_count)
    m3.metric("Processing", processing_count)
    st.write("")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### Get started")
        st.markdown('<div class="surface"><b>1 · Upload a PDF</b><p class="muted">Add a report, manual, contract or research paper using the upload panel.</p><b>2 · Let the assistant analyse it</b><p class="muted">The system extracts pages and builds vector, keyword and graph indexes.</p><b>3 · Explore with AI</b><p class="muted">Ask questions or generate summaries with page-linked evidence.</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### What you can do")
        st.markdown('<div class="surface"><p>💬 <b>Ask questions</b><br><span class="muted">Get answers from your selected PDF.</span></p><p>📝 <b>Create summaries</b><br><span class="muted">Executive, detailed or section summaries.</span></p><p>🔎 <b>Review evidence</b><br><span class="muted">Open extracted passages and source pages.</span></p></div>', unsafe_allow_html=True)
    st.markdown("### Recently added")
    if documents:
        for doc in documents[:5]:
            with st.container(border=True):
                a, b, c = st.columns([4, 1.5, 1])
                a.markdown(f"**📄 {doc['file_name']}**")
                a.caption(f"{doc.get('page_count') or '—'} pages · Added {doc.get('created_at', 'date unavailable')}")
                b.write(status_label(doc["status"]))
                if c.button("Open", key=f"open_home_{doc['document_id']}"):
                    st.session_state.selected_document = doc["document_id"]
                    st.session_state.pending_page = "My documents"
                    st.rerun()
    else:
        st.info("No documents yet. Upload your first PDF from the left panel.")

elif page == "My documents":
    st.title("My documents")
    st.caption("Manage uploaded PDFs and follow their analysis progress.")
    if not documents:
        st.info("Your library is empty. Upload a PDF from the left panel to begin.")
    else:
        search = st.text_input("Search documents", placeholder="Search by file name…")
        visible = [doc for doc in documents if search.lower() in doc["file_name"].lower()]
        for start in range(0, len(visible), 2):
            cols = st.columns(2)
            for col, doc in zip(cols, visible[start:start + 2]):
                with col:
                    with st.container(border=True):
                        st.markdown(f"### 📄 {doc['file_name']}")
                        st.caption(f"{doc.get('page_count') or 'Page count pending'} pages · {doc.get('created_at', '')}")
                        st.write(f"**Status:** {status_label(doc['status'])}")
                        st.caption(f"Vector index: {status_label(doc.get('vector_status', 'UNKNOWN'))} · Knowledge graph: {status_label(doc.get('graph_status', 'UNKNOWN'))}")
                        if doc.get("warning"):
                            st.warning(doc["warning"])
                        if st.button("Open workspace", key=f"open_library_{doc['document_id']}", use_container_width=True):
                            st.session_state.selected_document = doc["document_id"]
                            st.session_state.pending_page = "AI chat" if is_ready(doc) else "My documents"
                            st.rerun()
        if selected_doc:
            st.divider()
            st.markdown("### Selected document details")
            detail_response = api_request("GET", f"/api/v1/documents/{selected_doc['document_id']}")
            if detail_response.ok:
                detail = detail_response.json()
                st.write(f"**{detail['file_name']}** · {status_label(detail['status'])}")
                if detail["status"] in {"UPLOADED", "EXTRACTING", "INDEXING_VECTOR", "INDEXING_GRAPH", "EXTRACTION_APPROVED_PENDING_INDEX"}:
                    st.info("Analysis is running. Refresh this page shortly to check progress.")
                    if st.button("Refresh status"):
                        st.rerun()
                elif detail["status"] == "EXTRACTION_REVIEW_REQUIRED":
                    st.warning("Please review the extracted passages before indexing.")
                    chunks = api_request("GET", f"/api/v1/documents/{detail['document_id']}/chunks")
                    if chunks.ok:
                        for chunk in chunks.json():
                            with st.expander(f"Page {chunk['page']} · {chunk.get('section') or 'Extracted text'}"):
                                st.write(chunk["text"])
                    accepted = st.checkbox("I reviewed these extracted passages and approve indexing.")
                    if st.button("Approve and continue", type="primary", disabled=not accepted):
                        approval = api_request("POST", f"/api/v1/documents/{detail['document_id']}/approve-extraction")
                        if approval.status_code == 202:
                            st.success("Indexing started.")
                            st.rerun()
                        st.error(response_error(approval))
                elif detail["status"] == "FAILED_RETRYABLE":
                    st.error(detail.get("warning") or "Document analysis failed.")
                    if st.button("Retry analysis", type="primary"):
                        retry = api_request("POST", f"/api/v1/documents/{detail['document_id']}/retry")
                        if retry.ok:
                            st.success("Retry queued.")
                            st.rerun()
                        st.error(response_error(retry))
                else:
                    st.success("Document is ready for questions and summaries.")

elif page == "AI chat":
    st.title("Chat with your PDF")
    st.caption("Ask a question. Answers are grounded in your selected document and include evidence references.")
    if not selected_doc:
        st.info("Upload or select a PDF to start a conversation.")
    elif not is_ready(selected_doc):
        st.warning(f"This document is not ready yet: {status_label(selected_doc['status'])}. Complete processing before chatting.")
    else:
        st.markdown(f"**Current document:** {selected_doc['file_name']}")
        conversation = st.session_state.messages.setdefault(selected_doc["document_id"], [])
        if not conversation:
            st.markdown('<div class="surface"><b>Try asking</b><p class="muted">What is this document about? · List the key findings · Explain the main recommendations · What does page 5 say?</p></div>', unsafe_allow_html=True)
        for message in conversation:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                render_citations(message.get("citations", []))
        question = st.chat_input("Ask a question about this PDF…", max_chars=3000)
        if question:
            conversation.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Searching document evidence and preparing an answer…"):
                    history = [{"role": item["role"], "content": item["content"]} for item in conversation[-8:-1]]
                    try:
                        answer = api_request("POST", "/api/v1/ask", json={
                            "document_id": selected_doc["document_id"], "question": question,
                            "conversation_history": history,
                        })
                        if answer.ok:
                            payload = answer.json()
                            st.markdown(payload["answer"])
                            if payload.get("abstained"):
                                st.info("The document did not provide enough evidence to answer confidently.")
                            render_citations(payload.get("citations", []))
                            if payload.get("retrieval_warnings"):
                                st.warning(" · ".join(payload["retrieval_warnings"]))
                            conversation.append({"role": "assistant", "content": payload["answer"], "citations": payload.get("citations", [])})
                        else:
                            message = response_error(answer)
                            st.error(message)
                            conversation.append({"role": "assistant", "content": f"I couldn't complete that request: {message}"})
                    except requests.RequestException as exc:
                        st.error(f"The API could not be reached: {exc}")
            st.rerun()
        if conversation and st.button("Clear this conversation"):
            st.session_state.messages[selected_doc["document_id"]] = []
            st.rerun()

elif page == "Smart summary":
    st.title("Smart summary")
    st.caption("Generate a source-linked summary of the selected PDF.")
    if not selected_doc:
        st.info("Select a PDF from your library first.")
    elif not is_ready(selected_doc):
        st.warning("Summary generation becomes available after document analysis is complete.")
    else:
        st.markdown(f"**Document:** {selected_doc['file_name']}")
        mode = st.segmented_control("Summary style", ["Executive", "Detailed", "Section"], default="Executive")
        section = st.text_input("Section heading", placeholder="Enter the section heading") if mode == "Section" else None
        if st.button("Generate summary", type="primary", disabled=(mode == "Section" and not section)):
            with st.spinner("Reading the indexed document and preparing a summary…"):
                try:
                    result = api_request("POST", "/api/v1/summaries", json={
                        "document_id": selected_doc["document_id"], "mode": mode.lower(), "section": section,
                    })
                    if result.ok:
                        st.session_state.summaries[f"{selected_doc['document_id']}:{mode}:{section or ''}"] = result.json()
                    else:
                        st.error(response_error(result))
                except requests.RequestException as exc:
                    st.error(f"Summary request failed: {exc}")
        key = f"{selected_doc['document_id']}:{mode}:{section or ''}"
        summary = st.session_state.summaries.get(key)
        if summary:
            st.markdown("### Your summary")
            if summary.get("abstained"):
                st.warning(summary.get("summary", "Not enough evidence to generate a summary."))
            else:
                st.markdown(summary.get("summary", ""))
            render_citations(summary.get("citations", []))
            st.download_button("Download summary as Markdown", summary.get("summary", ""), file_name="pdf-summary.md", mime="text/markdown")

elif page == "Extracted content":
    st.title("Extracted content")
    st.caption("Inspect page-linked passages extracted from your PDF.")
    if not selected_doc:
        st.info("Select a PDF from your library first.")
    else:
        chunks_response = api_request("GET", f"/api/v1/documents/{selected_doc['document_id']}/chunks")
        if chunks_response.ok:
            chunks = chunks_response.json()
            st.metric("Extracted passages", len(chunks))
            query = st.text_input("Find text in extracted passages", placeholder="Search within this document…")
            matches = [chunk for chunk in chunks if query.lower() in chunk.get("text", "").lower()]
            st.caption(f"Showing {len(matches)} of {len(chunks)} passages")
            for chunk in matches:
                with st.expander(f"Page {chunk['page']} · {chunk.get('section') or 'Document text'}"):
                    st.write(chunk["text"])
        else:
            st.error(response_error(chunks_response))

st.divider()
st.caption(f"Guru PDF Intelligence · API {API_BASE} · {datetime.now().strftime('%d %b %Y')}")
