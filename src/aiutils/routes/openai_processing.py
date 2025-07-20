from fastapi import APIRouter, Depends
from typing import Annotated, Dict, Any, Union

from aiutils.schemas.openai_input import OpenAiPdfInput, OpenAiCompletionCustomCoT, OpenAiCompletion
from aiutils.schemas.openai_response import (
    OpenAIPdfToTextResponse, 
    OpenAICompletionResponse, 
    OpenAICompletionCustomResponse
)
from aiutils.services.openai_service import OpenAIService
from aiutils.core.dependencies import get_openai_service

router = APIRouter()


@router.post("/pdf-to-text/",
    summary="Extract text from PDF using GPT-4 Vision",
    response_description="Extracted text from PDF",
    response_model=OpenAIPdfToTextResponse)
async def pdf_to_text(
    input: OpenAiPdfInput,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
) -> Union[OpenAIPdfToTextResponse, Dict[str, Any]]:
    """
    Extract text from PDF using GPT-4 Vision API.
    
    Args:
        input: PDF input with URL and API key
        openai_service: OpenAI processing service
        
    Returns:
        OpenAIPdfToTextResponse with extracted text or error details
    """
    result = await openai_service.pdf_to_text(input)
    
    # Convert internal data class to response schema
    return OpenAIPdfToTextResponse(
        text=result.text,
        status_code=result.status_code,
        detail=result.detail
    )


@router.post("/text/",
    summary="Generate text completion",
    response_description="Generated text completion",
    response_model=OpenAICompletionResponse)
async def text(
    input: OpenAiCompletion,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
) -> Union[OpenAICompletionResponse, Dict[str, Any]]:
    """
    Generate text completion using GPT-4.
    
    Args:
        input: Completion input with text and API key
        openai_service: OpenAI processing service
        
    Returns:
        OpenAICompletionResponse with generated text or error details
    """
    result = await openai_service.completion(input)
    
    # Convert internal data class to response schema
    return OpenAICompletionResponse(
        text=result.text,
        status_code=result.status_code,
        detail=result.detail
    )


@router.post("/text_custom_cot/",
    summary="Generate custom chain-of-thought completion",
    response_description="Custom completion result",
    response_model=OpenAICompletionCustomResponse)
async def text_custom_cot(
    input: OpenAiCompletionCustomCoT,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
) -> Union[OpenAICompletionCustomResponse, Dict[str, Any]]:
    """
    Generate custom chain-of-thought completion with full control over parameters.
    
    Args:
        input: Custom completion input with body and API key
        openai_service: OpenAI processing service
        
    Returns:
        OpenAICompletionCustomResponse with completion result or error details
    """
    result = await openai_service.completion_custom_cot(input)
    
    # Convert internal data class to response schema
    return OpenAICompletionCustomResponse(
        text=result.text,
        status_code=result.status_code,
        detail=result.detail
    )