import streamlit as st
import requests
import os

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

st.title("OpenAI Chat Application")

question = st.text_area("Ask your question")

if st.button("Generate Answer"):
    if question.strip():
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": question},
            timeout=60
        )

        if response.ok:
            st.write("### AI Response")
            st.write(response.json()["answer"])
        else:
            st.error(response.text)