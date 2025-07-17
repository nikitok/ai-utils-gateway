from pydantic import BaseModel, Field, validator

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    max_length: int = Field(default=512, ge=1, le=2048)
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or only whitespace')
        return v