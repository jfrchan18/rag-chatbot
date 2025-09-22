#!/usr/bin/env python3
"""
Test script for PDF upload functionality.
This script tests the PDF upload endpoint without requiring the full Docker setup.
"""

import requests
import json
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "test_sample.pdf"

def test_health():
    """Test if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            data = response.json()
            print(f"   Documents in database: {data.get('documents', 'Unknown')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on localhost:8000")
        return False

def create_test_pdf():
    """Create a simple test PDF file."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(TEST_PDF_PATH, pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "Sample PDF Document")
        c.drawString(100, 700, "This is a test document for the RAG chatbot.")
        c.drawString(100, 650, "It contains information about artificial intelligence.")
        c.drawString(100, 600, "AI is transforming many industries including healthcare, finance, and education.")
        
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "Page 2: Machine Learning")
        c.drawString(100, 700, "Machine learning is a subset of artificial intelligence.")
        c.drawString(100, 650, "It enables computers to learn without being explicitly programmed.")
        c.drawString(100, 600, "Common applications include image recognition, natural language processing, and recommendation systems.")
        
        c.save()
        print(f"✅ Created test PDF: {TEST_PDF_PATH}")
        return True
        
    except ImportError:
        print("⚠️  reportlab not installed. Creating a simple text file instead.")
        with open(TEST_PDF_PATH.replace('.pdf', '.txt'), 'w') as f:
            f.write("Sample Document\n\n")
            f.write("This is a test document for the RAG chatbot.\n")
            f.write("It contains information about artificial intelligence.\n")
            f.write("AI is transforming many industries including healthcare, finance, and education.\n\n")
            f.write("Machine Learning\n\n")
            f.write("Machine learning is a subset of artificial intelligence.\n")
            f.write("It enables computers to learn without being explicitly programmed.\n")
            f.write("Common applications include image recognition, natural language processing, and recommendation systems.\n")
        print("✅ Created test text file (rename to .pdf for actual PDF testing)")
        return False

def test_pdf_upload():
    """Test PDF upload endpoint."""
    if not Path(TEST_PDF_PATH).exists():
        print("❌ Test PDF not found. Run create_test_pdf() first.")
        return False
    
    try:
        with open(TEST_PDF_PATH, 'rb') as f:
            files = {'file': (TEST_PDF_PATH, f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload-pdf", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PDF upload successful!")
            print(f"   Document ID: {data.get('doc_id')}")
            print(f"   Filename: {data.get('filename')}")
            print(f"   Chunks created: {data.get('chunks_created')}")
            print(f"   Text length: {data.get('text_length')}")
            return True
        else:
            print(f"❌ PDF upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PDF upload error: {e}")
        return False

def test_ask_question():
    """Test asking a question about the uploaded PDF."""
    questions = [
        "What is artificial intelligence?",
        "What are some applications of machine learning?",
        "What industries is AI transforming?"
    ]
    
    for question in questions:
        try:
            response = requests.post(f"{API_BASE_URL}/ask", 
                json={"question": question, "top_k": 4})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Question: {question}")
                print(f"   Answer: {data.get('answer', 'No answer')[:100]}...")
                print(f"   Sources found: {len(data.get('sources', []))}")
            else:
                print(f"❌ Question failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Question error: {e}")

def cleanup():
    """Clean up test files."""
    if Path(TEST_PDF_PATH).exists():
        os.remove(TEST_PDF_PATH)
        print(f"🧹 Cleaned up {TEST_PDF_PATH}")

if __name__ == "__main__":
    print("🧪 Testing PDF Upload Functionality")
    print("=" * 40)
    
    # Test API health
    if not test_health():
        print("\n❌ API is not running. Please start the backend first:")
        print("   docker-compose up --build")
        exit(1)
    
    # Create test PDF
    pdf_created = create_test_pdf()
    
    if pdf_created:
        # Test PDF upload
        print("\n📤 Testing PDF Upload...")
        if test_pdf_upload():
            # Test questions
            print("\n❓ Testing Questions...")
            test_ask_question()
    
    # Cleanup
    cleanup()
    
    print("\n🎉 Test completed!")
