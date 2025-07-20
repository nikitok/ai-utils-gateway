from contextlib import asynccontextmanager
import whisper
from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, Body
import logging

from aiutils.core.config import settings
from aiutils.core.logger import get_logger
from aiutils.core.dependencies import container

# Get logger for this module
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    # Set ready flag to False initially
    app.state.is_ready = False

    # loading a big Whisper model
    logger.info("Loading Whisper model...")
    model = whisper.load_model(settings.whisper_model)
    app.state.whisper_model = model
    
    # Initialize DI container with whisper model
    container.whisper_model.override(model)
    logger.info("Whisper model loaded and DI container initialized!")

    # loading a embeding model
    logger.info(f"Loading tokenizer and model: {settings.model_name}...")
    app.state.tokenizer = AutoTokenizer.from_pretrained(settings.model_name)
    app.state.pretrained = AutoModel.from_pretrained(settings.model_name)
    app.state.pretrained_name = settings.model_name.split('/')[-1]
    container.tokenizer.override(app.state.tokenizer)
    container.pretrained_model.override(app.state.pretrained)
    container.model_name.override(app.state.pretrained_name)
    logger.info("Tokenizer model loaded successfully!")
    
    # All models loaded, mark as ready
    app.state.is_ready = True
    logger.info("Application is ready!")

    yield

    logger.info("Shutting down application...")
    app.state.is_ready = False
    app.state.model = None