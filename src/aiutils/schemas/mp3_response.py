from pydantic import BaseModel, Field


class Mp3TranscriptionResponse(BaseModel):
    """API response for MP3 transcription."""
    text: str = Field(..., description="Transcribed text from the audio file")
    language: str = Field(..., description="Language code of the transcribed audio (e.g., 'en', 'es', 'fr')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a sample transcription of the audio file.",
                "language": "en"
            }
        }