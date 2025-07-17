from pydantic import BaseModel, Field, field_validator
from typing import Union

class Mp3Input(BaseModel):
    url: str = Field(..., description="URL to MP3 file (http://, https://, or file://)")
    language: str = Field(default="auto", max_length=10, description="Language code for transcription")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://', 'file://')):
            raise ValueError('URL must start with http://, https://, or file://')
        return v
