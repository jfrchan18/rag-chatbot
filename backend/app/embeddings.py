# app/embeddings.py
import os
from openai import OpenAI

_client_instance = None
EMBED_MODEL = "text-embedding-3-small"  # 1536 dims

def get_client() -> OpenAI:
    """Return a cached OpenAI client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client_instance

def embed_text(text: str) -> list[float]:
    """Embed a single text string and return the vector."""
    resp = get_client().embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding
