# Data Parser FastAPI Application

A modern FastAPI application for data parsing built with `uv` for fast dependency management.

## Features

- FastAPI web framework
- Async/await support
- Pydantic for data validation
- Modular project structure
- Development tools (pytest, black, isort, mypy)

## Requirements

- Python 3.8+
- uv (for dependency management)

## Installation

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
uv pip install -e .[dev]
```

3. Activate the virtual environment:
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

## Running the Application

### Development Server
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Development

### Code Formatting
```bash
uv run black .
uv run isort .
```

### Linting
```bash
uv run flake8
uv run mypy .
```

### Testing
```bash
uv run pytest
```

## Project Structure

```
data-parser/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   └── __init__.py
│   ├── routers/             # API route handlers
│   │   └── __init__.py
│   └── services/            # Business logic
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation
