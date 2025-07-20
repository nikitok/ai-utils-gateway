from io import BytesIO
from typing import Dict, Any, Optional

import torch
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModel

from aiutils.core.exceptions import PDFExtractionError, FileDownloadError, ProcessingError
from aiutils.core.logger import get_logger
from aiutils.core.security import download_file_safely
from aiutils.schemas.pdf_input import PdfInput


class PdfService:
    """Service for processing PDF files."""
    
    def __init__(self, tokenizer: Optional[AutoTokenizer] = None,
                 model: Optional[AutoModel] = None,
                 model_name: Optional[str] = None):
        """
        Initialize PDF service.
        
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
    
    async def process_to_text(self, pdf_input: PdfInput) -> Dict[str, Any]:
        """
        Extract text from PDF.
        
        Args:
            pdf_input: PDF input containing URL
            
        Returns:
            Dictionary with extracted text
            
        Raises:
            FileDownloadError: If PDF download fails
            PDFExtractionError: If text extraction fails
        """
        self.logger.info(f"Processing PDF to text from URL: {pdf_input.url}")
        
        try:
            self.logger.debug("Downloading PDF content")
            pdf_content = await download_file_safely(pdf_input.url)
            self.logger.debug(f"Downloaded PDF, size: {len(pdf_content)} bytes")
            
            pdf_file = BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            page_count = len(reader.pages)
            self.logger.info(f"PDF loaded successfully, pages: {page_count}")

            all_text = ""
            for i, page in enumerate(reader.pages):
                self.logger.debug(f"Extracting text from page {i+1}/{page_count}")
                all_text += page.extract_text()

            if not all_text.strip():
                self.logger.error("No text extracted from PDF")
                raise PDFExtractionError()

            self.logger.info(f"Successfully extracted text from PDF, total characters: {len(all_text)}")
            
            return {
                "text": all_text
            }
        except (FileDownloadError, PDFExtractionError):
            # Re-raise known exceptions
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during PDF text extraction: {str(e)}")
            raise PDFExtractionError(f"Processing error: {str(e)}")
    
    async def process_to_tensor(self, pdf_input: PdfInput) -> Dict[str, Any]:
        """
        Extract text from PDF and convert to embeddings.
        
        Args:
            pdf_input: PDF input containing URL
            
        Returns:
            Dictionary with text and embeddings
            
        Raises:
            FileDownloadError: If PDF download fails
            PDFExtractionError: If text extraction fails
            ProcessingError: If embedding generation fails
        """
        self.logger.info(f"Processing PDF to tensor from URL: {pdf_input.url}")
        
        # First extract text
        text_result = await self.process_to_text(pdf_input)
        text = text_result["text"]
        self.logger.debug(f"Extracted text length: {len(text)} characters")
        
        if not self.tokenizer or not self.model:
            self.logger.error("Model or tokenizer not loaded for tensor generation")
            raise ProcessingError("Model not loaded for tensor generation")
        
        try:
            self.logger.debug(f"Generating embeddings with model: {self.model_name}")
            # Generate embeddings from extracted text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=512  # Default max length for PDFs
            )

            self.logger.debug("Running model inference")
            with torch.no_grad():
                outputs = self.model(**inputs)

            token_embeddings = outputs.last_hidden_state
            sentence_embedding = torch.mean(token_embeddings, dim=1).squeeze().tolist()

            self.logger.info(f"Successfully generated embeddings from PDF, dimension: {len(sentence_embedding)}")
            
            return {
                "text": text,
                "model_name": self.model_name,
                "embedding": sentence_embedding,
                "embedding_dimension": len(sentence_embedding),
            }
        except Exception as e:
            self.logger.error(f"Unexpected error during PDF embedding generation: {str(e)}")
            raise ProcessingError(f"Failed to generate embeddings: {str(e)}")