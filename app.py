from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag.query_data import query_rag
from router_agent.router_agent import detect_intent
from calendar_agent.calendar_agent import handle_calendar
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
    history: Optional[List[Message]] = []

@app.post("/ask")
async def ask(request: QueryRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]

    # Detect intent
    intent = detect_intent(request.question)

    # Route to the right agent
    if intent == "calendar":
        response = await handle_calendar(request.question, history=[])
    else:
        response = query_rag(request.question, history=history)

    # Return with intent label (useful for debugging / frontend)
    return {
        **response,               # keeps whatever query_rag already returns
        "intent": intent          # adds intent so frontend knows what happened
    }