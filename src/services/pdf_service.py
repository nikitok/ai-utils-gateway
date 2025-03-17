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

        if format not in ["text", "tensor"]:
            raise CustomHTTPException(
                status_code=400,
                detail="Invalid 'result' parameter. Allowed values are 'text' or 'tensor'."
            )

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

        # Возвращаем результат в зависимости от запроса
        if format == "text":
            return {
                "message": "Text extracted successfully",
                "text": all_text
            }
        elif format == "tensor":
            # Токенизация текста
            inputs = tokenizer(
                all_text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=512
            )

            # Получение эмбеддингов с помощью модели
            with torch.no_grad():
                outputs = model(**inputs)

            token_embeddings = outputs.last_hidden_state
            sentence_embedding = torch.mean(token_embeddings, dim=1).squeeze().tolist()

            return {
                "message": "Tensor generated successfully",
                "tensor": sentence_embedding,
                "tensor_dimension": len(sentence_embedding),
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