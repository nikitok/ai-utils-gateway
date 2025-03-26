from pydantic import BaseModel
import requests
from io import BytesIO
from PyPDF2 import PdfReader
import torch

from src.schemas.pdf_input import PdfInput

from transformers import AutoTokenizer, AutoModel
import torch

MODEL_NAME = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)


# Создаём свой класс исключений
class CustomHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


def process_pdf_to_text_or_tensor(input: PdfInput, format: str):
    try:

        print(f"Processing PDF from URL: {input.url}")
        response = requests.get(input.url)
        if response.status_code != 200:
            raise CustomHTTPException(
                status_code=400,
                detail="Could not download the file from the provided URL"
            )

        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)

        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text()

        if not all_text.strip():
            raise CustomHTTPException(
                status_code=422,
                detail="Unable to extract text from the provided PDF"
            )

        return {
            "text": all_text
        }
    except CustomHTTPException as custom_exc:
        return {
            "status_code": custom_exc.status_code,
            "detail": custom_exc.detail
        }
    except Exception as e:
        return {
            "status_code": 500,
            "detail": f"An unexpected error occurred: {str(e)}"
        }


if __name__ == "__main__":
    e = process_pdf_to_text_or_tensor(
        PdfInput(url="https://api.directual.com/fileUploaded/rag/web/9644bf00-83c6-4ae4-80b8-927aba929f73.pdf"),
        format="text")
    print(e)
