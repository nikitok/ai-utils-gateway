from fastapi import APIRouter
from aiutils.schemas.mp3_input import Mp3Input
from aiutils.services.mp3_service import process_mp3_to_text

router = APIRouter()

@router.post("/to-text/")
def mp3_to_text(input: Mp3Input):
    return process_mp3_to_text(input, "text")