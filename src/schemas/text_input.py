from pydantic import BaseModel

class TextInput(BaseModel):
    text: str
    max_length: int = 512