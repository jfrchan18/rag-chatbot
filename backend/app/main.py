# backend/app/main.py
from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import db
from app.embeddings import embed_text
from app.pdf_processor import process_pdf_for_rag


# ----------------------------
# App
# ----------------------------
app = FastAPI(title="RAG Backend", version="0.1.0")

# CORS (add/remove origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",   # simple static frontend (python -m http.server)
        "http://127.0.0.1:5500",
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "null",                    # file:// protocol (for local HTML files)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Lifecycle
# ----------------------------
@app.on_event("startup")
def _startup():
    db.init_db()
    db.run_schema()


# ----------------------------
# Health
# ----------------------------
@app.get("/health")
def health():
    try:
        doc_count = db.count_documents()
    except Exception:
        doc_count = None
    return {"ok": True, "service": "api", "version": "0.1.0", "documents": doc_count}


@app.delete("/reset-database")
def reset_database():
    """Reset the entire database - delete all documents and chunks."""
    try:
        with db.conn().cursor() as cur:
            # Delete all chunks first (due to foreign key constraint)
            cur.execute("DELETE FROM chunks;")
            # Delete all documents
            cur.execute("DELETE FROM documents;")
            # Delete all chat history
            cur.execute("DELETE FROM chat_history;")
        
        return {
            "message": "Database reset successfully",
            "documents_deleted": True,
            "chunks_deleted": True,
            "chat_history_deleted": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database reset error: {e}")


# ----------------------------
# Request Models
# ----------------------------
class DocumentIn(BaseModel):
    doc_name: str = Field(..., min_length=1)


class ChunkIn(BaseModel):
    doc_id: int
    content: str = Field(..., min_length=1)
    embedding: List[float]  # 1536-d for text-embedding-3-small


class SearchIn(BaseModel):
    embedding: List[float]
    top_k: int = Field(5, ge=1, le=50)


class ChatIn(BaseModel):
    session_id: str
    role: str  # "user" or "assistant"
    message: str


class EmbedAndChunkIn(BaseModel):
    doc_id: int
    content: str = Field(..., min_length=1)


class AskIn(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(4, ge=1, le=20)


class SearchTextIn(BaseModel):
    text: str
    top_k: int = Field(5, ge=1, le=50)


# ----------------------------
# Retrieval-only (vector search)
# ----------------------------
@app.post("/search-text")
def search_text(body: SearchTextIn):
    try:
        qvec = embed_text(body.text)
        results = db.search_chunks(qvec, top_k=body.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/search-text error: {e}")


@app.post("/search")
def search_chunks(body: SearchIn):
    try:
        results = db.search_chunks(body.embedding, top_k=body.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/search error: {e}")


# ----------------------------
# Documents & Chunks
# ----------------------------
@app.post("/documents")
def create_document(body: DocumentIn):
    try:
        doc_id = db.insert_document(body.doc_name)
        return {"doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/documents error: {e}")


@app.post("/chunks")
def create_chunk(body: ChunkIn):
    try:
        chunk_id = db.insert_chunk(body.doc_id, body.content, body.embedding)
        return {"chunk_id": chunk_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/chunks error: {e}")


@app.post("/embed-and-chunk")
def embed_and_chunk(body: EmbedAndChunkIn):
        # embed text server-side, then insert
    try:
        vec = embed_text(body.content)  # 1536-d vector
        chunk_id = db.insert_chunk(body.doc_id, body.content, vec)
        return {"chunk_id": chunk_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/embed-and-chunk error: {e}")


# ----------------------------
# Chat history
# ----------------------------
@app.post("/chat")
def add_chat(body: ChatIn):
    role = body.role.lower()
    if role not in ("user", "assistant"):
        raise HTTPException(status_code=400, detail="role must be 'user' or 'assistant'")
    try:
        chat_id = db.insert_chat(body.session_id, role, body.message)
        return {"chat_id": chat_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/chat error: {e}")


@app.get("/chat/{session_id}")
def get_chat(session_id: str):
    try:
        history = db.get_chat_history(session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/chat/{session_id} error: {e}")


# ----------------------------
# Ask (RAG: retrieve + generate)
# ----------------------------
def _get_openai_client():
    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=key)


@app.post("/ask")
def ask(body: AskIn):
    # 1) Embed the question
    qvec = embed_text(body.question)
    hits = db.search_chunks(qvec, top_k=body.top_k)

    # 2) Return early if nothing found
    if not hits:
        return {"answer": "I don't know based on the current knowledge base.", "sources": []}

    # 3) Build context
    context = "\n\n".join(f"- {h['content']}" for h in hits)

    # 4) Call LLM
    client = _get_openai_client()
    chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    system_msg = (
        "You are a helpful assistant. Use ONLY the provided context to answer. "
        "If the answer is not in the context, say you don't know."
    )
    user_msg = f"Context:\n{context}\n\nQuestion: {body.question}\nAnswer:"

    try:
        resp = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        choice = resp.choices[0] if resp.choices else None
        answer = getattr(choice.message, "content", None) if choice else None
        if not answer and choice and isinstance(choice.message, dict):
            answer = choice.message.get("content")
        if not answer:
            answer = "⚠️ No content returned from model."
        return {"answer": answer, "sources": hits}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")


# ----------------------------
# Debug route (retrieval only)
# ----------------------------
@app.post("/ask-debug")
def ask_debug(body: AskIn):
    try:
        qvec = embed_text(body.question)   # embeds the query
        hits = db.search_chunks(qvec, top_k=body.top_k)
        context = "\n\n".join(f"- {h['content']}" for h in hits)
        return {"hits": hits, "context": context}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"ask-debug error: {e}")


# ----------------------------
# PDF Upload
# ----------------------------
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file for RAG.
    
    The PDF will be:
    1. Extracted for text content
    2. Chunked into smaller pieces
    3. Embedded using OpenAI
    4. Stored in the vector database
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        pdf_bytes = await file.read()
        
        # Process PDF (extract text and create chunks)
        extracted_text, chunks = process_pdf_for_rag(pdf_bytes, file.filename)
        
        # Create document record
        doc_id = db.insert_document(file.filename)
        
        # Process each chunk
        chunk_ids = []
        for chunk in chunks:
            # Generate embedding for the chunk
            embedding = embed_text(chunk.page_content)
            
            # Store chunk in database
            chunk_id = db.insert_chunk(doc_id, chunk.page_content, embedding)
            chunk_ids.append(chunk_id)
        
        return {
            "message": "PDF uploaded and processed successfully",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_created": len(chunk_ids),
            "text_length": len(extracted_text),
            "chunk_ids": chunk_ids
        }
        
    except ValueError as e:
        # PDF processing errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Other errors
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF upload error: {e}")
