from pydantic import BaseModel

class Mp3Input(BaseModel):
    url: str
    language: str = 512
