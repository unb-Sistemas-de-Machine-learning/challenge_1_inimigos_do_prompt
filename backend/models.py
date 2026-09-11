from pydantic import BaseModel, Field
from typing import Optional, Literal

# ---------------------------------------------------------------------------
# Fase A: BERTimbau local
# O modelo fine-tunado retorna apenas label binário + confiança.
# ---------------------------------------------------------------------------

class AnalyzeResponse(BaseModel):
    email_id:    Optional[str] = None
    label:       Literal['Sóbrio', 'Sensacionalista']
    confidence:  float = Field(..., ge=0.0, le=1.0, description="Probabilidade da classe predita (0–1)")
    disclaimer:  str = "Resultado gerado por modelo de IA treinado localmente (BERTimbau)."

    # ------------------------------------------------------------------
    # Fase B (futuro) — Integração Gemini para análise enriquecida:
    # highlighted_terms: List[HighlightedTerm]
    # suspicious_claims: List[SuspiciousClaim]
    # disinformation_risk: int
    # sensationalism_score: float  (escala 0–5 gerada pelo Gemini)
    # ------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    email_id: Optional[str] = None
    sender:   Optional[str] = None
    subject:  Optional[str] = None
    raw_text: str
