"""Extract and chunk MUDRA and Stand-Up India documents."""

import re
from pathlib import Path

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    text = " ".join(text.split())

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def load_mudra_ocr():
    """Read OCR text while preserving original PDF page numbers."""
    ocr_path = RAW_DIR / "pmmy_ocr.txt"

    if not ocr_path.exists():
        print("Warning: pmmy_ocr.txt not found")
        return []

    text = ocr_path.read_text(encoding="utf-8")

    pages = re.split(r"--- PAGE (\d+) ---", text)
    documents = []

    title = "Guide to MUDRA Loans for Homestays - September 2025"

    for i in range(1, len(pages), 2):
        page_number = int(pages[i])
        page_text = pages[i + 1].strip()

        for chunk_number, chunk in enumerate(
            split_text(page_text), start=1
        ):
            documents.append({
                "id": f"pmmy_faq_page_{page_number}_chunk_{chunk_number}",
                "text": chunk,
                "source": "pmmy_faq.pdf",
                "page": page_number,
                "title": title,
            })

    return documents


def load_standup_pdf():
    """Extract text from the Stand-Up India PDF."""
    pdf_path = RAW_DIR / "standup_faq.pdf"

    if not pdf_path.exists():
        print("Warning: standup_faq.pdf not found")
        return []

    reader = PdfReader(str(pdf_path))
    documents = []

    title = "Frequently Asked Questions - Stand Up India Scheme"

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        for chunk_number, chunk in enumerate(
            split_text(page_text), start=1
        ):
            documents.append({
                "id": f"standup_faq_page_{page_number}_chunk_{chunk_number}",
                "text": chunk,
                "source": "standup_faq.pdf",
                "page": page_number,
                "title": title,
            })

    return documents


def load_documents():
    """Load chunks from all supported documents."""
    documents = []
    documents.extend(load_mudra_ocr())
    documents.extend(load_standup_pdf())
    return documents


if __name__ == "__main__":
    chunks = load_documents()

    print("Total chunks:", len(chunks))

    sources = {}

    for chunk in chunks:
        sources[chunk["source"]] = sources.get(chunk["source"], 0) + 1

    print("Chunks by source:", sources)

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0])

        print("\nLast chunk:")
        print(chunks[-1])
