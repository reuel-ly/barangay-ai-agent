import argparse
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter

# Local Imports
from rag.get_embedding_function import get_embedding_function
from rag.settings import CHUNK_SIZE, CHUNK_OVERLAP

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma"
DATA_PATH = BASE_DIR / "data"


def init_database():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_documents(DATA_PATH)
    chunks = split_documents(documents)
    inspect_chunks(chunks)
    add_to_chroma(chunks)



# ── Update load_documents to use clean_content ────────────────
def load_documents(data_path: str) -> list[Document]:
    documents = []

    for filename in os.listdir(data_path):
        if not filename.endswith('.md'):
            continue

        md_path = os.path.join(data_path, filename)
        source_name = filename.replace(".md", "").replace("_", " ")
        print(f"Processing: {filename}")

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc = Document(
            page_content=content,
            metadata={
                "source": md_path,
                "page": 0,
                "product_name": source_name,
                "type": "text",
            }
        )
        documents.append(doc)

        print(f"  ✅ Done: {filename}")

    print(f"\n✅ Loaded {len(documents)} documents")
    return documents

# ── Everything below unchanged ────────────────────────────────
from langchain_text_splitters import MarkdownHeaderTextSplitter

def split_documents(documents: list[Document]):
    headers_to_split_on = [
        ("#",  "section"),
        ("##", "process"),
        ("###","subsection"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )

    all_chunks = []
    for doc in documents:
        splits = md_splitter.split_text(doc.page_content)
        for i, split in enumerate(splits):
            # Carry over parent metadata
            split.metadata.update({
                "source": doc.metadata.get("source"),
                "page":   i,
                "type":   "text",
            })
            all_chunks.append(split)

    # Filter out tiny chunks
    all_chunks = [c for c in all_chunks if len(c.page_content.strip()) >= 50]
    return all_chunks


def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=get_embedding_function(),
    )
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = [
        chunk for chunk in chunks_with_ids
        if chunk.metadata["id"] not in existing_ids
    ]

    if new_chunks:
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        print("✅ Documents added successfully")
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks: list[Document]):
    page_id_counts = {}
    for chunk in chunks:
        source     = chunk.metadata.get("source")
        page       = chunk.metadata.get("page")
        chunk_type = chunk.metadata.get("type", "text")
        page_id    = f"{source}:{page}:{chunk_type}"
        current_index = page_id_counts.get(page_id, 0)
        chunk.metadata["id"] = f"{page_id}:{current_index}"
        page_id_counts[page_id] = current_index + 1
    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print("🗑 Database cleared")    


def inspect_chunks(chunks: list[Document], sample_size: int = 5):
    if not chunks:
        print("⚠️ No chunks to inspect")
        return
    print(f"\nTotal chunks: {len(chunks)}")
    print(f"Avg chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")
    print(f"\n--- Sample Chunks ---")
    for i, chunk in enumerate(chunks[:sample_size]):
        print(f"\nChunk {i+1} | Page: {chunk.metadata.get('page')} | Size: {len(chunk.page_content)} chars")
        print(chunk.page_content[:200])
        print("...")


if __name__ == "__main__":
    init_database()