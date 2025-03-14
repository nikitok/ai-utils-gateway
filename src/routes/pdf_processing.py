from fastapi import APIRouter
from src.schemas.pdf_input import PdfInput
from src.services.pdf_service import process_pdf_to_text_or_tensor

router = APIRouter()

@router.post("/to-tensor/")
def pdf_to_text_or_tensor(input: PdfInput):
    return process_pdf_to_text_or_tensor(input)