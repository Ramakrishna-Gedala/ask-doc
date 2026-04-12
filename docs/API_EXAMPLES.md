# API Examples

Complete examples of all Ask-Doc API endpoints with curl commands and responses.

## Setup

Start the backend:
```bash
docker-compose up backend
# API available at: http://localhost:8000
```

Access interactive API docs: http://localhost:8000/docs

---

## Authentication Endpoints

### 1. Sign Up

Create a new user account.

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepass123"
  }'
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJleHAiOjE3MTM0NTAwMzd9.abc123...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "john@example.com"
}
```

**Error (400):**
```json
{
  "detail": "User with this email already exists"
}
```

---

### 2. Login

Authenticate and get JWT token.

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "john@example.com"
}
```

**Error (401):**
```json
{
  "detail": "Invalid credentials"
}
```

---

### 3. Get Current User Profile

Get authenticated user details.

**cURL:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-04-12T10:30:00Z"
}
```

**Error (401):**
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

## Document Endpoints

### 4. Upload Document

Upload and process a document (PDF, CSV, DOCX).

**cURL:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

**Response (200):**
```json
{
  "id": 1,
  "filename": "research_paper.pdf",
  "file_type": "pdf",
  "file_size": 2048576,
  "created_at": "2024-04-12T10:30:00Z"
}
```

**Errors:**

Invalid file type (400):
```json
{
  "detail": "File type 'txt' not allowed"
}
```

File too large (400):
```json
{
  "detail": "File exceeds maximum size of 10MB"
}
```

Too many files (400):
```json
{
  "detail": "Maximum 20 documents per user"
}
```

---

### 5. List Documents

Get all documents for authenticated user.

**cURL:**
```bash
curl -X GET http://localhost:8000/documents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200):**
```json
{
  "total": 3,
  "documents": [
    {
      "id": 3,
      "filename": "notes.docx",
      "file_type": "docx",
      "file_size": 512000,
      "created_at": "2024-04-12T11:00:00Z"
    },
    {
      "id": 2,
      "filename": "data.csv",
      "file_type": "csv",
      "file_size": 1024000,
      "created_at": "2024-04-12T10:45:00Z"
    },
    {
      "id": 1,
      "filename": "research_paper.pdf",
      "file_type": "pdf",
      "file_size": 2048576,
      "created_at": "2024-04-12T10:30:00Z"
    }
  ]
}
```

---

### 6. Get Specific Document

Get details of a single document.

**cURL:**
```bash
curl -X GET http://localhost:8000/documents/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200):**
```json
{
  "id": 1,
  "filename": "research_paper.pdf",
  "file_type": "pdf",
  "file_size": 2048576,
  "created_at": "2024-04-12T10:30:00Z"
}
```

**Error (404):**
```json
{
  "detail": "Document not found or access denied"
}
```

---

### 7. Delete Document

Delete a document and associated chunks.

**cURL:**
```bash
curl -X DELETE http://localhost:8000/documents/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200):**
```json
{
  "message": "Document deleted successfully"
}
```

**Error (404):**
```json
{
  "detail": "Document not found or access denied"
}
```

---

## Query/RAG Endpoints

### 8. Ask Document Question

Ask a question about a document using RAG.

**cURL:**
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "query": "What are the main findings of this research?",
    "top_k": 5
  }'
