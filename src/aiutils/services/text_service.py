from aiutils.schemas.text_input import TextInput
from aiutils.core.exceptions import ModelNotLoadedError, ProcessingError

from fastapi import FastAPI, Body
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
from typing import List
import logging

logger = logging.getLogger(__name__)

# MODEL_NAME = "multilingual-e5-small-onnx-qint8"
# tokenizer = AutoTokenizer.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')
# model = AutoModel.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')


def process_text_to_tensor(input: TextInput, models):
    
    if not hasattr(models, 'tokenizer') or not hasattr(models, 'pretrained'):
        raise ModelNotLoadedError("multilingual-e5-small")
        
    tokenizer = models.tokenizer
    model = models.pretrained
    model_name = models.pretrained_name

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
            "model_name": model_name,
            "max_length": input.max_length,

            "embedding": sentence_embedding,
            "embedding_dimension": len(sentence_embedding),
        }
    except ModelNotLoadedError:
        raise
    except Exception as e:
        raise ProcessingError(f"Failed to generate embeddings: {str(e)}")


def process_text_to_tokens(input: TextInput, models):
    
    if not hasattr(models, 'tokenizer'):
        raise ModelNotLoadedError("tokenizer")
        
    tokenizer = models.tokenizer
    model = models.pretrained
    model_name = models.pretrained_name

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
            "model_name": model_name,
            "text": input.text,
            "max_length": input.max_length,
            "tokens": tokens,
            "input_ids": input_ids
        }
    except ModelNotLoadedError:
        raise
    except Exception as e:
        raise ProcessingError(f"Failed to tokenize text: {str(e)}")