from pydantic import BaseModel, HttpUrl

class PdfInput(BaseModel):
    url: HttpUrl
