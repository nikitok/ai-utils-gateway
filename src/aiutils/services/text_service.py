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
        self.logger.info(f"Setting models, model name: {model_name}")
        self.tokenizer = tokenizer
        self.model = model
        self.model_name = model_name
        self.logger.debug("Models successfully set")
    
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
        self.logger.info(f"Processing text to tensor, text length: {len(input.text)}, max_length: {input.max_length}")
        
        if not self.tokenizer or not self.model:
            self.logger.error("Model or tokenizer not loaded")
            raise ModelNotLoadedError("multilingual-e5-small")
        
        try:
            self.logger.debug(f"Tokenizing text with model: {self.model_name}")
            inputs = self.tokenizer(
                input.text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=input.max_length
            )

            self.logger.debug("Generating embeddings")
            with torch.no_grad():
                outputs = self.model(**inputs)

            token_embeddings = outputs.last_hidden_state
            sentence_embedding = torch.mean(token_embeddings, dim=1).squeeze().tolist()

            self.logger.info(f"Successfully generated embeddings, dimension: {len(sentence_embedding)}")
            
            return TextEmbeddingResult(
                model_name=self.model_name,
                max_length=input.max_length,
                embedding=sentence_embedding,
                embedding_dimension=len(sentence_embedding)
            )
        except ModelNotLoadedError:
            # Re-raise known exceptions
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during embedding generation: {str(e)}")
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
        self.logger.info(f"Processing text to tokens, text length: {len(input.text)}, max_length: {input.max_length}")
        
        if not self.tokenizer:
            self.logger.error("Tokenizer not loaded")
            raise ModelNotLoadedError("tokenizer")
        
        try:
            self.logger.debug(f"Tokenizing text with model: {self.model_name}")
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

            self.logger.info(f"Successfully tokenized text, token count: {len(tokens)}")
            
            return TextTokenizationResult(
                model_name=self.model_name,
                text=input.text,
                max_length=input.max_length,
                tokens=tokens,
                input_ids=input_ids
            )
        except ModelNotLoadedError:
            # Re-raise known exceptions
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during tokenization: {str(e)}")
            raise ProcessingError(f"Failed to tokenize text: {str(e)}")