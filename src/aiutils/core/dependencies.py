from fastapi import Request, Depends
from typing import Any


def get_models(request: Request) -> Any:
    return request.app.state


def get_tokenizer(models: Any = Depends(get_models)):
    if not hasattr(models, 'tokenizer'):
        from src.core.exceptions import ModelNotLoadedError
        raise ModelNotLoadedError("tokenizer")
    return models.tokenizer


def get_pretrained_model(models: Any = Depends(get_models)):
    if not hasattr(models, 'pretrained'):
        from src.core.exceptions import ModelNotLoadedError
        raise ModelNotLoadedError("pretrained model")
    return models.pretrained


def get_whisper_model(models: Any = Depends(get_models)):
    if not hasattr(models, 'whisper_model'):
        from src.core.exceptions import ModelNotLoadedError
        raise ModelNotLoadedError("whisper model")
    return models.whisper_model