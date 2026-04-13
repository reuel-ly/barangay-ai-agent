from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag.query_data import query_rag
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []   # ← accept history from frontend

@app.post("/ask")
async def ask(request: QueryRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    return query_rag(request.question, history=history)