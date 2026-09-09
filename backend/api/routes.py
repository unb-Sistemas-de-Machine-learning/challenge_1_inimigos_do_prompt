from fastapi import APIRouter, HTTPException
from models import AnalyzeRequest, AnalyzeResponse
from services.llm import analyze_email_text

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_email(request: AnalyzeRequest):
    try:
        response = await analyze_email_text(request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
