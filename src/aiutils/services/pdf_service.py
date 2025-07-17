from io import BytesIO

from PyPDF2 import PdfReader
from fastapi import Request

from aiutils.core.exceptions import PDFExtractionError, FileDownloadError
from aiutils.core.logger import get_logger
from aiutils.core.security import download_file_safely
from aiutils.schemas.pdf_input import PdfInput

logger = get_logger(__name__)


# Создаём свой класс исключений
class CustomHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


async def process_pdf_to_text_or_tensor(input: PdfInput, format: str, request: Request):
    try:
        tokenizer = request.app.state.tokenizer
        model = request.app.state.pretrained
        
        logger.info(f"Processing PDF from URL: {input.url}")
        
        pdf_content = await download_file_safely(input.url)
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
        raise PDFExtractionError(f"Processing error: {str(e)}")


