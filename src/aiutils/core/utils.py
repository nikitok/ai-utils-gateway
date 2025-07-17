from contextlib import asynccontextmanager
import whisper
from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, Body
import logging

from aiutils.core.config import settings
from aiutils.core.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    # Загружаем модель при запуске приложения
    logger.info("Loading Whisper model...")
    model = whisper.load_model(settings.whisper_model)
    logger.info("Whisper model loaded")
    logger.info(f"Loading tokenizer and model: {settings.model_name}")
    app.state.tokenizer = AutoTokenizer.from_pretrained(settings.model_name)
    app.state.pretrained = AutoModel.from_pretrained(settings.model_name)
    app.state.pretrained_name = settings.model_name.split('/')[-1]
    logger.info("Models loaded successfully")
    #
    # # Добавляем модель в состояние приложения (app.state) для последующего использования
    app.state.whisper_model = model

    yield

    logger.info("Shutting down application...")
    app.state.model = None