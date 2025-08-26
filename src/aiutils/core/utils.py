from contextlib import asynccontextmanager
import os
from pathlib import Path
import whisper
from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, Body
import logging

from aiutils.core.config import settings
from aiutils.core.logger import get_logger
from aiutils.core.dependencies import container

# Get logger for this module
logger = get_logger(__name__)

# Create data directory if it doesn't exist
# Use /app/data in container, ./data locally
DATA_DIR = Path("/app/data") if os.path.exists("/app") else Path("./data")
DATA_DIR.mkdir(exist_ok=True, parents=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    # Set ready flag to False initially
    app.state.is_ready = False

    # loading a big Whisper model
    logger.info("Loading Whisper model...")
    whisper_model_dir = DATA_DIR / f"whisper-{settings.whisper_model}"
    
    # Set environment variable for whisper to use local cache
    os.environ["XDG_CACHE_HOME"] = str(DATA_DIR)
    
    if whisper_model_dir.exists() and any(whisper_model_dir.iterdir()):
        logger.info(f"Loading Whisper model from local cache: {whisper_model_dir}")
        model = whisper.load_model(settings.whisper_model, download_root=str(DATA_DIR))
    else:
        logger.info(f"Downloading Whisper model {settings.whisper_model} to {DATA_DIR}")
        model = whisper.load_model(settings.whisper_model, download_root=str(DATA_DIR))
        logger.info(f"Whisper model downloaded and saved to {DATA_DIR}")
    
    app.state.whisper_model = model
    
    # Initialize DI container with whisper model
    container.whisper_model.override(model)
    logger.info("Whisper model loaded and DI container initialized!")

    # loading a embedding model
    logger.info(f"Loading tokenizer and model: {settings.model_name}...")
    model_cache_dir = DATA_DIR / "transformers"
    model_cache_dir.mkdir(exist_ok=True)
    
    # Set HuggingFace cache directory
    os.environ["TRANSFORMERS_CACHE"] = str(model_cache_dir)
    os.environ["HF_HOME"] = str(model_cache_dir)
    
    # Check if model exists in local cache
    model_local_path = model_cache_dir / settings.model_name.replace("/", "_")
    
    if model_local_path.exists() and any(model_local_path.iterdir()):
        logger.info(f"Loading model from local cache: {model_local_path}")
        app.state.tokenizer = AutoTokenizer.from_pretrained(str(model_local_path))
        app.state.pretrained = AutoModel.from_pretrained(str(model_local_path))
    else:
        logger.info(f"Downloading model {settings.model_name}")
        app.state.tokenizer = AutoTokenizer.from_pretrained(settings.model_name, cache_dir=str(model_cache_dir))
        app.state.pretrained = AutoModel.from_pretrained(settings.model_name, cache_dir=str(model_cache_dir))
        
        # Save model to local path for easier access
        model_local_path.mkdir(parents=True, exist_ok=True)
        app.state.tokenizer.save_pretrained(str(model_local_path))
        app.state.pretrained.save_pretrained(str(model_local_path))
        logger.info(f"Model saved to {model_local_path}")
    
    app.state.pretrained_name = settings.model_name.split('/')[-1]
    container.tokenizer.override(app.state.tokenizer)
    container.pretrained_model.override(app.state.pretrained)
    container.model_name.override(app.state.pretrained_name)
    logger.info("Tokenizer and embedding model loaded successfully!")
    
    # All models loaded, mark as ready
    app.state.is_ready = True
    logger.info("Application is ready!")

    yield

    logger.info("Shutting down application...")
    app.state.is_ready = False
    app.state.model = None