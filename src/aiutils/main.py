from fastapi import FastAPI
import uvicorn

from aiutils.core.utils import lifespan
from aiutils.routes.text_processing import router as text_router
from aiutils.routes.pdf_processing import router as pdf_router
from aiutils.routes.mp3_processing import router as mp3_router
from aiutils.routes.openai_processing import router as openai_router

fastAPI = FastAPI(
    title="AI utils",
    description="API to transform text to tensor and another utils",
    version="1.0.0",
    lifespan=lifespan
)

fastAPI.include_router(text_router, prefix="/text", tags=["Text Processing"])
fastAPI.include_router(pdf_router, prefix="/pdf", tags=["PDF Processing"])
fastAPI.include_router(mp3_router, prefix="/mp3", tags=["MP3 Processing"])
fastAPI.include_router(openai_router, prefix="/openai", tags=["OpenAI Processing"])

@fastAPI.get("/health/live", tags=["Health Check"])
async def health_live():
    return {"status": "alive"}


@fastAPI.get("/health/ready", tags=["Health Check"])
async def health_ready():
    return {"status": "ready"}


@fastAPI.get("/")
async def root():
    return {"message": "Text to Tensor API is live!"}


