from pydantic import BaseModel

class PdfInput(BaseModel):
    url: str
