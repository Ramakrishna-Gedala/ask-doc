# 🎯 Ask-Doc: Multi-Tenant AI Document Q&A System

A production-ready SaaS application for uploading documents (PDF, CSV, DOCX) and asking AI-powered questions using **Retrieval-Augmented Generation (RAG)** with **Amazon Bedrock**.

Perfect for understanding **RAG architectures**, **multi-tenancy patterns**, and **modern AI/LLM integrations** in interviews.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup Guide](#setup-guide)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Documentation](#api-documentation)
- [Alternative Tools](#alternative-tools)
- [Interview Talking Points](#interview-talking-points)

---

## 🎨 Project Overview

**Ask-Doc** is a multi-tenant application where users can:

1. **Upload documents** (PDF, CSV, DOCX) - max 10MB each
2. **Ask questions** about their documents using natural language
3. **Get AI-powered answers** with relevant document excerpts
4. **View chat history** of previous questions and answers

**Example Flow:**
- User uploads a research paper (PDF)
- Asks: "What are the key findings?"
- System:
  - Finds relevant paragraphs using semantic search
  - Sends them + question to Claude AI
  - Returns natural language answer + source excerpts

---

## 🏗️ Architecture

### High-Level Flow

```
User Upload → Extract Text → Chunk Document → Generate Embeddings → Store in DB
                                                                          ↓
User Query → Embed Query → Semantic Search → Retrieve Chunks → LLM Answer Generation
```

### System Diagram

```
┌─────────────────┐
│   Frontend      │  (React SPA)
│   (Port 3000)   │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Nginx   │  (Reverse Proxy, Load Balancer)
    └────┬────┘
         │
    ┌────▼──────────────────────────┐
    │   Backend (FastAPI)            │
    │   - Auth (JWT)                 │
    │   - Document Upload/Processing │
    │   - RAG Query Engine           │
    │   (Port 8000)                  │
    └────┬──────────────┬────────────┘
         │              │
    ┌────▼────┐    ┌────▼─────────┐
    │PostgreSQL│    │  AWS Services │
    │+ pgvector│    │- Bedrock      │
    │  (DB)    │    │- S3 (Storage) │
    └──────────┘    └───────────────┘
```

### Data Flow: Document Processing

```
1. Upload (PDF, CSV, DOCX)
   ↓ Extract text using language-specific parsers
2. Raw Text Extraction
   ↓ Split with overlap using RecursiveCharacterTextSplitter
3. Chunking (500 chars, 100 overlap)
   ↓ Generate embedding for each chunk
4. Vector Embeddings (Titan Model, 1536 dims)
   ↓ Store in PostgreSQL with pgvector
5. Chunk Storage in DB
```

### Data Flow: Query Processing (RAG)

```
1. User Question
   ↓ Embed query using same Titan model
2. Query Embedding
   ↓ Semantic search using pgvector cosine similarity
3. Find Similar Chunks (Top-5)
   ↓ Build context from relevant chunks
4. Context Building
   ↓ Send to Claude with guardrails
5. LLM Generation
   ↓ Return answer + source chunks
6. User Gets Answer
```

---

## 💻 Tech Stack

### Backend
- **Framework**: FastAPI (Python web framework, similar to Express.js but Python)
- **Database**: PostgreSQL with pgvector (vector database extension)
- **ORM**: SQLAlchemy (database abstraction)
- **LLM/Embeddings**: AWS Bedrock (Claude + Titan models)
- **Orchestration**: LangChain (LLM framework)
- **Authentication**: JWT (JSON Web Tokens)
- **File Storage**: Amazon S3

### Frontend
- **UI Framework**: ReactJS (SPA with Vite/React Scripts)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **UI Components**: Lucide Icons
- **Styling**: Vanilla CSS with Flexbox/Grid

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx
- **Cloud**: AWS (EC2, S3, Bedrock, RDS)

### Development Tools
- **Code Quality**: Black, Flake8
- **Testing**: Pytest, React Testing Library
- **Build Tools**: Makefile for automation

---

## 🚀 Setup Guide

### Prerequisites

- **Docker & Docker Compose** (for containerized development)
- OR **Python 3.11+** + **Node.js 18+** (for local development)
- **AWS Account** with Bedrock access
- **Git**

### Step 1: Clone & Initialize

```bash
git clone <repo-url>
cd ask-doc

# Create environment files
cp backend/.env.example backend/.env
```

### Step 2: Configure AWS Credentials

Edit `backend/.env`:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=ask-doc-files  # Create this S3 bucket first
```

**Important**: Enable Bedrock models in AWS console:
- `amazon.titan-embed-text-v1` (Embeddings)
- `anthropic.claude-3-sonnet-20240229-v1:0` (LLM)

### Step 3A: Docker Setup (Recommended)

```bash
# Install all dependencies and start services
make dev

# View logs
make dev-logs

# Access the app
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/docs
# Database:  localhost:5432
```

### Step 3B: Local Development Setup

**Backend:**

```bash
cd backend
pip install -r requirements.txt

# Create .env file and configure
cp .env.example .env

# Start PostgreSQL (Docker)
docker run -d \
  --name askdoc-db \
  -e POSTGRES_USER=askdoc_user \
  -e POSTGRES_PASSWORD=askdoc_password_change_me \
  -e POSTGRES_DB=askdoc \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Run migrations and start server
python -m app.db.database  # Initialize DB
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm start
```

### Step 4: Test the Application

1. **Sign Up**: Create an account at `http://localhost:3000/signup`
2. **Upload Document**: Upload a test PDF/CSV/DOCX
3. **Ask Questions**: Try asking about the document
4. **View History**: Check past queries in the sidebar

---

## 📁 Project Structure

```
ask-doc/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── api/                 # API route handlers
│   │   │   ├── auth_routes.py  # Login/Signup endpoints
│   │   │   ├── document_routes.py # File upload endpoints
│   │   │   └── query_routes.py  # RAG query endpoints
│   │   ├── core/                # Configuration
│   │   │   ├── config.py        # Environment variables
│   │   │   └── security.py      # JWT, password hashing
│   │   ├── db/                  # Database
│   │   │   └── database.py      # Connection, migrations
│   │   ├── models/              # Data models
│   │   │   ├── db.py            # SQLAlchemy ORM models
│   │   │   └── schemas.py       # Pydantic request/response
│   │   ├── services/            # Business logic layer
│   │   │   ├── auth_service.py  # User management
│   │   │   ├── document_service.py # Document CRUD + S3
│   │   │   ├── file_processor.py # PDF/CSV/DOCX parsing
│   │   │   ├── chunking_service.py # Text splitting
│   │   │   ├── llm_service.py   # Bedrock LLM + Embeddings
│   │   │   ├── rag_service.py   # RAG pipeline
│   │   │   └── validation_service.py # Input validation
│   │   └── main.py              # FastAPI app initialization
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Backend container image
│   └── .env.example             # Environment template
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── api/                 # API client
│   │   │   ├── client.js        # Axios instance + interceptors
│   │   │   └── services.js      # API helper functions
│   │   ├── components/          # Reusable React components
│   │   │   ├── Navigation.jsx   # Top navigation bar
│   │   │   ├── DocumentUpload.jsx # File upload form
│   │   │   ├── DocumentList.jsx # Document grid
│   │   │   └── QueryInterface.jsx # Chat interface
│   │   ├── context/             # State management
│   │   │   └── AuthContext.jsx  # User authentication state
│   │   ├── pages/               # Page components
│   │   │   ├── Login.jsx        # Login page
│   │   │   ├── Signup.jsx       # Signup page
│   │   │   └── Documents.jsx    # Main dashboard
│   │   ├── styles/              # CSS files
│   │   ├── App.jsx              # App routing
│   │   ├── index.jsx            # React entry point
│   │   └── index.css            # Global styles
│   ├── public/
│   │   └── index.html           # HTML template
│   ├── package.json             # Dependencies
│   ├── Dockerfile               # Frontend container image
│   └── .env                     # Environment variables
│
├── docker-compose.yml           # Multi-container orchestration
├── nginx.conf                   # Reverse proxy config
├── Makefile                     # Development automation
└── README.md                    # This file
```

---

## 🔄 How It Works

### 1. Authentication Flow

```
User Input (Email/Password)
    ↓
Backend Validation → Password Hashing (bcrypt)
    ↓
Create JWT Token (HS256)
    ↓
Return Token to Frontend
    ↓
Frontend Stores Token in localStorage
    ↓
All Requests Include: Authorization: Bearer <token>
```

**Multi-tenancy**: All queries filter by `user_id` from JWT token.

### 2. Document Upload Flow

```
1. Frontend: File selected by user
2. Validation: Check size (<10MB) & type (pdf/csv/docx)
3. Backend: Receive file
4. S3 Upload: Store original file for backup
5. File Processing:
   - PDF: PyPDF2 extracts text page by page
   - CSV: csv module converts rows to text
   - DOCX: python-docx extracts paragraphs + tables
6. Chunking:
   - RecursiveCharacterTextSplitter
   - Size: 500 chars, Overlap: 100 chars
   - Preserves sentence boundaries
7. Embedding:
   - Bedrock Titan model
   - Generates 1536-dim vector per chunk
8. Storage:
   - PostgreSQL with pgvector
   - Stores: chunk_id, content, embedding, metadata
```

### 3. Query (RAG) Flow

```
User Question: "What are the main topics?"
    ↓
1. RETRIEVE: Semantic Search
   - Embed query using same Titan model
   - Compare with chunk embeddings using cosine similarity
   - Get top-5 most similar chunks
   ↓
2. AUGMENT: Build Context
   - Extract text from top-5 chunks
   - Create prompt with context
   ↓
3. GENERATE: LLM Call
   - Send to Claude via Bedrock
   - Prompt includes guardrail: "Answer only from context"
   - Claude generates natural language answer
   ↓
4. RETURN: Response to User
   - Answer text
   - Source chunks with highlighting
```

**Guardrails Implemented:**
- ✅ Input validation (query length <500 chars)
- ✅ Content filtering (no code execution)
- ✅ PII masking (regex for emails/phones)
- ✅ Fallback message if no context found
- ✅ System prompt: "Answer only from provided context"

---

## 📡 API Documentation

### Authentication Endpoints

#### POST /auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com"
}
```

#### POST /auth/login
Authenticate user and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:** Same as signup

---

### Document Endpoints

#### POST /documents/upload
Upload and process a document.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Binary file (PDF, CSV, or DOCX)

**Response:**
```json
{
  "id": 1,
  "filename": "research_paper.pdf",
  "file_type": "pdf",
  "file_size": 2048576,
  "created_at": "2024-04-12T10:30:00Z"
}
```

#### GET /documents/
List all documents for user.

**Response:**
```json
{
  "total": 3,
  "documents": [
    {
      "id": 1,
      "filename": "research.pdf",
      "file_type": "pdf",
      "file_size": 2048576,
      "created_at": "2024-04-12T10:30:00Z"
    }
  ]
}
```

#### DELETE /documents/{document_id}
Delete a document.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

### Query Endpoints

#### POST /query/ask
Ask a question about a document using RAG.

**Request:**
```json
{
  "document_id": 1,
  "query": "What are the main findings?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "The main findings are...",
  "relevant_chunks": [
    {
      "id": 42,
      "chunk_index": 5,
      "content": "On page 3, the research found...",
      "tokens": 150
    }
  ],
  "query": "What are the main findings?",
  "document_id": 1
}
```

#### GET /query/history/{document_id}
Get chat history for a document.

**Response:**
```json
{
  "document_id": 1,
  "total": 5,
  "history": [
    {
      "id": 1,
      "query": "What is this about?",
      "answer": "This document is about...",
      "relevant_chunks": 5,
      "created_at": "2024-04-12T10:35:00Z"
    }
  ]
}
```

---

## 🔌 Alternative Tools & Architectures

### Vector Database Alternatives

| Tool | Pros | Cons |
|------|------|------|
| **PostgreSQL + pgvector** (Current) | SQL familiarity, cost-effective, integrated | ~Slower for massive scale |
| **Pinecone** | Managed, fast, scalable | Vendor lock-in, monthly cost |
| **Weaviate** | Open-source, flexible | More setup, ops overhead |
| **Milvus** | High-performance, open-source | Complex deployment |
| **Qdrant** | Fast, Rust-based | Newer ecosystem |

### LLM Alternatives

| Provider | Model | Pros | Cons |
|----------|-------|------|------|
| **AWS Bedrock** (Current) | Claude, Titan | AWS integration, multi-model | Vendor lock-in |
| **OpenAI** | GPT-4, GPT-3.5 | Powerful, many integrations | Pay-per-token, no self-hosted |
| **Hugging Face** | Open models | Free, no API costs | Requires inference server |
| **Together AI** | Llama, Mistral | Affordable, open models | Smaller ecosystem |
| **Anthropic Direct** | Claude | Same as Bedrock | Separate billing |

### Document Parsing Alternatives

| Tool | Supported Formats | Pros | Cons |
|------|-------------------|------|------|
| **PyPDF2** (Current) | PDF | Simple, lightweight | Limited OCR |
| **pdfplumber** | PDF | Accurate table extraction | PDF-only |
| **Unstructured.io** | PDF, DOCX, PPT, etc. | Comprehensive | Cloud-based |
| **LlamaParse** | PDF, DOCX, images | LLM-based parsing | API calls |
| **Adobe PDF Extract** | PDF | Highly accurate | Enterprise cost |

### Frontend Alternatives

| Framework | Pros | Cons |
|-----------|------|------|
| **React** (Current) | Large ecosystem, jobs | Complex for simple apps |
| **Vue.js** | Gentle learning curve | Smaller ecosystem |
| **Svelte** | Minimal boilerplate | Newer, fewer jobs |
| **Next.js** | Full-stack, SSR | Overkill for SPA |

### Deployment Alternatives

| Platform | Pros | Cons |
|----------|------|------|
| **Docker + EC2** (Current) | Full control, flexible | Ops overhead |
| **ECS/Fargate** | AWS native, serverless | Vendor lock-in |
| **Kubernetes** | Production-grade, portable | Complex, overkill for small apps |
| **Vercel/Netlify** | Zero-ops frontend | Limited backend support |
| **Render/Railway** | Easy deployment | Limited customization |

---

## 💡 Interview Talking Points

### 1. Multi-Tenancy

- **What it is**: Each user's data is isolated, even in shared infrastructure
- **Implementation**: Filter all queries by `user_id`
- **Why it matters**: Scales cost-efficiently, improves security
- **Challenge**: Ensuring data isolation at every layer

### 2. RAG (Retrieval-Augmented Generation)

- **Why RAG?**: LLMs hallucinate; RAG grounds answers in real data
- **Process**: Retrieve relevant docs → Augment prompt → Generate answer
- **Semantic Search**: Vector embeddings enable "meaning" matching, not keyword matching
- **Trade-offs**: Embedding quality vs. retrieval speed

### 3. Vector Embeddings

- **What**: Convert text to 1536-dimensional vectors
- **Similarity**: Cosine distance measures text relevance
- **Challenge**: Embedding cost scales with data size (optimize chunking)
- **Alternative**: Sparse embeddings, hierarchical retrieval

### 4. JWT Authentication

- **Stateless**: No session storage needed
- **Security**: Signed token prevents tampering
- **Challenge**: Token revocation (use blacklist or short expiry)

### 5. File Processing Pipeline

- **Scalability**: Chunking enables parallel processing
- **Quality**: Overlapping chunks preserve context
- **Challenge**: Format-specific parsing (PDF OCR, table extraction)

### 6. Chunking Strategy

- **Size**: 500 chars balances context vs. precision
- **Overlap**: 100 chars preserves sentence continuity
- **Alternative**: Hierarchical chunking, semantic chunking

### 7. Performance Optimization

- **Caching**: Cache embeddings to avoid regeneration
- **Batch Processing**: Generate embeddings in parallel
- **Lazy Loading**: Stream large results instead of loading all

### 8. Error Handling & Guardrails

- **Input Validation**: Check file type, size before processing
- **Content Filtering**: PII masking, prompt injection detection
- **Fallback**: Return sensible error if no context found

---

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest backend/tests/

# With coverage
pytest --cov=app backend/tests/

# Test specific module
pytest backend/tests/test_auth.py
```

### Frontend Tests
```bash
# Run tests
npm test --prefix frontend

# With coverage
npm test -- --coverage --prefix frontend
```

---

## 📚 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Documents Table
```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  filename VARCHAR(500) NOT NULL,
  file_type VARCHAR(10),
  file_size INTEGER,
  s3_key VARCHAR(500),
  original_text TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Chunks Table (with pgvector)
```sql
CREATE TABLE chunks (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id),
  chunk_index INTEGER,
  content TEXT NOT NULL,
  embedding vector(1536),  -- pgvector column
  tokens INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Vector similarity index for fast search
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
```

---

## 🔒 Security Considerations

- ✅ **JWT Tokens**: Signed, can't be tampered with
- ✅ **Password Hashing**: bcrypt with salt
- ✅ **CORS**: Only allow frontend origin
- ✅ **SQL Injection**: SQLAlchemy ORM prevents it
- ✅ **PII Masking**: Regex patterns mask sensitive data
- ✅ **File Validation**: Type & size checks before upload
- ⚠️ **Multi-tenancy**: Must verify `user_id` on every request
- ⚠️ **Rate Limiting**: Implement in production (configured in nginx.conf)

---

## 📖 Documentation

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# View migration history
alembic history
```

### Logging
Enable debug logging:
```env
DEBUG=True
```

View logs:
```bash
docker-compose logs -f backend
```

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **React Docs**: https://react.dev
- **pgvector README**: https://github.com/pgvector/pgvector
- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock
- **LangChain Docs**: https://python.langchain.com

---

## 📞 Support

For issues, questions, or improvements:
1. Check existing issues
2. Create detailed bug reports
3. Follow contributing guidelines

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- FastAPI for the amazing Python web framework
- AWS Bedrock for LLM & embedding models
- pgvector for vector search in PostgreSQL
- React community for frontend tooling

---

**Happy Coding! 🚀**

This is a learning project designed for understanding modern AI/LLM architectures. Use it as reference for building similar systems!
