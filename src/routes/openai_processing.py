from fastapi import APIRouter
from src.schemas.openai_input import OpenAiPdfInput
from src.schemas.openai_input import OpenAiCompletion
from src.services.openai_service import openai_pdf_to_text
from src.services.openai_service import open_ai_completion

router = APIRouter()

@router.post("/pdf-to-text/")
def pdf_to_text(input: OpenAiPdfInput):
    return openai_pdf_to_text(input)

@router.post("/text/")
def text(input: OpenAiCompletion):
    return open_ai_completion(input)