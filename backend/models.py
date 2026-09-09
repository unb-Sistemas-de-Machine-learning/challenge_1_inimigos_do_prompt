from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class HighlightedTerm(BaseModel):
    term: str
    weight: float
    category: Literal['alarmist', 'clickbait', 'hype', 'sensationalist'] | str

class SuspiciousClaim(BaseModel):
    claim: str
    explanation: str
    severity: Literal['moderate', 'high']

class AnalyzeResponse(BaseModel):
    email_id: Optional[str] = None
    sensationalism_score: float = Field(..., ge=0.0, le=5.0)
    label: Literal['Sóbrio', 'Hype Moderado', 'Hype Elevado'] | str
    confidence: float = Field(..., ge=0.0, le=1.0)
    highlighted_terms: List[HighlightedTerm]
    disclaimer: str
    disinformation_risk: int = Field(..., ge=0, le=100)
    suspicious_claims: List[SuspiciousClaim]

class AnalyzeRequest(BaseModel):
    email_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    raw_text: str
