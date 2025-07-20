from typing import Optional, Union
from pydantic import BaseModel, Field


class OpenAIPdfToTextResponse(BaseModel):
    """Response schema for OpenAI PDF to text endpoint."""
    text: Optional[str] = Field(None, description="Extracted text from PDF")
    status_code: Optional[int] = Field(None, description="Error status code if failed")
    detail: Optional[str] = Field(None, description="Error detail message if failed")


class OpenAICompletionResponse(BaseModel):
    """Response schema for OpenAI completion endpoint."""
    text: Optional[str] = Field(None, description="Generated completion text")
    status_code: Optional[int] = Field(None, description="Error status code if failed")
    detail: Optional[str] = Field(None, description="Error detail message if failed")


class OpenAICompletionCustomResponse(BaseModel):
    """Response schema for OpenAI custom chain-of-thought completion endpoint."""
    text: Optional[str] = Field(None, description="Generated text or JSON response")
    status_code: Optional[int] = Field(None, description="Error status code if failed")
    detail: Optional[str] = Field(None, description="Error detail message if failed")