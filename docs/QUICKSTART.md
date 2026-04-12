# Quick Start Guide

Get Ask-Doc running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- AWS Account with Bedrock access (or optional for testing)
- Git

## 1. Clone & Setup

```bash
git clone <repo-url>
cd ask-doc

# Copy environment template
cp backend/.env.example backend/.env
```

## 2. Configure AWS (Optional - Required for Real LLM Calls)

Edit `backend/.env`:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
S3_BUCKET=ask-doc-files  # Create this S3 bucket first
```

**Note**: Without AWS credentials, the app will still work but LLM calls will fail with a mock response.

## 3. Start Docker Services

```bash
make dev
```

This starts:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- React frontend (port 3000)

Wait 30 seconds for services to initialize.

## 4. Access the App

Open browser to: **http://localhost:3000**

## 5. Test the Flow

### Step 1: Sign Up
- Email: `test@example.com`
- Name: `Test User`
- Password: `test123456`

### Step 2: Create Sample Document

Create a test file `sample.txt`:

```
Artificial Intelligence Revolution

AI has transformed industries. Key areas include:
- Natural Language Processing: Understanding human language
- Computer Vision: Interpreting images and videos
- Reinforcement Learning: Training through feedback loops

Companies adopting AI report 40% efficiency gains.
The future is AI-driven automation.
```

Save as `sample.pdf` using any converter, or use existing PDF.

### Step 3: Upload Document
- Click "Upload Document"
- Select your PDF
- Wait for processing (shows "Uploading...")

### Step 4: Ask Questions
- Click "Ask Questions" on uploaded document
- Try: "What is AI used for?"
- Wait for LLM response

### Step 5: View Chat History
- Previous questions are saved
- Click on any to see full context

## Common Issues

### Issue: Database Connection Error
```
psycopg2.OperationalError: could not connect to server
```

**Solution**: Wait 10-20 seconds for PostgreSQL to start
```bash
# Check container logs
docker-compose logs postgres
```

### Issue: 502 Bad Gateway
Frontend can't connect to backend.

**Solution**: Check backend is running
```bash
docker-compose logs backend
```

### Issue: AWS Credentials Error
```
UnrecognizedClientException: The security token included in the request is invalid
```

**Solution**: Verify AWS credentials in `.env` are correct

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all
make dev-stop

# Full cleanup
make dev-clean

# Access database
docker-compose exec postgres psql -U askdoc_user -d askdoc

# Check backend API docs
# Visit: http://localhost:8000/docs
```

## File Structure After Setup

```
ask-doc/
├── backend/
│   ├── .env              # Your AWS config (created)
│   ├── app/
│   └── Dockerfile
├── frontend/
│   ├── .env              # API URL config
│   ├── src/
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Next Steps

1. **Explore API**: Visit http://localhost:8000/docs for interactive API docs
2. **Review Code**: Check `backend/app/services/` for core logic
3. **Modify Prompts**: Edit `backend/app/services/llm_service.py` line ~48
4. **Add Features**: Try adding user profiles, document sharing, etc.

## Stop Services

```bash
# Stop but keep data
make dev-stop

# Stop and delete everything (including database)
make dev-clean
```

---

**Congratulations! You've deployed Ask-Doc! 🎉**

For detailed setup, see [README.md](../README.md)
