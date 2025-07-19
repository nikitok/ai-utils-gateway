from fastapi import APIRouter, Depends
from typing import Annotated

from aiutils.schemas.text_input import TextInput
from aiutils.schemas.text_response import TextToTensorResponse, TextToTokensResponse
from aiutils.services.text_service import TextService
from aiutils.core.dependencies import get_text_service

router = APIRouter()


@router.post("/to-tensor/",
    summary="Convert text to embeddings",
    response_description="Text embeddings and metadata",
    response_model=TextToTensorResponse)
async def text_to_tensor(
    input: TextInput,
    text_service: Annotated[TextService, Depends(get_text_service)]
) -> TextToTensorResponse:
    """
    Convert text to tensor embeddings using multilingual-e5-small model.
    
    Args:
        input: Text input with text and max_length
        text_service: Text processing service
        
    Returns:
        TextToTensorResponse with embeddings and metadata
    """
    result = text_service.process_to_tensor(input)
    
    # Convert internal data class to response schema
    return TextToTensorResponse(
        model_name=result.model_name,
        max_length=result.max_length,
        embedding=result.embedding,
        embedding_dimension=result.embedding_dimension
    )


@router.post("/to-tokens/",
    summary="Tokenize text",
    response_description="Tokenized text and token IDs",
    response_model=TextToTokensResponse)
async def text_to_tokens(
    input: TextInput,
    text_service: Annotated[TextService, Depends(get_text_service)]
) -> TextToTokensResponse:
    """
    Tokenize text using multilingual-e5-small tokenizer.
    
    Args:
        input: Text input with text and max_length
        text_service: Text processing service
        
    Returns:
        TextToTokensResponse with tokens and token IDs
    """
    result = text_service.process_to_tokens(input)
    
    # Convert internal data class to response schema
    return TextToTokensResponse(
        model_name=result.model_name,
        text=result.text,
        max_length=result.max_length,
        tokens=result.tokens,
        input_ids=result.input_ids
    )