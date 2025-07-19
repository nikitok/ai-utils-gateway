from fastapi import APIRouter, Depends
from typing import Annotated

from aiutils.schemas.pdf_input import PdfInput
from aiutils.services.pdf_service import PdfService
from aiutils.core.dependencies import get_pdf_service

router = APIRouter()


@router.post("/to-tensor/",
    summary="Extract text from PDF and convert to embeddings",
    response_description="Text and embeddings from PDF")
async def pdf_to_tensor(
    input: PdfInput,
    pdf_service: Annotated[PdfService, Depends(get_pdf_service)]
):
    """
    Extract text from PDF and convert to tensor embeddings.
    
    Args:
        input: PDF input with URL
        pdf_service: PDF processing service
        
    Returns:
        Dictionary with text and embeddings
    """
    return await pdf_service.process_to_tensor(input)


@router.post("/to-text/",
    summary="Extract text from PDF",
    response_description="Extracted text from PDF")
async def pdf_to_text(
    input: PdfInput,
    pdf_service: Annotated[PdfService, Depends(get_pdf_service)]
):
    """
    Extract text content from PDF file.
    
    Args:
        input: PDF input with URL
        pdf_service: PDF processing service
        
    Returns:
        Dictionary with extracted text
    """
    return await pdf_service.process_to_text(input)