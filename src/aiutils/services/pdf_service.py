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
        self.tokenizer = tokenizer
        self.model = model
        self.model_name = model_name
    
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
        try:
            self.logger.info(f"Processing PDF from URL: {pdf_input.url}")
            
            pdf_content = await download_file_safely(pdf_input.url)
            pdf_file = BytesIO(pdf_content)
            reader = PdfReader(pdf_file)

            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text()

            if not all_text.strip():
                raise PDFExtractionError()

            return {
                "text": all_text
            }
        except (FileDownloadError, PDFExtractionError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during PDF processing: {str(e)}")
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
        # First extract text
        text_result = await self.process_to_text(pdf_input)
        text = text_result["text"]
        
        if not self.tokenizer or not self.model:
            raise ProcessingError("Model not loaded for tensor generation")
        
        try:
            # Generate embeddings from extracted text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=512  # Default max length for PDFs
            )

            with torch.no_grad():
                outputs = self.model(**inputs)

            token_embeddings = outputs.last_hidden_state
            sentence_embedding = torch.mean(token_embeddings, dim=1).squeeze().tolist()

            return {
                "text": text,
                "model_name": self.model_name,
                "embedding": sentence_embedding,
                "embedding_dimension": len(sentence_embedding),
            }
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings from PDF: {str(e)}")
            raise ProcessingError(f"Failed to generate embeddings: {str(e)}")