from fastapi import APIRouter, Depends
from typing import Annotated

from aiutils.schemas.openai_input import OpenAiPdfInput, OpenAiCompletionCustomCoT, OpenAiCompletion
from aiutils.services.openai_service import OpenAIService
from aiutils.core.dependencies import get_openai_service

router = APIRouter()


@router.post("/pdf-to-text/",
    summary="Extract text from PDF using GPT-4 Vision",
    response_description="Extracted text from PDF")
async def pdf_to_text(
    input: OpenAiPdfInput,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
):
    """
    Extract text from PDF using GPT-4 Vision API.
    
    Args:
        input: PDF input with URL and API key
        openai_service: OpenAI processing service
        
    Returns:
        Dictionary with extracted text or error details
    """
    return await openai_service.pdf_to_text(input)


@router.post("/text/",
    summary="Generate text completion",
    response_description="Generated text completion")
async def text(
    input: OpenAiCompletion,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
):
    """
    Generate text completion using GPT-4.
    
    Args:
        input: Completion input with text and API key
        openai_service: OpenAI processing service
        
    Returns:
        Dictionary with generated text or error details
    """
    return await openai_service.completion(input)


@router.post("/text_custom_cot/",
    summary="Generate custom chain-of-thought completion",
    response_description="Custom completion result")
async def text_custom_cot(
    input: OpenAiCompletionCustomCoT,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
):
    """
    Generate custom chain-of-thought completion with full control over parameters.
    
    Args:
        input: Custom completion input with body and API key
        openai_service: OpenAI processing service
        
    Returns:
        Dictionary with completion result or error details
    """
    return await openai_service.completion_custom_cot(input)