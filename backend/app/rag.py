import os
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.documents import Document

COLLECTION = "docs"

def _pg_conn_str():
    user = os.getenv("POSTGRES_USER", "rag")
    pwd = os.getenv("POSTGRES_PASSWORD", "ragpass")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db   = os.getenv("POSTGRES_DB", "ragdb")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

def get_vectorstore():
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        api_key=os.getenv("OPENAI_API_KEY", "")
    )
    return PGVector(
        connection_string=_pg_conn_str(),
        collection_name=COLLECTION,
        embedding_function=embeddings,
        use_jsonb=True,
    )

def ingest_folder(path="data") -> int:
    p = Path(path)
    texts = []
    for f in p.rglob("*"):
        if f.suffix.lower() in {".txt", ".md"}:
            try:
                texts.append(Document(
                    page_content=f.read_text(encoding="utf-8", errors="ignore"),
                    metadata={"source": str(f)}
                ))
            except Exception as e:
                print(f"⚠️ Skipped {f}: {e}")
    if not texts:
        print("No documents found for ingestion.")
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(texts)

    vs = get_vectorstore()
    vs.add_documents(chunks)

    print(f"✅ Ingested {len(chunks)} chunks from {len(texts)} files.")
    return len(chunks)

def make_chain():
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful RAG assistant. Use the context to answer. "
                   "If the answer is not in the context, say you don't know."),
        ("human", "Question: {question}\n\nContext:\n{context}")
    ])

    k = int(os.getenv("TOP_K", 4))
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": k})

    inputs = {"context": retriever, "question": RunnablePassthrough()}
    return RunnableParallel(**inputs) | prompt | llm
