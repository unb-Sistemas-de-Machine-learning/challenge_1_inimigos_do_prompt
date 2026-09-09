from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class HighlightedTerm(BaseModel):
    term: str
    weight: float
    category: str  # 'alarmist' | 'clickbait' | 'hype' | 'sensationalist' | string

class SuspiciousClaim(BaseModel):
    claim: str
    explanation: str
    severity: Literal['moderate', 'high']

class AnalyzeRequest(BaseModel):
    email_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    raw_text: str

class AnalyzeResponse(BaseModel):
    email_id: Optional[str] = None
    sensationalism_score: float
    label: str  # 'Sóbrio' | 'Hype Moderado' | 'Hype Elevado' | string
    confidence: float
    highlighted_terms: List[HighlightedTerm]
    disclaimer: str
    disinformation_risk: float
    suspicious_claims: List[SuspiciousClaim]
