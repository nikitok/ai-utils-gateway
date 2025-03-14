from fastapi import APIRouter
from src.schemas.text_input import TextInput
from src.services.text_service import process_text_to_tensor, process_text_to_tokens

router = APIRouter()

@router.post("/to-tensor/")
def text_to_tensor(input: TextInput):
    return process_text_to_tensor(input)


@router.post("/to-tokens/")
def text_to_tokens(input: TextInput):
    return process_text_to_tokens(input)