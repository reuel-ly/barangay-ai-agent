import json
import os
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from pathlib import Path
from datasets import Dataset
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import OllamaEmbeddings
import numpy as np

from rag.settings import LLM_MODEL, EMBEDDING_MODEL, K_similarity, PROMPT_TEXT
from rag.get_embedding_function import get_embedding_function

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma"
CONVERSATION_FILE = "conversation_history.json"
MAX_HISTORY = 6  # last 3 exchanges
PROMPT_TEXT = PROMPT_TEXT

EVAL_FILE = "rag/eval_data.json"

# ─── Conversation Persistence ─────────────────────────────────
def load_history() -> list:
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r') as f:
            history = json.load(f)
        print(f"[Resuming previous conversation — {len(history)} messages]\n")
        return history
    return []


def save_history(history: list):
    with open(CONVERSATION_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def clear_history() -> list:
    if os.path.exists(CONVERSATION_FILE):
        os.remove(CONVERSATION_FILE)
    print("[Conversation cleared]\n")
    return []


# ─── RAG ──────────────────────────────────────────────────────
def query_rag(query_text: str, history: list) -> dict:
    print("Answering Question...")
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function
    )

    results = db.similarity_search_with_score(query_text, k=K_similarity)

    context_parts = []
    retrieved_texts = []
    
    for doc, score in results:
        chunk_type = doc.metadata.get("type", "text").upper()
        context_parts.append(f"[{chunk_type}]\n{doc.page_content}")
        retrieved_texts.append(doc.page_content)
    context_text = "\n\n---\n\n".join(context_parts)

    # Build history text from last MAX_HISTORY messages
    history_text = ""
    if history:
        lines = []
        for msg in history[-MAX_HISTORY:]:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        history_text = "Previous conversation:\n" + "\n".join(lines) + "\n\n"

    prompt_template = PromptTemplate(
        template=PROMPT_TEXT,
        input_variables=["context", "question"]
    )
    prompt = prompt_template.format(
        context=context_text,
        question=f"{history_text}Current question: {query_text}"
    )

    model = OllamaLLM(model=LLM_MODEL)
    response_text = model.invoke(prompt)

    sources = [
    {
        "id":     doc.metadata.get("id"),
        "score":  round(score, 4),
        "page":   doc.metadata.get("page"),
        "source": os.path.basename(doc.metadata.get("source", ""))
    }
    for doc, score in results
]

    return {"answer": response_text, "sources": sources, "retrieved_texts": retrieved_texts}

def save_result(question: str, answer: str, contexts: list):
    """Appends each Q&A turn to eval_data.json for later RAGAS evaluation."""
    existing = []
    if os.path.exists(EVAL_FILE):
        with open(EVAL_FILE, 'r') as f:
            existing = json.load(f)

    existing.append({
        "question": question,
        "answer":   answer,
        "contexts": contexts      # list of retrieved chunk texts
    })

    with open(EVAL_FILE, 'w') as f:
        json.dump(existing, f, indent=2)

# ─── Main Loop ────────────────────────────────────────────────
def run():
    history = load_history()

    print("Grundfos RAG Assistant")
    print("Ask me anything about Grundfos pumps.")
    print("Type 'exit' to quit, 'clear' to start a new conversation.\n")

    while True:
        query_text = input("You: ").strip()

        if query_text.lower() == 'exit':
            save_history(history)
            print("Goodbye!")
            break

        if query_text.lower() == 'clear':
            history = clear_history()
            continue

        if not query_text:
            continue

        result = query_rag(query_text, history)

        history.append({"role": "user",      "content": query_text})
        history.append({"role": "assistant", "content": result["answer"]})
        save_history(history)

        # ← Save to eval file for later RAGAS processing
        save_result(
            question=query_text,
            answer=result["answer"],
            contexts=result["retrieved_texts"]
        )

        print(f"\nAgent: {result['answer']}")
        print("\nSources:")
        for s in result["sources"]:
            print(f"  Score: {s['score']:.4f} | Page: {s['page']} | File: {s['source']}")
        print()


if __name__ == "__main__":
    run()