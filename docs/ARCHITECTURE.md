# Ask-Doc Architecture Guide

## Overview

This document explains the architecture, design patterns, and key decisions behind Ask-Doc.

## System Architecture

### Layered Architecture

Ask-Doc follows a **3-tier layered architecture**:

```
┌─────────────────────────────────────┐
│   Presentation Layer (Frontend)     │
│   - React SPA                       │
│   - User Authentication              │
│   - Document Upload UI               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   API Layer (FastAPI Backend)       │
│   - REST API Endpoints              │
│   - Request/Response Validation     │
│   - Authentication Middleware       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Business Logic Layer              │
│   - Services (Auth, Documents, RAG) │
│   - File Processing                 │
│   - Embedding Generation            │
│   - Chunking & Vector Search        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Data Layer                        │
│   - PostgreSQL + pgvector           │
│   - S3 Storage                      │
│   - Bedrock API                     │
└─────────────────────────────────────┘
```

### Service Layer

Each domain has its own service class handling business logic:

```python
# auth_service.py - User management
class AuthService:
    - signup(user_data) → user with JWT token
    - login(credentials) → JWT token
    - get_user(user_id) → user object

# document_service.py - Document CRUD
class DocumentService:
    - upload_to_s3(file) → s3_key
    - save_document_metadata(...) → Document
    - get_user_documents(user_id) → List[Document]
    - delete_document(document_id) → None

# llm_service.py - LLM and embeddings
class LLMService:
    - generate_response(prompt, context) → str

class EmbeddingService:
    - embed_text(text) → List[float]
    - embed_batch(texts) → List[List[float]]

# rag_service.py - RAG pipeline
class RAGService:
    - query_document(document_id, query) → QueryResponse
    - get_chat_history(document_id) → List[ChatHistory]
```

### Database Design

**Multi-Tenancy Pattern**: Every table has a `user_id` foreign key:

```
users (id, email, hashed_password, ...)
   ├── documents (id, user_id, filename, ...)
   │    └── chunks (id, document_id, embedding, ...)
   └── chat_history (id, user_id, document_id, ...)
```

**Query Pattern**:
```python
# Always filter by user_id to ensure data isolation
db.query(Document).filter(
    Document.user_id == current_user.id,
    Document.id == document_id
).first()
```

---

## RAG Pipeline Architecture

### 1. Ingestion Pipeline

```
Document Upload
    ↓ [validation_service]
├─ Check file type (pdf, csv, docx)
├─ Check file size (<10MB)
└─ Validate no suspicious content
    ↓ [S3 Upload]
Upload original file to S3 for backup
    ↓ [File Processing]
├─ PDF → PyPDF2 text extraction
├─ CSV → csv module parsing
└─ DOCX → python-docx extraction
    ↓ [Text Cleaning]
Remove excessive whitespace, normalize encoding
    ↓ [document_service]
Save document metadata to PostgreSQL
    ↓ [chunking_service]
├─ RecursiveCharacterTextSplitter
├─ chunk_size = 500, overlap = 100
└─ Preserve sentence boundaries
    ↓ [llm_service - EmbeddingService]
Generate embedding for each chunk (Titan model, 1536-dim)
    ↓ [Database Storage]
Store chunks with embeddings in PostgreSQL + pgvector
```

**Performance Notes**:
- File processing: ~100ms-1s per MB (depends on format)
- Embedding generation: ~50-100ms per 100 chunks
- Vector indexing: Automatic with pgvector

### 2. Retrieval Pipeline

```
User Query: "What is the main topic?"
    ↓ [Validation]
├─ Check query length (<500 chars)
└─ Check query not empty
    ↓ [embedding_service]
Generate embedding using same Titan model
(ensures semantic compatibility)
    ↓ [pgvector Similarity Search]
SELECT chunks WHERE document_id = ? 
ORDER BY embedding <-> query_embedding
LIMIT 5
    ↓ [Ranking]
Chunks ordered by cosine similarity (highest first)
    ↓ [Context Assembly]
Concatenate top-k chunks into context string
    ↓ [Prompt Engineering]
Build system + user prompt with context
```

