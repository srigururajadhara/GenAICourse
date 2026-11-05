from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Welcome to GenAI Course",
        "status": "API is working successfully"
    }

@app.get("/about")
async def about():
    return {
        "course": "GenAI",
        "topic": "FastAPI"
    }