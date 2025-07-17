from fastapi import APIRouter, Depends
from aiutils.schemas.text_input import TextInput
from aiutils.services.text_service import process_text_to_tensor, process_text_to_tokens
from aiutils.core.dependencies import get_models

router = APIRouter()

@router.post("/to-tensor/")
def text_to_tensor(input: TextInput, models = Depends(get_models)):
    return process_text_to_tensor(input, models)


@router.post("/to-tokens/")
def text_to_tokens(input: TextInput, models = Depends(get_models)):
    return process_text_to_tokens(input, models)