from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from aiutils.core.utils import lifespan
from aiutils.core.logger import configure_uvicorn_logging
from aiutils.routes.health import router as health_router
from aiutils.routes.text_processing import router as text_router
from aiutils.routes.pdf_processing import router as pdf_router
from aiutils.routes.mp3_processing import router as mp3_router
from aiutils.routes.openai_processing import router as openai_router

# Configure logging before creating the app
configure_uvicorn_logging()

app = FastAPI(
    title="Directual AI Utilities",
    description="AI-powered utilities for Directual platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health_router, prefix="/health", tags=["Health Check"])
app.include_router(text_router, prefix="/text", tags=["Text Processing"])
app.include_router(pdf_router, prefix="/pdf", tags=["PDF Processing"])
app.include_router(mp3_router, prefix="/mp3", tags=["MP3 Processing"])
app.include_router(openai_router, prefix="/openai", tags=["OpenAI Processing"])

# Configure Prometheus metrics
Instrumentator().instrument(app).expose(app)


@app.get("/", summary="Welcome", tags=["General"])
async def root():
    return {
        "message": "Welcome to Directual AI Utilities API",
        "description": "AI-powered tools for text, voice, PDF processing and OpenAI integration",
        "docs": "/docs",
        "health": "/health/ready"
    }


