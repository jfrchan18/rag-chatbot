# backend/app/db.py
import os
import time
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from pgvector.psycopg import register_vector, Vector

# Global connection
_conn: psycopg.Connection | None = None


def init_db(retries: int = 10, delay: int = 3) -> None:
    """
    Connect to Postgres using env vars and ensure pgvector is enabled.
    Retries while the DB container is starting up.
    """
    load_dotenv()
    global _conn
    last_err: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            _conn = psycopg.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                dbname=os.getenv("POSTGRES_DB", "ragdb"),
                user=os.getenv("POSTGRES_USER", "rag"),
                password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
                autocommit=True,
                row_factory=dict_row,
            )
            register_vector(_conn)  # ✅ makes psycopg handle `vector` type
            with _conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ Connected to Postgres and pgvector is ready.")
            return
        except Exception as e:
            last_err = e
            print(f"DB connection failed ({e}); retrying in {delay}s... [{attempt}/{retries}]")
            time.sleep(delay)

    raise RuntimeError(f"❌ Could not connect to Postgres after retries: {last_err}")


def run_schema() -> None:
    """Execute schema.sql (idempotent)."""
    schema_path = Path(__file__).with_name("schema.sql")
    sql = schema_path.read_text()
    with _conn.cursor() as cur:
        cur.execute(sql)
    print("✅ Schema ensured.")


def conn() -> psycopg.Connection:
    if _conn is None:
        raise RuntimeError("❌ Database not initialized. Call init_db() first.")
    return _conn


# ----------------------------
# Documents
# ----------------------------
def insert_document(doc_name: str) -> int:
    with _conn.cursor() as cur:
        cur.execute(
            "INSERT INTO documents (doc_name) VALUES (%s) RETURNING id;",
            (doc_name,),
        )
        return cur.fetchone()["id"]


def count_documents() -> int:
    with _conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM documents;")
        return cur.fetchone()["c"]


# ----------------------------
# Chunks
# ----------------------------
def insert_chunk(doc_id: int, content: str, embedding: list[float]) -> int:
    with _conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chunks (doc_id, content, embedding)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (doc_id, content, embedding),   # ✅ pass embedding directly
        )
        return cur.fetchone()["id"]


def search_chunks(query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
    with _conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, doc_id, content, (embedding <=> %s::vector) AS distance
            FROM chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (Vector(query_embedding), Vector(query_embedding), top_k),
        )
        rows = cur.fetchall()
    return rows




# ----------------------------
# Chat history
# ----------------------------
def insert_chat(session_id: str, role: str, message: str) -> int:
    with _conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chat_history (session_id, role, message)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (session_id, role, message),
        )
        return cur.fetchone()["id"]


def get_chat_history(session_id: str) -> list[dict[str, Any]]:
    with _conn.cursor() as cur:
        cur.execute(
            """
            SELECT role, message, created_at
            FROM chat_history
            WHERE session_id = %s
            ORDER BY created_at ASC;
            """,
            (session_id,),
        )
        return cur.fetchall()
