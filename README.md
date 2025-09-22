# RAG Chatbot with PDF Upload

A Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents and ask questions about their content. Built with FastAPI, PostgreSQL + pgvector, OpenAI, and a modern React frontend.

## Features

- 📄 **PDF Upload**: Upload PDF documents for analysis
- 🤖 **RAG Chat**: Ask questions about uploaded PDFs using OpenAI GPT-4o-mini
- 🔍 **Vector Search**: Uses pgvector for efficient similarity search
- 💾 **Chat History**: Persistent conversation history stored in PostgreSQL
- 🐳 **Dockerized**: Complete containerized setup with docker-compose
- ⚛️ **Modern UI**: Clean, responsive React frontend with component-based architecture

## Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)
*Clean, modern interface with PDF upload and chat functionality*

### PDF Upload
![PDF Upload](screenshots/pdf-upload.png)
*Drag-and-drop PDF upload with progress indication*

### Chat Interface
![Chat Interface](screenshots/chat-interface.png)
*Interactive chat with message bubbles and typing indicators*

### Mobile Responsive
![Mobile View](screenshots/mobile-view.png)
*Fully responsive design that works on all devices*

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL + pgvector**: Vector database for embeddings storage
- **OpenAI**: GPT-4o-mini for chat completions and text-embedding-3-small for embeddings
- **PyPDF2**: PDF text extraction
- **LangChain**: RAG pipeline components

### Frontend
- **React 18**: Modern component-based UI framework
- **Webpack**: Module bundler with hot reloading
- **Responsive Design**: Mobile-friendly interface
- **File Upload**: Drag-and-drop PDF upload functionality

### Infrastructure
- **Docker**: Containerized backend application
- **docker-compose**: Multi-service orchestration

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd rag-chatbot
```

### 2. Environment Setup
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Then edit `.env` with your actual values:
```bash
# Database Configuration
POSTGRES_USER=rag
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=ragdb
POSTGRES_HOST=db
POSTGRES_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize models
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
TOP_K=4
```

### 3. Start the Services
```bash
docker-compose up --build
```

This will start:
- PostgreSQL database with pgvector extension (port 5432)
- FastAPI backend (port 8000)

### 4. Start the Frontend

#### Option A: React Development Server (Recommended)
```bash
cd react-frontend
npm install
npm start
```
This will start the React app at `http://localhost:3000`

#### Option B: Static HTML Version (No Node.js required)
```bash
cd react-frontend
python3 -m http.server 3000
```
Then open `http://localhost:3000/static/index.html`

### 5. Access the Application
- **Frontend**: http://localhost:3000 (React) or http://localhost:3000/static/index.html (Static)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## Usage

### Upload a PDF
1. Click "Choose File" and select a PDF document
2. Click "Upload PDF" to process the document
3. Wait for the upload confirmation message

### Ask Questions
1. Type your question in the chat input
2. Press Enter or click "Send"
3. The chatbot will search your uploaded PDFs and provide answers with source references

## API Endpoints

### Core RAG Endpoints
- `POST /upload-pdf`: Upload and process a PDF file
- `POST /ask`: Ask a question about uploaded documents
- `POST /search-text`: Search for text in the knowledge base

### Document Management
- `POST /documents`: Create a new document record
- `POST /chunks`: Add text chunks with embeddings
- `GET /health`: Health check endpoint

### Chat History
- `POST /chat`: Store chat messages
- `GET /chat/{session_id}`: Retrieve chat history

## Development

### Local Development Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd react-frontend
npm install
npm start
```

### Project Structure
```
rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── db.py            # Database operations
│   │   ├── embeddings.py    # OpenAI embeddings
│   │   ├── pdf_processor.py # PDF text extraction
│   │   ├── rag.py           # LangChain RAG components
│   │   └── schema.sql       # Database schema
│   ├── Dockerfile
│   └── requirements.txt
├── react-frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js          # Main React app
│   │   └── *.css           # Styling
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── static/
│   │   └── index.html      # Standalone version
│   ├── package.json
│   └── webpack.config.js
├── db/init/
│   └── 001_pgvector.sql     # Database initialization
├── docker-compose.yml
├── .env.example             # Environment template
└── README.md
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI API access
- `POSTGRES_*`: Database connection settings
- `CHAT_MODEL`: OpenAI model for chat completions (default: gpt-4o-mini)
- `EMBEDDING_MODEL`: OpenAI model for embeddings (default: text-embedding-3-small)
- `TOP_K`: Number of chunks to retrieve for RAG (default: 4)

### PDF Processing
- Chunk size: 800 characters
- Chunk overlap: 120 characters
- Supports multi-page PDFs with page separation markers

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is correctly set in the `.env` file
   - Verify you have sufficient credits in your OpenAI account

2. **Database Connection Issues**
   - Wait for the database to fully initialize (check logs)
   - Ensure the database container is healthy before starting the API

3. **PDF Upload Fails**
   - Verify the PDF is not corrupted
   - Check that the PDF contains extractable text (not just images)
   - Ensure the file size is reasonable (< 10MB recommended)

4. **CORS Issues**
   - The backend includes CORS middleware for local development
   - For production, configure CORS origins appropriately

### Logs
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs db
```

## Production Deployment

For production deployment:

1. **Security**: Update default passwords and API keys
2. **CORS**: Configure appropriate CORS origins
3. **File Storage**: Implement proper file storage for uploaded PDFs
4. **Scaling**: Consider using managed PostgreSQL and Redis for scaling
5. **Monitoring**: Add logging and monitoring solutions

## License

This project is licensed under the MIT License.
