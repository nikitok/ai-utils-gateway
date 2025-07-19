import logging
from typing import List, Optional
from dataclasses import dataclass

import torch
from transformers import AutoTokenizer, AutoModel

from aiutils.core.exceptions import ModelNotLoadedError, ProcessingError
from aiutils.core.logger import get_logger
from aiutils.schemas.text_input import TextInput


@dataclass
class TextEmbeddingResult:
    """Result of text embedding generation."""
    model_name: str
    max_length: int
    embedding: List[float]
    embedding_dimension: int


@dataclass
class TextTokenizationResult:
    """Result of text tokenization."""
    model_name: str
    text: str
    max_length: int
    tokens: List[str]
    input_ids: List[int]


class TextService:
    """Service for processing text with transformer models."""
    
    def __init__(self, tokenizer: Optional[AutoTokenizer] = None, 
                 model: Optional[AutoModel] = None,
                 model_name: Optional[str] = None):
        """
        Initialize text service.
        
        Args:
            tokenizer: Pre-loaded tokenizer. If None, should be set later.
            model: Pre-loaded model. If None, should be set later.
            model_name: Name of the model being used.
        """
        self.tokenizer = tokenizer
        self.model = model
        self.model_name = model_name or "multilingual-e5-small"
        self.logger = get_logger(self.__class__.__name__)
    
    def set_models(self, tokenizer: AutoTokenizer, model: AutoModel, model_name: str) -> None:
        """Set or update the tokenizer and model."""
        self.tokenizer = tokenizer
        self.model = model
        self.model_name = model_name
    
    def process_to_tensor(self, input: TextInput) -> TextEmbeddingResult:
        """
        Process text to tensor embeddings.
        
        Args:
            input: Text input containing text and max_length
            
        Returns:
            TextEmbeddingResult with embeddings and metadata
            
        Raises:
            ModelNotLoadedError: If tokenizer or model not loaded
            ProcessingError: If embedding generation fails
        """
        if not self.tokenizer or not self.model:
            raise ModelNotLoadedError("multilingual-e5-small")
        
        try:
            inputs = self.tokenizer(
                input.text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=input.max_length
            )

            with torch.no_grad():
                outputs = self.model(**inputs)

            token_embeddings = outputs.last_hidden_state
            sentence_embedding = torch.mean(token_embeddings, dim=1).squeeze().tolist()

            return TextEmbeddingResult(
                model_name=self.model_name,
                max_length=input.max_length,
                embedding=sentence_embedding,
                embedding_dimension=len(sentence_embedding)
            )
        except ModelNotLoadedError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {str(e)}")
            raise ProcessingError(f"Failed to generate embeddings: {str(e)}")

    def process_to_tokens(self, input: TextInput) -> TextTokenizationResult:
        """
        Process text to tokens.
        
        Args:
            input: Text input containing text and max_length
            
        Returns:
            TextTokenizationResult with tokens and metadata
            
        Raises:
            ModelNotLoadedError: If tokenizer not loaded
            ProcessingError: If tokenization fails
        """
        if not self.tokenizer:
            raise ModelNotLoadedError("tokenizer")
        
        try:
            # Text tokenization
            tokenized = self.tokenizer(
                input.text,
                truncation=True,
                padding=False,
                max_length=input.max_length
            )

            # Extract tokens and their numerical representation
            tokens = self.tokenizer.convert_ids_to_tokens(tokenized["input_ids"])
            input_ids = tokenized["input_ids"]

            return TextTokenizationResult(
                model_name=self.model_name,
                text=input.text,
                max_length=input.max_length,
                tokens=tokens,
                input_ids=input_ids
            )
        except ModelNotLoadedError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to tokenize text: {str(e)}")
            raise ProcessingError(f"Failed to tokenize text: {str(e)}")