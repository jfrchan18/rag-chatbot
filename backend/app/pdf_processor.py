# backend/app/pdf_processor.py
import io
from typing import List, Tuple
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text content from PDF bytes.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        
    Returns:
        Extracted text content as string
    """
    try:
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        
        text_content = []
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")
            except Exception as e:
                print(f"⚠️ Error extracting page {page_num}: {e}")
                continue
        
        if not text_content:
            raise ValueError("No text content found in PDF")
            
        return "\n\n".join(text_content)
        
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")


def chunk_pdf_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> List[Document]:
    """
    Split PDF text into chunks for embedding.
    
    Args:
        text: Full text content from PDF
        chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between chunks
        
    Returns:
        List of Document objects ready for embedding
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Create a single document for splitting
    doc = Document(page_content=text, metadata={"source": "uploaded_pdf"})
    chunks = splitter.split_documents([doc])
    
    return chunks


def process_pdf_for_rag(pdf_bytes: bytes, doc_name: str) -> Tuple[str, List[Document]]:
    """
    Complete PDF processing pipeline: extract text and create chunks.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        doc_name: Name for the document
        
    Returns:
        Tuple of (extracted_text, chunks)
    """
    # Extract text
    extracted_text = extract_text_from_pdf(pdf_bytes)
    
    # Create chunks
    chunks = chunk_pdf_text(extracted_text)
    
    # Add document metadata to chunks
    for chunk in chunks:
        chunk.metadata.update({
            "doc_name": doc_name,
            "source_type": "pdf_upload"
        })
    
    return extracted_text, chunks
