from typing import List
from pydantic import BaseModel, Field


class TextToTensorResponse(BaseModel):
    """Response schema for text to tensor endpoint."""
    model_name: str = Field(..., description="Name of the model used")
    max_length: int = Field(..., description="Maximum sequence length used")
    embedding: List[float] = Field(..., description="Text embedding vector")
    embedding_dimension: int = Field(..., description="Dimension of the embedding vector")


class TextToTokensResponse(BaseModel):
    """Response schema for text to tokens endpoint."""
    model_name: str = Field(..., description="Name of the model used")
    text: str = Field(..., description="Original input text")
    max_length: int = Field(..., description="Maximum sequence length used")
    tokens: List[str] = Field(..., description="List of tokens")
    input_ids: List[int] = Field(..., description="List of token IDs")