**SQL Query (Simplified)**:
```sql
SELECT id, content, embedding <-> %s AS distance
FROM chunks
WHERE document_id = %s
ORDER BY distance ASC
LIMIT 5;
```

### 3. Generation Pipeline

```
[Context + Query]
    ↓
System Prompt:
"You are a helpful assistant. Answer questions based ONLY on 
the provided context. If the context doesn't contain information 
to answer, say 'I don't have enough information.'"
    ↓
User Prompt:
"Context: [chunk1, chunk2, chunk3, ...]
Question: What is the main topic?
Answer:"
    ↓ [Bedrock Claude Call]
Generate natural language response
    ↓ [Response Processing]
├─ Trim response
├─ Save to chat history
└─ Return with source chunks
    ↓
[Answer + Relevant Chunks to User]
```

---

## Key Design Patterns

### 1. Dependency Injection

Routes depend on services, injected via FastAPI dependencies:

```python
@router.post("/ask")
def ask_question(
    request: QueryRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user and db are injected
    rag_service = RAGService()
    return rag_service.query_document(...)
```

### 2. Service Locator Pattern

Services are instantiated at route level:

```python
doc_service = DocumentService()
rag_service = RAGService()
embedding_service = EmbeddingService()

# Each service has single responsibility
# Services are reusable across routes
```

### 3. Factory Pattern

File processing routes to correct parser:

```python
class FileProcessor:
    @staticmethod
    def process_file(content, file_type):
        if file_type == "pdf":
            return FileProcessor.process_pdf(content)
        elif file_type == "csv":
            return FileProcessor.process_csv(content)
        # ...
```

### 4. Strategy Pattern

Different embedding/LLM strategies via configuration:

```python
# Current: AWS Bedrock
BEDROCK_EMBEDDING_MODEL = "amazon.titan-embed-text-v1"
BEDROCK_LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"

# Can swap for:
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
OPENAI_LLM_MODEL = "gpt-4-turbo"
```

---

## Performance Optimization

### 1. Embedding Caching

```python
# Don't regenerate embeddings for same text
embedding_cache = {}
def get_embedding(text):
    if text in embedding_cache:
        return embedding_cache[text]
    embedding = embedding_service.embed_text(text)
    embedding_cache[text] = embedding
    return embedding
```

### 2. Batch Processing

```python
# Generate embeddings in parallel
def embed_chunks(chunks):
    # Could use ThreadPoolExecutor for parallel calls
    embeddings = []
    for chunk in chunks:
        embeddings.append(embedding_service.embed_text(chunk))
    return embeddings
```

### 3. Database Indexing

```sql
-- Fast vector similarity search
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Fast user document lookup
CREATE INDEX ON documents(user_id);
CREATE INDEX ON chunks(document_id);
```

### 4. Connection Pooling

```python
# SQLAlchemy manages DB connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Max connections
    max_overflow=40,       # Additional connections if needed
)
```

---

## Security Architecture

### 1. Authentication Flow

```
Signup/Login
    ↓
Verify Email/Password
    ↓
Generate JWT Token (HS256)
    ↓
Return Token to Client
    ↓
Client stores in localStorage
    ↓
Client sends with each request:
    Authorization: Bearer <token>
    ↓
Backend verifies signature + expiry
    ↓
Extract user_id from token payload
    ↓
Filter all queries by user_id
```

### 2. Multi-Tenancy Enforcement

```
Every operation:
1. Get current user from JWT
2. Verify user_id in request matches JWT user_id
3. Filter DB queries by user_id
4. Never trust user input for user_id

Example:
@router.get("/documents/{document_id}")
def get_document(document_id: int, current_user = Depends(get_current_user)):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.user_id  # ← Key check
    ).first()
    if not doc:
        raise 404
    return doc
```

### 3. Input Validation

```python
class QueryRequest(BaseModel):
    document_id: int
    query: str
    top_k: int = 5

# Pydantic validates:
# - Type checking
# - Required fields
# - Max string length
# - Custom validators
```

### 4. PII Masking

```python
class ValidationService:
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    
    @staticmethod
    def mask_pii(text):
        text = EMAIL_PATTERN.sub("[EMAIL]", text)
        text = PHONE_PATTERN.sub("[PHONE]", text)
        return text
```

---

## Scalability Considerations

