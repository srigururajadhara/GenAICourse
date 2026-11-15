
import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS


# Load API key from the .env file in this project folder
load_dotenv(Path(__file__).resolve().parent / ".env")

# Page configuration
st.set_page_config(
    page_title="Multi-PDF RAG Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Multi-PDF RAG Assistant")
st.write("Upload multiple PDF documents and ask questions across all of them.")

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found. Please check your .env file.")
    st.stop()

# Initialize session state
if "store" not in st.session_state:
    st.session_state.store = None

if "indexed_chunks" not in st.session_state:
    st.session_state.indexed_chunks = 0

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []


# Upload multiple PDFs
st.subheader("1. Upload PDF Documents")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

# Build vector database
if st.button("Build Knowledge Base", disabled=not uploaded_files):

    all_documents = []

    progress = st.progress(0, text="Reading PDF documents...")

    for index, uploaded_file in enumerate(uploaded_files):

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False
            ) as temp_file:

                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name

            try:
                loader = PyPDFLoader(temp_path)
                pages = loader.load()
            finally:
                os.remove(temp_path)

            # Preserve original filename and page metadata
            for page in pages:
                page.metadata["source"] = uploaded_file.name

            all_documents.extend(pages)

        except Exception as error:
            st.error(f"Error reading {uploaded_file.name}: {error}")
            st.stop()

        progress.progress(
            (index + 1) / len(uploaded_files),
            text=f"Reading {uploaded_file.name}..."
        )

    # Split documents into chunks
    st.info("Splitting documents into chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(all_documents)

    if not chunks:
        st.error("No readable text found in the uploaded PDFs.")
        st.stop()

    # Create embeddings and one FAISS vector database
    with st.spinner("Creating embeddings and indexing documents..."):

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )

        st.session_state.store = vector_store
        st.session_state.indexed_chunks = len(chunks)
        st.session_state.indexed_files = [
            file.name for file in uploaded_files
        ]

    progress.progress(1.0, text="Indexing completed!")

    st.success(
        f"Successfully indexed {len(chunks)} chunks "
        f"from {len(uploaded_files)} PDF files!"
    )


# Display indexing information
if st.session_state.store is not None:

    st.divider()

    st.subheader("2. Knowledge Base Status")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Indexed Chunks",
            st.session_state.indexed_chunks
        )

    with col2:
        st.metric(
            "Uploaded PDF Files",
            len(st.session_state.indexed_files)
        )

    with st.expander("View Indexed Documents"):
        for filename in st.session_state.indexed_files:
            st.write(f"📄 {filename}")

    st.divider()

    # Ask questions
    st.subheader("3. Ask Questions Across Your PDFs")

    question = st.text_input(
        "Enter your question",
        placeholder="Example: What is the main topic discussed in these documents?"
    )

    if st.button("Get Answer", disabled=not question.strip()):

        with st.spinner("Searching documents and generating answer..."):

            # Retrieve relevant document chunks
            retrieved_docs = st.session_state.store.similarity_search(
                question,
                k=4
            )

            # Prepare context with source information
            context_parts = []

            for doc in retrieved_docs:

                filename = doc.metadata.get("source", "Unknown file")
                page_number = doc.metadata.get("page")

                if page_number is not None:
                    page_number = int(page_number) + 1
                else:
                    page_number = "Unknown"

                context_parts.append(
                    f"[Source: {filename}, Page: {page_number}]\n"
                    f"{doc.page_content}"
                )

            context = "\n\n".join(context_parts)

            # Ask the LLM to answer using retrieved context
            prompt = f"""
You are a helpful PDF document assistant.

Answer the user's question using ONLY the supplied document context.

If the information is not available, clearly say:
"The uploaded documents do not contain enough information to answer."

If two documents disagree:
- Explain the disagreement.
- Present both statements separately.
- Mention the source file and page for each statement.
- Do not silently choose one statement as correct.

Include source citations in your answer using:
[filename, page number]

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0
            )

            response = llm.invoke(prompt)

        # Display answer
        st.subheader("Answer")
        st.markdown(response.content)

        # Display sources from metadata
        st.subheader("Sources")

        displayed_sources = set()

        for doc in retrieved_docs:

            filename = doc.metadata.get("source", "Unknown file")
            page = doc.metadata.get("page")

            page_number = int(page) + 1 if page is not None else "Unknown"

            source_key = (filename, page_number)

            if source_key not in displayed_sources:

                displayed_sources.add(source_key)

                st.caption(
                    f"📄 {filename} — Page {page_number}"
                )

else:
    st.info("Upload PDF files and build your knowledge base to begin.")
