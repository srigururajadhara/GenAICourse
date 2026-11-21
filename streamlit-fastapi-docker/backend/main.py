
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI(title="OpenAI Chat API")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "OpenAI FastAPI backend is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = client.responses.create(
            model=MODEL,
            input=request.message
        )

        return {
            "question": request.message,
            "answer": response.output_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
