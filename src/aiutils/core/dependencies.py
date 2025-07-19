from fastapi import Request, Depends
from typing import Any, Optional
from dependency_injector import containers, providers

import whisper

from aiutils.services.mp3_service import Mp3Service
from aiutils.services.text_service import TextService
from aiutils.services.pdf_service import PdfService
from aiutils.services.openai_service import OpenAIService
from aiutils.core.exceptions import ModelNotLoadedError


class Container(containers.DeclarativeContainer):
    """DI container for application services."""
    
    config = providers.Configuration()

    # Models
    whisper_model = providers.Dependency()
    tokenizer = providers.Dependency()
    pretrained_model = providers.Dependency()
    model_name = providers.Dependency()

    # Services
    mp3_service = providers.Singleton(
        Mp3Service,
        whisper_model=whisper_model
    )
    
    text_service = providers.Singleton(
        TextService,
        tokenizer=tokenizer,
        model=pretrained_model,
        model_name=model_name
    )
    
    pdf_service = providers.Singleton(
        PdfService,
        tokenizer=tokenizer,
        model=pretrained_model,
        model_name=model_name
    )
    
    openai_service = providers.Singleton(
        OpenAIService
    )


container = Container()


def get_models(request: Request) -> Any:
    """Get models from FastAPI app state."""
    return request.app.state


def get_tokenizer(models: Any = Depends(get_models)):
    """Get tokenizer from models."""
    if not hasattr(models, 'tokenizer'):
        raise ModelNotLoadedError("tokenizer")
    return models.tokenizer


def get_pretrained_model(models: Any = Depends(get_models)):
    """Get pretrained model from models."""
    if not hasattr(models, 'pretrained'):
        raise ModelNotLoadedError("pretrained model")
    return models.pretrained


def get_whisper_model(models: Any = Depends(get_models)):
    """Get Whisper model from models."""
    if not hasattr(models, 'whisper_model'):
        raise ModelNotLoadedError("whisper model")
    return models.whisper_model


def get_mp3_service(request: Request) -> Mp3Service:
    """Get MP3 service with injected Whisper model."""
    container.whisper_model.override(request.app.state.whisper_model)
    return container.mp3_service()


def get_text_service(request: Request) -> TextService:
    """Get text service with injected models."""
    container.tokenizer.override(request.app.state.tokenizer)
    container.pretrained_model.override(request.app.state.pretrained)
    container.model_name.override(request.app.state.pretrained_name)
    return container.text_service()


def get_pdf_service(request: Request) -> PdfService:
    """Get PDF service with injected models."""
    container.tokenizer.override(request.app.state.tokenizer)
    container.pretrained_model.override(request.app.state.pretrained)
    container.model_name.override(request.app.state.pretrained_name)
    return container.pdf_service()


def get_openai_service() -> OpenAIService:
    """Get OpenAI service."""
    return container.openai_service()