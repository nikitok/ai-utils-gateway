from fastapi import HTTPException
from typing import Any, Dict, Optional


class ModelNotLoadedError(HTTPException):
    def __init__(self, model_name: str):
        super().__init__(
            status_code=503,
            detail=f"Model {model_name} is not loaded. Please try again later."
        )


class InvalidInputError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=message
        )


class FileDownloadError(HTTPException):
    def __init__(self, url: str, status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail=f"Failed to download file from URL: {url}"
        )


class PDFExtractionError(HTTPException):
    def __init__(self, message: str = "Unable to extract text from PDF"):
        super().__init__(
            status_code=422,
            detail=message
        )


class ProcessingError(HTTPException):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            status_code=status_code,
            detail=f"Processing error: {message}"
        )


class Mp3ProcessingError(HTTPException):
    """Base exception for MP3 processing errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            status_code=status_code,
            detail=f"MP3 processing error: {message}"
        )


class Mp3DownloadError(Mp3ProcessingError):
    """Exception for MP3 download failures."""
    def __init__(self, url: str, reason: Optional[str] = None):
        message = f"Failed to download MP3 from {url}"
        if reason:
            message += f": {reason}"
        super().__init__(message, status_code=400)


class Mp3TranscriptionError(Mp3ProcessingError):
    """Exception for MP3 transcription failures."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Failed to transcribe audio: {reason}",
            status_code=422
        )


class CustomHTTPException(Exception):
    """Custom HTTP exception for non-FastAPI contexts."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class OpenAIProcessingError(HTTPException):
    """Base exception for OpenAI processing errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            status_code=status_code,
            detail=f"OpenAI processing error: {message}"
        )


class OpenAIVisionError(OpenAIProcessingError):
    """Exception for OpenAI Vision API failures."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Vision API failed: {reason}",
            status_code=422
        )


class OpenAICompletionError(OpenAIProcessingError):
    """Exception for OpenAI completion failures."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Completion failed: {reason}",
            status_code=422
        )