```

**Response (200):**
```json
{
  "answer": "According to the research paper, the main findings are:\n\n1. AI implementation increases operational efficiency by 40%\n2. Organizations adopting AI see improved customer satisfaction\n3. Data quality is critical for AI success\n\nThe study surveyed 500 companies across various industries.",
  "relevant_chunks": [
    {
      "id": 42,
      "chunk_index": 5,
      "content": "Our research found that AI implementation leads to a 40% increase in operational efficiency. Companies that invested in data quality saw even better results, with some reporting 60% improvements in specific processes.",
      "tokens": 150
    },
    {
      "id": 43,
      "chunk_index": 6,
      "content": "Customer satisfaction improved significantly. In the financial services sector, adoption of AI-driven customer service increased satisfaction scores by 35 percentage points.",
      "tokens": 120
    }
  ],
  "query": "What are the main findings of this research?",
  "document_id": 1
}
```

**Errors:**

Query too long (400):
```json
{
  "detail": "Query exceeds maximum length of 500"
}
```

Document not found (404):
```json
{
  "detail": "Document not found or access denied"
}
```

LLM generation failed (500):
```json
{
  "detail": "Failed to process query"
}
```

---

### 9. Get Chat History

Get all previous questions and answers for a document.

**cURL:**
```bash
curl -X GET "http://localhost:8000/query/history/1?limit=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200):**
```json
{
  "document_id": 1,
  "total": 3,
  "history": [
    {
      "id": 3,
      "query": "How was this study conducted?",
      "answer": "The study was conducted over 12 months and included...",
      "relevant_chunks": 4,
      "created_at": "2024-04-12T11:15:00Z"
    },
    {
      "id": 2,
      "query": "What industries were included?",
      "answer": "The research covered technology, finance, healthcare...",
      "relevant_chunks": 5,
      "created_at": "2024-04-12T11:05:00Z"
    },
    {
      "id": 1,
      "query": "What are the main findings?",
      "answer": "According to the research paper, the main findings are...",
      "relevant_chunks": 5,
      "created_at": "2024-04-12T10:35:00Z"
    }
  ]
}
```

---

## Health & Status

### 10. Health Check

Check API health status.

**cURL:**
```bash
curl http://localhost:8000/health
```

**Response (200):**
```json
{
  "status": "healthy"
}
```

---

### 11. API Root

Get API information.

**cURL:**
```bash
curl http://localhost:8000/
```

**Response (200):**
```json
{
  "message": "Ask-Doc API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## Complete Workflow Example

Here's a complete end-to-end example:

### 1. Sign Up
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "full_name": "Test User",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Upload Document
```bash
DOC_ID=$(curl -s -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample.pdf" | jq -r '.id')

echo "Document ID: $DOC_ID"
```

### 3. Ask Question
```bash
curl -s -X POST http://localhost:8000/query/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"document_id\": $DOC_ID,
    \"query\": \"What is the main topic?\",
    \"top_k\": 5
  }" | jq .
```

### 4. View History
```bash
curl -s -X GET "http://localhost:8000/query/history/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### 5. Delete Document
```bash
curl -X DELETE "http://localhost:8000/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing with Postman

### 1. Import Collection

Create a new Postman collection with these requests:

**Request 1: Sign Up**
- Method: `POST`
- URL: `http://localhost:8000/auth/signup`
- Body (JSON):
  ```json
  {
    "email": "{{email}}",
    "full_name": "Test User",
    "password": "test123456"
  }
  ```
- Tests:
  ```javascript
  var jsonData = pm.response.json();
  pm.environment.set("token", jsonData.access_token);
  pm.environment.set("user_id", jsonData.user_id);
  ```

**Request 2: Upload Document**
- Method: `POST`
- URL: `http://localhost:8000/documents/upload`
- Headers: `Authorization: Bearer {{token}}`
- Body: Form-Data with `file` field
- Tests:
  ```javascript
  var jsonData = pm.response.json();
  pm.environment.set("doc_id", jsonData.id);
  ```

**Request 3: Ask Question**
- Method: `POST`
- URL: `http://localhost:8000/query/ask`
- Headers: `Authorization: Bearer {{token}}`
- Body (JSON):
  ```json
  {
    "document_id": {{doc_id}},
    "query": "What is this about?",
    "top_k": 5
  }
  ```

---

## Environment Variables for Testing

Create a `.env` file in Postman or shell:

```bash
# Auth
API_BASE_URL=http://localhost:8000
EMAIL=user+$(date +%s)@test.com  # Unique email each run

# Auto-populated by tests
TOKEN=
USER_ID=
DOC_ID=
```

---

## Common cURL Tips

```bash
# Pretty print JSON response
curl ... | jq .

# Save access token to variable
TOKEN=$(curl ... | jq -r '.access_token')

# Use token in subsequent requests
curl ... -H "Authorization: Bearer $TOKEN"

# Upload file
curl ... -F "file=@filename.pdf"

# Check response headers
curl -i ...

# Debug request
curl -v ...

# Follow redirects
curl -L ...
```

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "detail": "Error message"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `404` - Not found (document doesn't exist)
- `500` - Server error

---

## Rate Limiting

In production (nginx.conf):
- API endpoints: 100 requests/minute per IP
- General endpoints: 1000 requests/minute per IP

You'll receive `429` status if rate limit exceeded.

---

**Happy Testing! 🚀**
