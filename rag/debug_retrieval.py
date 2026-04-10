# debug_retrieval.py
from langchain_chroma import Chroma
from pathlib import Path
from get_embedding_function import get_embedding_function

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma"

# Step 1: Check if chroma folder exists
print(f"Chroma path: {CHROMA_PATH}")
print(f"Chroma exists: {CHROMA_PATH.exists()}")

db = Chroma(
    persist_directory=str(CHROMA_PATH),
    embedding_function=get_embedding_function()
)

# Step 2: Check total documents in DB
total = db.get(include=[])
print(f"Total chunks in DB: {len(total['ids'])}")

# Step 3: Print first 3 IDs to confirm what's stored
print("\nSample IDs in DB:")
for id in total['ids'][:3]:
    print(f"  {id}")

# Step 4: Try the search
print("\n--- Retrieval Debug ---")
results = db.similarity_search_with_score("MAGNA1 flow rate m3/h", k=10)
print(f"Results returned: {len(results)}")

results = [(doc, 1 - score) for doc, score in results]
results = sorted(results, key=lambda x: x[1], reverse=True)

top_3 = results[:3]

for doc, score in top_3:
    print(f"\nScore: {score:.4f} | Page: {doc.metadata.get('page')} | Source: {doc.metadata.get('source')}")
    print(doc.page_content[:300])
    print("...")