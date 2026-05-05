import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "cdpr_docs"
TOP_K = 5  # number of chunks to retrieve

embedding_fn = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/health")
def health():
    return {"status": "ok", "chunks": collection.count()}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    # Retrieve relevant chunks
    results = collection.query(
        query_texts=[req.question],
        n_results=TOP_K
    )

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context string
    context = "\n\n---\n\n".join(
        f"[Source: {m['source']}, chunk {m['chunk']}]\n{doc}"
        for doc, m in zip(chunks, metadatas)
    )

    # Build prompt
    prompt = f"""You are a helpful assistant that answers questions about California pesticide regulations.
Use only the context below to answer. If the answer isn't in the context, say so clearly.
Always mention which source your answer comes from.

Context:
{context}

Question: {req.question}

Answer:"""

    message = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = message.content[0].text
    sources = list(set(m["source"] for m in metadatas))

    return QueryResponse(answer=answer, sources=sources)