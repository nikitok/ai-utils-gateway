from fastapi import APIRouter, HTTPException, Request

from aiutils.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/live", summary="Liveness probe")
async def health_live():
    """
    Liveness probe for Kubernetes.
    Returns 200 if the service is alive.
    """
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
async def health_ready(request: Request):
    """
    Readiness probe for Kubernetes.
    Returns 200 only when all models are loaded and ready.
    """
    app = request.app
    
    if hasattr(app.state, 'is_ready') and app.state.is_ready:
        return {
            "status": "ready",
            "models": {
                "whisper": hasattr(app.state, 'whisper_model'),
                "tokenizer": hasattr(app.state, 'tokenizer'),
                "embeddings": hasattr(app.state, 'pretrained')
            }
        }
    else:
        # Return 503 Service Unavailable if not ready
        raise HTTPException(
            status_code=503,
            detail="Service is starting up, models are being loaded",
            headers={"Retry-After": "30"}  # Suggest retry after 30 seconds
        )