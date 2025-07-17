# AI Utils API

FastAPI service for ML-powered text, PDF, and audio processing with OpenAI integration.

## Quick Start

```bash
# Install dependencies
uv sync

# Run locally
source .venv/bin/activate
uv run fastapi dev src/aiutils/main.py

# Or run with Docker
docker build -t ai-utils .
docker run -p 80:80 ai-utils
```

## Features

- **Text Processing**: Convert text to embeddings and tokens using multilingual-e5-small model
- **PDF Processing**: Extract and embed text from PDF documents
- **Audio Processing**: Transcribe MP3 files using OpenAI Whisper
- **OpenAI Integration**: Access GPT models for advanced processing
- **Vector Search**: Vespa integration for similarity search

## API Endpoints

- `GET /health/live` - Liveness check
- `GET /health/ready` - Readiness check
- `POST /text/to-tensor/` - Text to embedding vectors
- `POST /text/to-tokens/` - Text tokenization
- `POST /pdf/*` - PDF processing endpoints
- `POST /mp3/*` - Audio transcription endpoints
- `POST /openai/*` - OpenAI-powered endpoints

## Requirements

- Python 3.12+
- System dependencies: `ffmpeg`, `poppler-utils` (included in Docker image)
- Environment variables: OpenAI API key and other configs in `.env`

## Architecture

```
src/
├── aiutils/
│   ├── main.py          # FastAPI app with lifespan context
│   ├── routes/          # API endpoints by processing type
│   ├── services/        # Business logic and integrations
│   ├── schemas/         # Pydantic models
│   └── core/            # Config, security, utilities
└── tests/               # Test suite
```

Models are pre-loaded at startup for optimal performance.