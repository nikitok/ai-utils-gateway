from pydantic import BaseModel, HttpUrl, Field

class Mp3Input(BaseModel):
    url: HttpUrl
    language: str = Field(default="auto", max_length=10)