### Horizontal Scaling

1. **Stateless Backend**: FastAPI instances can be load-balanced
2. **Shared Database**: All instances connect to same PostgreSQL
3. **S3 Storage**: Shared across instances
4. **Bedrock API**: Managed service, auto-scales

```
┌──────────────────────┐
│   Load Balancer      │
└──────────────┬───────┘
        │
    ┌───┼───┬───────────┐
    │   │   │           │
┌───▼──┐│  Backend Instance 2
│Backend││
│Inst 1 ││
└───────┘└──────────────┘
    │
    ▼
┌──────────────┐
│ PostgreSQL   │
│ (Shared)     │
└──────────────┘
```

### Vertical Scaling

1. **Increase DB connections**: Adjust `pool_size`, `max_overflow`
2. **Increase worker processes**: Uvicorn workers
3. **Increase memory**: For embedding cache

### Bottlenecks & Solutions

| Bottleneck | Solution |
|-----------|----------|
| Slow embedding generation | Use batch API, cache embeddings |
| Slow vector search | Add pgvector indices, use approximate search |
| Slow file processing | Async processing, queue system (Celery) |
| High memory usage | Streaming responses, pagination |
| DB connections exhausted | Increase pool size, optimize query time |

---

## Error Handling

### Exception Hierarchy

```python
# Custom exceptions for clarity
class AskDocException(Exception):
    pass

class ValidationError(AskDocException):
    pass

class DocumentNotFoundError(AskDocException):
    pass

class EmbeddingError(AskDocException):
    pass

# Usage in services
try:
    embedding = embedding_service.embed_text(text)
except Exception as e:
    raise EmbeddingError(f"Failed to generate embedding: {str(e)}")
```

### Error Response Format

```json
{
  "detail": "File exceeds maximum size of 10MB",
  "error_code": "FILE_TOO_LARGE"
}
```

---

## Monitoring & Observability

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Document {doc_id} uploaded successfully")
logger.warning(f"Embedding generation took {duration}ms")
logger.error(f"Bedrock API call failed: {str(e)}")
```

### Metrics to Track

```
- Upload latency per file type
- Embedding generation time
- Vector search latency
- LLM response time
- User retention/churn
- Token usage costs
- Error rates by endpoint
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_db(),
        "s3": check_s3(),
        "bedrock": check_bedrock()
    }
```

---

## Testing Strategy

### Unit Tests

Test individual services in isolation:

```python
# tests/test_validation_service.py
def test_validate_file_size():
    with pytest.raises(ValueError):
        ValidationService.validate_file_size(11_000_000, 10_000_000)

def test_mask_pii():
    text = "Email: john@example.com"
    masked = ValidationService.mask_pii(text)
    assert "@" not in masked
```

### Integration Tests

Test multiple services together:

```python
# tests/test_document_upload.py
def test_full_upload_flow():
    # Create user → Upload file → Check chunks created
    user = create_test_user()
    doc = upload_test_document(user)
    chunks = get_chunks(doc.id)
    assert len(chunks) > 0
    assert all(chunk.embedding is not None for chunk in chunks)
```

### End-to-End Tests

Test full user flows:

```python
# tests/test_e2e.py
def test_ask_document():
    # Signup → Upload → Ask question → Get answer
    token = signup_user()
    doc_id = upload_document(token, "test.pdf")
    response = ask_question(token, doc_id, "What is this about?")
    assert "answer" in response
    assert len(response["relevant_chunks"]) > 0
```

---

## Future Improvements

1. **Real-time Collaboration**: WebSocket support for shared editing
2. **Advanced RAG**: Hybrid search (keyword + semantic), re-ranking
3. **Multi-modal**: Support images, audio, video
4. **Fine-tuning**: Allow users to fine-tune models on their data
5. **Caching**: Redis for embeddings, query results
6. **Async Tasks**: Celery for long-running operations
7. **Analytics**: Dashboard for usage, insights
8. **Export**: Save conversations, generate reports

---

## References

- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/concepts/)
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector)
- [AWS Bedrock Architecture](https://docs.aws.amazon.com/bedrock/)
- [RAG Best Practices](https://www.anthropic.com/news/retrieval-augmented-generation)
