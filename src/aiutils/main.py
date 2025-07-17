from fastapi import FastAPI
from aiutils.core.utils import lifespan
from aiutils.core.logger import configure_uvicorn_logging
from aiutils.routes.text_processing import router as text_router
from aiutils.routes.pdf_processing import router as pdf_router
from aiutils.routes.mp3_processing import router as mp3_router
from aiutils.routes.openai_processing import router as openai_router

# Configure logging before creating the app
configure_uvicorn_logging()

app = FastAPI(
    title="AI utils",
    description="API to transform text to tensor and another utils",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(text_router, prefix="/text", tags=["Text Processing"])
app.include_router(pdf_router, prefix="/pdf", tags=["PDF Processing"])
app.include_router(mp3_router, prefix="/mp3", tags=["MP3 Processing"])
app.include_router(openai_router, prefix="/openai", tags=["OpenAI Processing"])

@app.get("/health/live", tags=["Health Check"])
async def health_live():
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health Check"])
async def health_ready():
    return {"status": "ready"}


@app.get("/")
async def root():
    return {"message": "API to transform text to tensor and more utilities"}


