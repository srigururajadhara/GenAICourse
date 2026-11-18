import streamlit as st
from dotenv import load_dotenv
from rag.chat import answer_question

load_dotenv()

st.set_page_config(
    page_title="Tamil Nadu Government Schemes Assistant",
    page_icon="🏛️",
    layout="centered"
)

st.title("🏛️ Tamil Nadu Government Schemes Assistant")
st.caption(
    "Ask questions in Tamil or English. Responses are grounded in the official "
    "pages and PDFs that have actually been crawled and indexed."
)
st.info(
    "Coverage depends on the latest crawl and indexed documents. Always verify "
    "important eligibility and application details with the responsible department."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Official sources"):
                for source in message["sources"]:
                    st.markdown(
                        f"- [{source['title']}]({source['url']}) "
                        f"· similarity {source['score']}"
                    )

question = st.chat_input("Ask about schemes, eligibility, benefits or documents...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching indexed government information..."):
            try:
                result = answer_question(question)
                st.markdown(result["answer"])
                if result["sources"]:
                    with st.expander("Official sources"):
                        for source in result["sources"]:
                            st.markdown(
                                f"- [{source['title']}]({source['url']}) "
                                f"· similarity {source['score']}"
                            )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })
            except Exception as exc:
                safe_message = (
                    f"Unable to answer right now: {exc}\n\n"
                    "Check your API key, Neo4j connection, vector index and ingestion report."
                )
                st.error(safe_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": safe_message,
                    "sources": []
                })
