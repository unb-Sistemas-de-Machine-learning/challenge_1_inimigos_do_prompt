from fastapi import APIRouter, HTTPException
from models import AnalyzeRequest, AnalyzeResponse
# Fase A: classificador BERTimbau local
# Fase B (futuro): trocar por services.hybrid que combina BERTimbau + Gemini
from services.bertimbau import analyze_email_text

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
