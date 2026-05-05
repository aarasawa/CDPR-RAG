import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pypdf import PdfReader

# --- Config ---
DOCS_DIR = Path(__file__).parent.parent / "docs"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "cdpr_docs"
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50

embedding_fn = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

def extract_text(filepath: Path) -> str:
    """Extract raw text from PDF or TXT file."""
    if filepath.suffix == ".pdf":
        reader = PdfReader(str(filepath))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif filepath.suffix == ".txt":
        return filepath.read_text(encoding="utf-8")
    return ""

def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def ingest():
    docs = list(DOCS_DIR.glob("*.pdf")) + list(DOCS_DIR.glob("*.txt"))
    if not docs:
        print(f"No documents found in {DOCS_DIR}")
        return

    for filepath in docs:
        print(f"Processing: {filepath.name}")
        text = extract_text(filepath)
        chunks = chunk_text(text)

        ids = [f"{filepath.stem}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filepath.name, "chunk": i} for i in range(len(chunks))]

        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        print(f"  → Added {len(chunks)} chunks")

    print(f"\nDone. Collection has {collection.count()} total chunks.")

if __name__ == "__main__":
    ingest()