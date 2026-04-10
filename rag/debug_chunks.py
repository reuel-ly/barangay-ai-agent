# debug_chunks.py
import pymupdf4llm
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path

# ── Settings ──────────────────────────────────────────────────
CHUNK_SIZE = 800
CHUNK_OVERLAP = 80
MIN_CHUNK_SIZE = 50

# ── Change this to the PDF you want to inspect ────────────────
PDF_PATH = "data\CBS_MAGNA3_SAMPLE.pdf"


def inspect_pdf_chunks(pdf_path: str):
    print(f"\n{'='*60}")
    print(f"PDF: {pdf_path}")
    print(f"{'='*60}")

    # Step 1: Raw extraction
    pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
    print(f"\nTotal pages extracted: {len(pages)}")

    # Step 2: Show raw page content
    for page in pages:
        print(f"\n{'-'*40}")
        print(f"PAGE {page['metadata']['page']} — raw extracted text:")
        print(f"{'-'*40}")
        print(page["text"][:1000])  # first 1000 chars
        print("...")

    # Step 3: Build documents
    documents = []
    for page in pages:
        content = page["text"].strip()
        if not content:
            continue
        documents.append(Document(
            page_content=content,
            metadata={
                "source": pdf_path,
                "page": page["metadata"]["page"],
                "type": "text"
            }
        ))

    print(f"\nTotal documents (pages) after filtering: {len(documents)}")

    # Step 4: Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)
    chunks = [c for c in chunks if len(c.page_content.strip()) >= MIN_CHUNK_SIZE]

    print(f"Total chunks after splitting: {len(chunks)}")
    print(f"Avg chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")

    # Step 5: Show every chunk
    print(f"\n{'='*60}")
    print("ALL CHUNKS:")
    print(f"{'='*60}")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} | Page {chunk.metadata.get('page')} | {len(chunk.page_content)} chars ---")
        print(chunk.page_content)
        print()


if __name__ == "__main__":
    inspect_pdf_chunks(PDF_PATH)