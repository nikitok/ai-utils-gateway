from pydantic import BaseModel

class OpenAiPdfInput(BaseModel):
    key: str
    url: str

class OpenAiCompletion(BaseModel):
    key: str
    text: str