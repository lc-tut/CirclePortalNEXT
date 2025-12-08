# CirclePortal Backend

FastAPI backend for CirclePortal.

## Setup

```bash
# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Start database (Docker required)
docker compose up -d

# Run development server
uv run uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Configuration
│   ├── db/             # Database session
│   ├── models/         # SQLModel classes
│   ├── services/       # Business logic
│   └── main.py         # Application entry point
├── static/             # Static files (images)
├── tests/              # Test files
└── pyproject.toml      # Python dependencies
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```
