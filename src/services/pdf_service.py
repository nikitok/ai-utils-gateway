from http.client import HTTPException

from src.schemas.pdf_input import PdfInput

from pydantic import BaseModel, HttpUrl
import requests
from io import BytesIO
from PyPDF2 import PdfReader


def process_pdf_to_text_or_tensor(input: PdfInput):
    try:
        # Проверяем валидность параметров
        if input.result not in ["txt", "tensor"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid 'result' parameter. Allowed values are 'txt' or 'tensor'."
            )

        # Загружаем PDF
        response = requests.get(input.url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not download the file from the provided URL")

        # Открываем PDF как бинарный поток
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        # Извлекаем текст со всех страниц
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text()

        # Проверяем, был ли текст извлечён
        if not all_text.strip():
            raise HTTPException(status_code=422, detail="Unable to extract text from the provided PDF")

        # Возвращаем результат в зависимости от запроса
        if input.result == "txt":
            return {
                "message": "Text extracted successfully",
                "text": all_text
            }
        elif input.result == "tensor":
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

    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred. Please check the URL, file format, or model configuration."
        }