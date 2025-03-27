from fastapi import FastAPI, Body
import uvicorn
from contextlib import asynccontextmanager
import whisper
from transformers import AutoTokenizer, AutoModel

from src.routes.text_processing import router as text_router
from src.routes.pdf_processing import router as pdf_router
from src.routes.mp3_processing import router as mp3_router
from src.routes.openai_processing import router as openai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    # Загружаем модель при запуске приложения
    print("Whisper loading...")
    model = whisper.load_model("small")
    print("Whisper loaded.")
    print("e5 loading...")
    AutoTokenizer.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')
    AutoModel.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')
    print("e5 loaded.")
    #
    # # Добавляем модель в состояние приложения (app.state) для последующего использования
    app.state.whisper_model = model

    yield


    print("Shutting down application...")
    app.state.model = None

fastAPI = FastAPI(
    title="Text to Tensor API",
    description="API to transform text to tensor",
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
    # if not check_database_connection():
    #     return {"status": "unhealthy"}
    return {"status": "ready"}


@fastAPI.get("/")
async def root():
    return {"message": "Text to Tensor API is live!"}


