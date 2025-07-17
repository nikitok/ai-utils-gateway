from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from aiutils.schemas.mp3_input import Mp3Input
from aiutils.schemas.mp3_response import Mp3TranscriptionResponse
from aiutils.services.mp3_service import Mp3Service, Mp3DownloadError, Mp3TranscriptionError, Mp3ProcessingError
from aiutils.core.logger import get_logger
from aiutils.core.dependencies import get_mp3_service

logger = get_logger(__name__)
router = APIRouter()


@router.post("/to-text/", 
    summary="Transcribe MP3 to text",
    response_description="Transcribed text and detected language",
    response_model=Mp3TranscriptionResponse)
async def mp3_to_text(
    mp3_input: Mp3Input,
    mp3_service: Annotated[Mp3Service, Depends(get_mp3_service)]
) -> Mp3TranscriptionResponse:
    """
    Transcribe MP3 audio to text using Whisper.
    
    Supports URLs with http://, https://, or file:// schemes.
    
    Args:
        mp3_input: Input containing MP3 URL and optional language
        mp3_service: MP3 processing service
        
    Returns:
        Mp3TranscriptionResponse with transcribed text and detected language
        
    Raises:
        Mp3DownloadError: If MP3 download fails
        Mp3TranscriptionError: If transcription fails
        Mp3ProcessingError: If processing fails
    """
    try:
        result = await mp3_service.mp3ToText(mp3_input)
        # Convert internal TranscribeResult to API Mp3TranscriptionResponse
        return Mp3TranscriptionResponse(
            text=result.text,
            language=result.language
        )
        
    except Mp3DownloadError as e:
        logger.error(f"MP3 download failed: {e.detail}")
        raise
        
    except Mp3TranscriptionError as e:
        logger.error(f"MP3 transcription failed: {e.detail}")
        raise
        
    except Mp3ProcessingError as e:
        logger.error(f"MP3 processing failed: {e.detail}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in MP3 processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during MP3 processing: {str(e)}"
        )