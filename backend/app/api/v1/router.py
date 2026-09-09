from fastapi import APIRouter
from app.api.v1.endpoints import analyze, feedback

api_router = APIRouter()
api_router.include_router(analyze.router, tags=["analyze"])
api_router.include_router(feedback.router, tags=["feedback"])
