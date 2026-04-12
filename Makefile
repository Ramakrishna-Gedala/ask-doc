# Makefile for Ask-Doc Project
# Simplifies common development and deployment tasks

.PHONY: help install dev build logs down clean test lint format

help:
	@echo "Ask-Doc Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        - Install all dependencies"
	@echo "  make setup-env      - Create environment files from templates"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start development environment (docker-compose)"
	@echo "  make dev-stop       - Stop development environment"
	@echo "  make dev-logs       - View development logs"
	@echo "  make dev-clean      - Stop and clean development environment"
	@echo ""
	@echo "Backend:"
	@echo "  make backend-install - Install backend dependencies"
	@echo "  make backend-dev    - Run backend server locally (requires DB)"
	@echo "  make backend-test   - Run backend tests"
	@echo "  make backend-lint   - Run linter on backend code"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo "  make frontend-dev    - Run frontend dev server"
	@echo "  make frontend-build  - Build frontend for production"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-reset       - Reset database (WARNING: deletes data)"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-build   - Build production Docker images"
	@echo "  make deploy-up      - Start production containers"
	@echo "  make deploy-down    - Stop production containers"
	@echo ""

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

install: setup-env backend-install frontend-install
	@echo "✓ Installation complete!"

setup-env:
	@echo "Creating environment files..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "Created backend/.env - please configure AWS credentials"; \
	fi
	@if [ ! -f frontend/.env ]; then \
		echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env; \
		echo "Created frontend/.env"; \
	fi

# ============================================================================
# DEVELOPMENT
# ============================================================================

dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "✓ Development environment started!"
	@echo "Frontend:  http://localhost:3000"
	@echo "Backend:   http://localhost:8000"
	@echo "Database:  localhost:5432"
	@echo "API Docs:  http://localhost:8000/docs"

dev-stop:
	@echo "Stopping development environment..."
	docker-compose stop

dev-logs:
	docker-compose logs -f

dev-clean:
	@echo "Cleaning up development environment..."
	docker-compose down -v
	@echo "✓ Development environment cleaned!"

# ============================================================================
# BACKEND
# ============================================================================

backend-install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

backend-dev:
	@echo "Starting backend server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	@echo "Running backend tests..."
	cd backend && pytest

backend-lint:
	@echo "Linting backend code..."
	cd backend && flake8 app/ --max-line-length=100

backend-format:
	@echo "Formatting backend code..."
	cd backend && black app/

# ============================================================================
# FRONTEND
# ============================================================================

frontend-install:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

frontend-dev:
	@echo "Starting frontend dev server..."
	cd frontend && npm start

frontend-build:
	@echo "Building frontend for production..."
	cd frontend && npm run build
	@echo "✓ Frontend build complete!"

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm test

frontend-lint:
	@echo "Linting frontend code..."
	cd frontend && npm run lint || true

# ============================================================================
# DATABASE
# ============================================================================

db-migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

db-reset:
	@echo "WARNING: This will delete all data in the database!"
	@read -p "Are you sure? (y/n) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec backend python -c "from app.db.database import drop_db; drop_db()"; \
		docker-compose exec backend python -c "from app.db.database import init_db; init_db()"; \
		echo "✓ Database reset!"; \
	fi

# ============================================================================
# DEPLOYMENT
# ============================================================================

deploy-build:
	@echo "Building production Docker images..."
	docker-compose build --no-cache
	@echo "✓ Docker images built!"

deploy-up:
	@echo "Starting production containers..."
	docker-compose -f docker-compose.yml up -d
	@echo "✓ Containers running!"

deploy-down:
	@echo "Stopping production containers..."
	docker-compose down
	@echo "✓ Containers stopped!"

# ============================================================================
# UTILITIES
# ============================================================================

clean:
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete!"

status:
	@echo "Docker status:"
	docker-compose ps
