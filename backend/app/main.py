from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# CORS configuration to allow Chrome extensions and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em prod, restringir para origin da extensão
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_str)

@app.get("/health", tags=["health"])
async def health_check():
    from app.ml.model_loader import ml_loader
    return {
        "status": "healthy",
        "model_loaded": ml_loader.model is not None,
        "model_backend": settings.model_backend
    }
