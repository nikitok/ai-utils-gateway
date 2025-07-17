from fastapi import Request, Depends
from typing import Any, Optional
from dependency_injector import containers, providers

import whisper

from aiutils.services.mp3_service import Mp3Service
from aiutils.core.exceptions import ModelNotLoadedError


class Container(containers.DeclarativeContainer):
    """DI container for application services."""
    
    config = providers.Configuration()

    whisper_model = providers.Dependency()

    mp3_service = providers.Singleton(
        Mp3Service,
        whisper_model=whisper_model
    )

container = Container()


def get_models(request: Request) -> Any:
    return request.app.state


def get_tokenizer(models: Any = Depends(get_models)):
    if not hasattr(models, 'tokenizer'):
        raise ModelNotLoadedError("tokenizer")
    return models.tokenizer


def get_pretrained_model(models: Any = Depends(get_models)):
    if not hasattr(models, 'pretrained'):
        raise ModelNotLoadedError("pretrained model")
    return models.pretrained


def get_whisper_model(models: Any = Depends(get_models)):
    if not hasattr(models, 'whisper_model'):
        raise ModelNotLoadedError("whisper model")
    return models.whisper_model


def get_mp3_service(request: Request) -> Mp3Service:
    container.whisper_model.override(request.app.state.whisper_model)
    return container.mp3_service()
