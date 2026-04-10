import argparse
import os
import shutil
import re                          # ← add this import
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from pathlib import Path
import pymupdf4llm

# Local Imports
from get_embedding_function import get_embedding_function
from settings import CHUNK_SIZE, CHUNK_OVERLAP

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

def clean_content(text: str) -> str:
    """Remove entire lines containing noise patterns."""

    # Each pattern removes the whole line it matches
    noise_lines = [
        r".*\*\*Company name:\*\*.*",
        r".*\*\*Created by:\*\*.*",
        r".*\*\*Phone:\*\*.*",
        r".*\*\*Date:\*\*.*",
        r".*\*\*Qty\.\*\*.*",
        r".*\*\*Note!.*",
        r".*Printed from Grundfos.*",
        r".*Pumped liquid = Water.*",
        r".*Density = .*kg/m.*",
        r".*Liquid temperature during operation.*",
        r".*Example of mains-connected motor.*",
        r".*with mains switch.*",
    ]
    for pattern in noise_lines:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # Remove graph axis number sequences
    text = re.sub(r"^(\*\*\d+\*\*\s*){3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^(\d+\s*){4,}$", "", text, flags=re.MULTILINE)

    # Remove graph axis labels
    text = re.sub(r".*eta\s*\[%\].*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r".*H\s*\[m\].*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r".*P1\s*\[\w+\].*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r".*Q\s*\[m[³3]/h\].*", "", text, flags=re.IGNORECASE | re.MULTILINE)

    # Remove empty markdown table rows
    text = re.sub(r"(\|\s*\|)+", "", text)
    text = re.sub(r"^\|[-| ]+\|$", "", text, flags=re.MULTILINE)

    # Remove connector pressure labels
    text = re.sub(r".*PN\s*\d+/?\d*.*", "", text, flags=re.MULTILINE)

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

# ── Update load_documents to use clean_content ────────────────
def load_documents(data_path: str) -> list[Document]:
    documents = []

    for filename in os.listdir(data_path):
        if not filename.endswith('.pdf'):
            continue

        pdf_path = os.path.join(data_path, filename)
        product_name = filename.replace(".pdf", "").replace("_", " ")
        print(f"Processing: {filename}")

        pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
        first_page_content = ""

        for page in pages:
            content = page["text"].strip()
            if not content:
                continue

            # ← Clean noise before storing
            content = clean_content(content)

            if len(content) < 50:
                print(f"  ⏭ Skipping page {page['metadata']['page']} (too short after cleaning)")
                continue

            page_num = page["metadata"]["page"]

            if page_num == 1:
                first_page_content = content
                content_with_context = f"Product: {product_name}\n\n{content}"
            else:
                # Spec pages — label clearly so embedding finds them
                content_with_context = f"""Product: {product_name}
Specification sheet for {product_name}

{content}"""

            documents.append(Document(
                page_content=content_with_context,
                metadata={
                    "source":  pdf_path,
                    "page":    page_num,
                    "type":    "text",
                    "product": product_name
                }
            ))

        print(f"  ✅ Done: {filename} — {len(pages)} pages")

    print(f"\n✅ Loaded {len(documents)} documents")
    return documents


# ── Everything below unchanged ────────────────────────────────
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    split_texts = text_splitter.split_documents(documents)
    MIN_CHUNK_SIZE = 50
    split_texts = [chunk for chunk in split_texts if len(chunk.page_content.strip()) >= MIN_CHUNK_SIZE]
    return split_texts


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