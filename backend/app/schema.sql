-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents that were uploaded
CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  doc_name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks + embeddings (1536 dims matches text-embedding-3-small)
CREATE TABLE IF NOT EXISTS chunks (
  id SERIAL PRIMARY KEY,
  doc_id INT REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding VECTOR(1536) NOT NULL
);

-- Speed up vector search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding
ON chunks USING ivfflat (embedding vector_cosine_ops);

-- Chat history by session
CREATE TABLE IF NOT EXISTS chat_history (
  id SERIAL PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user','assistant')),
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
