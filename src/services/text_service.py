from src.schemas.text_input import TextInput

from http.client import HTTPException

from fastapi import FastAPI, Body
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
from typing import List

tokenizer = AutoTokenizer.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')
model = AutoModel.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')


def process_text_to_tensor(input: TextInput):
    try:
        inputs = tokenizer(
            input.text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=input.max_length
        )

        with torch.no_grad():
            outputs = model(**inputs)

        token_embeddings = outputs.last_hidden_state
        sentence_embedding = torch.mean(token_embeddings, dim=1).squeeze().tolist()

        return {
            "model_name": MODEL_NAME,
            "max_length": input.max_length,

            "embedding": sentence_embedding,
            "embedding_dimension": len(sentence_embedding),
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred while processing the text. Please check your input or model configuration."
        }


def process_text_to_tokens(input: TextInput):
    try:
        # Токенизация текста
        tokenized = tokenizer(
            input.text,
            truncation=True,
            padding=False,
            max_length=input.max_length
        )

        # Вытаскиваем токены и их числовое представление
        tokens = tokenizer.convert_ids_to_tokens(tokenized["input_ids"])
        input_ids = tokenized["input_ids"]

        return {
            "model_name": MODEL_NAME,
            "text": input.text,
            "max_length": input.max_length,
            "tokens": tokens,
            "input_ids": input_ids
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred while processing the text. Please check your input or model configuration."
        }