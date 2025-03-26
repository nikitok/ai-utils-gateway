from fastapi import FastAPI, Body
import uvicorn

from src.routes.text_processing import router as text_router
from src.routes.pdf_processing import router as pdf_router
from src.routes.mp3_processing import router as mp3_router
from src.routes.openai_processing import router as openai_router

fastAPI = FastAPI(
    title="Text to Tensor API",
    description="API to transform text to tensor",
    version="1.0.0"
)

fastAPI.include_router(text_router, prefix="/text", tags=["Text Processing"])
fastAPI.include_router(pdf_router, prefix="/pdf", tags=["PDF Processing"])
fastAPI.include_router(mp3_router, prefix="/mp3", tags=["MP3 Processing"])
fastAPI.include_router(openai_router, prefix="/openai", tags=["OpenAI Processing"])

@fastAPI.get("/")
async def root():
    return {"message": "Text to Tensor API is live!"}