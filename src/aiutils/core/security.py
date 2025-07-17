from urllib.parse import urlparse
from aiutils.core.config import settings
from aiutils.core.exceptions import FileDownloadError
import httpx


def validate_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        
        if settings.allowed_domains:
            domain = parsed.netloc.lower()
            return any(domain.endswith(allowed.lower()) for allowed in settings.allowed_domains)
        
        return parsed.scheme in ['http', 'https']
    except Exception:
        return False


async def download_file_safely(url: str, max_size_mb: int = None) -> bytes:
    if not validate_url(url):
        raise FileDownloadError(url, 403)
    
    max_size = (max_size_mb or settings.max_file_size_mb) * 1024 * 1024
    
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        async with client.stream("GET", url) as response:
            if response.status_code != 200:
                raise FileDownloadError(url, response.status_code)
            
            content = bytearray()
            async for chunk in response.aiter_bytes(chunk_size=8192):
                content.extend(chunk)
                if len(content) > max_size:
                    raise FileDownloadError(f"File too large (max {max_size_mb}MB)", 413)
            
            return bytes(content)