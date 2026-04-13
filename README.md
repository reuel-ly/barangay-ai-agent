# Barangay AI Assistant — Setup Guide

A RAG (Retrieval-Augmented Generation) chatbot for answering questions about barangay processes in the Philippines. Built with LangChain, ChromaDB, qwen2.5:7b (LLM), and a React frontend.

---
## Tech Stack

| Layer | Technology |
|---|---|
| LLM | qwen2.5:7b — local |
| Embeddings | Ollama (`snowflake-arctic-embed2`) — local |
| Vector DB | ChromaDB — local |
| RAG Framework | LangChain |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Tailwind CSS |
| Knowledge Base | Markdown file |

---

## Project Structure

```
barangay-ai-agent/
├── app.py                  # FastAPI backend
├── data/
│   └── barangay_processes_data.md   # Knowledge base
├── chroma/                 # Vector database (auto-generated)
├── rag/
│   ├── populate_database.py
│   ├── query_data.py
│   ├── get_embedding_function.py
│   └── settings.py
└── frontend/               # React Frontend
    
```

---

## Prerequisites

- Python 3.10+
- Anaconda or `venv`
- Node.js 18+ (for frontend)
- Ollama installed locally — [https://ollama.com](https://ollama.com)

---

## 1. Environment Setup

### Create and activate Conda environment

```bash
conda create -n barangay_rag python=3.11
conda activate barangay_rag
```

### Install Python dependencies

```bash
pip install fastapi uvicorn langchain langchain-community langchain-chroma
pip install langchain-ollama chromadb pymupdf4llm unstructured markdown
```

---

## 2. Configure Settings

Edit `rag/settings.py`:

```python
EMBEDDING_MODEL = "snowflake-arctic-embed2"
LLM_MODEL       = "qwen2.5:7b"   

CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50
K_similarity  = 5


PROMPT_TEXT = """
You are a helpful assistant for barangay residents in the Philippines.
Answer questions about barangay processes such as clearances, certificates,
blotter reports, and dispute resolution (Lupon Tagapamayapa).

IMPORTANT: Always respond in English only. Never use Chinese or any other language.

Use ONLY the information provided in the context below.
If the answer is not found, say:
"I don't have that information. Please visit your barangay hall directly."

Rules:
- Respond in English only
- Be friendly and concise
- Use numbered steps when describing procedures
- List requirements as bullet points
- Always mention processing time and fees if available
- If the user greets you, respond warmly without referencing the context

Context:
{context}

{question}
"""
```

---

## 3. Pull the Embedding Model and LLM Model(Ollama)

The embedding model still runs locally via Ollama.

```bash
ollama pull snowflake-arctic-embed2
```

```bash
ollama pull qwen2.5:7b
```

Verify Ollama is running:

```bash
ollama list
```

---

## 4. Populate the Vector Database

Place your `barangay_processes_data.md` file inside the `/data` folder, then run:

```bash
# First time
python -m rag.populate_database

# Reset and repopulate (if you updated the .md file)
python -m rag.populate_database --reset
```

Expected output:

```
Processing: barangay_processes_data.md
  ✅ Done: barangay_processes_data.md

Total chunks: 24
Avg chunk size: 187 chars
👉 Adding new documents: 24
✅ Documents added successfully
```

---

## 5. Start the Backend

```bash
uvicorn app:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

### Test it with curl

```bash
curl -X POST http://127.0.0.1:8000/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"What is a barangay clearance?\", \"history\": []}"
```

You should get a JSON response with an `answer` field.

---

## 6. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

Open the browser and click the 💬 bubble in the bottom-right corner.

---

## 7. Full Stack (Both at Once)

Open two terminals:

**Terminal 1 — Backend:**
```bash
conda activate barangay_rag
uvicorn app:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```


---

## Updating the Knowledge Base

1. Edit `data/barangay_processes_data.md`
2. Repopulate the database:
   ```bash
   python -m rag.populate_database --reset
   ```
3. Restart the backend — no frontend changes needed

---
