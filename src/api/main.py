from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Inimigos do Prompt - API de Inferência",
    version="1.0.0",
    description="Serviço de inferência para detecção de sensacionalismo em newsletters."
)

# Configuração de CORS para permitir requisições da Extensão Chromium
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar chrome-extension://<ID>
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    email_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    raw_text: str = Field(..., min_length=10, description="Texto da newsletter a ser analisado")

class HighlightedTerm(BaseModel):
    term: str
    weight: float
    category: str

class AnalyzeResponse(BaseModel):
    email_id: Optional[str]
    sensationalism_score: float
    label: str
    confidence: float
    highlighted_terms: List[HighlightedTerm]
    disclaimer: str

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "model_loaded": True, "model_version": "baseline-v1"}

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
def analyze_newsletter(payload: AnalyzeRequest):
    text = payload.raw_text
    
    # Exemplo de lógica de extração (PoC Baseline)
    alarmist_keywords = ["destruir", "bombástico", "revolucionar", "assustador", "urgente", "inacreditável"]
    found_terms = []
    
    words = text.split()
    score_acc = 1.0
    
    for word in set(words):
        clean_word = word.strip(".,!?\"'()").lower()
        if clean_word in alarmist_keywords:
            score_acc += 0.65
            found_terms.append(HighlightedTerm(
                term=word,
                weight=0.8,
                category="sensationalist"
            ))
            
    final_score = min(5.0, round(score_acc, 2))
    label = "Sóbrio" if final_score < 2.5 else ("Hype Moderado" if final_score < 3.8 else "Hype Elevado")
    
    return AnalyzeResponse(
        email_id=payload.email_id,
        sensationalism_score=final_score,
        label=label,
        confidence=0.85,
        highlighted_terms=found_terms,
        disclaimer="Análise gerada automaticamente por modelo preditivo."
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)