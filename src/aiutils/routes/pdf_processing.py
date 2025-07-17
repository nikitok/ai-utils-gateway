from fastapi import APIRouter
from aiutils.schemas.pdf_input import PdfInput
from aiutils.services.pdf_service import process_pdf_to_text_or_tensor

router = APIRouter()

@router.post("/to-tensor/")
async def pdf_to_tensor(input: PdfInput):
    return await process_pdf_to_text_or_tensor(input, "tensor")

@router.post("/to-text/")
async def pdf_to_text(input: PdfInput):
    return await process_pdf_to_text_or_tensor(input, "text")