from fastapi import FastAPI, Body
import uvicorn

from src.routes.text_processing import router as text_router
from src.routes.pdf_processing import router as pdf_router

fastAPI = FastAPI(
    title="Text to Tensor API",
    description="API to transform text to tensor",
    version="1.0.0"
)

fastAPI.include_router(text_router, prefix="/text", tags=["Text Processing"])
fastAPI.include_router(pdf_router, prefix="/pdf", tags=["PDF Processing"])

@fastAPI.get("/")
async def root():
    return {"message": "Text to Tensor API is live!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:fastAPI", host="0.0.0.0", port=8000, reload=True)
