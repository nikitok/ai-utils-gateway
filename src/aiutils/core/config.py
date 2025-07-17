from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    vespa_cert_path: str = "./security/vespa-cert.pem"
    vespa_key_path: str = "./security/vespa-key.pem"
    vespa_ca_cert_path: str = "./security/clients.pem"
    
    model_name: str = "deepfile/multilingual-e5-small-onnx-qint8"
    whisper_model: str = "small"
    pdf_dpi: int = 400
    max_file_size_mb: int = 50
    request_timeout: int = 30
    
    allowed_domains: Optional[list[str]] = None
    google_genai_use_vertexai: Optional[bool] = None
    proxy_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()