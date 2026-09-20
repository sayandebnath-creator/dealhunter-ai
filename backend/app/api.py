from fastapi import FastAPI
from pydantic import BaseModel

from app.main import run_agent


app = FastAPI(
    title="DealHunter AI",
    description="Agentic AI e-commerce assistant",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {
        "message": "DealHunter AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    result = await run_agent(request.message)

    return {
        "response": result
    }