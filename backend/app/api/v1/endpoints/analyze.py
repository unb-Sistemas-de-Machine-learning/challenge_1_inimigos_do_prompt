import uuid
from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, HighlightedTerm, SuspiciousClaim

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(payload: AnalyzeRequest):
    from app.services.preprocessor import clean_text, extract_hype_features
    from app.services.classifier import classify
    from app.services.explainer import generate_highlighted_terms, extract_suspicious_claims
    from app.utils.cache import analysis_cache, generate_cache_key
    
    # 1. Verifica cache (evita processamento repetido para newsletters comuns)
    cache_key = generate_cache_key(payload.raw_text)
    if cache_key in analysis_cache:
        cached_response = analysis_cache[cache_key]
        # Atualizamos apenas o email_id da resposta cacheadas se o payload informar
        if payload.email_id:
            cached_response.email_id = payload.email_id
        return cached_response
        
    email_id = payload.email_id or str(uuid.uuid4())
    
    # 2. Pré-processamento
    text = clean_text(payload.raw_text)
    features = extract_hype_features(text)
    
    # 3. Classificação
    label, score = classify(text, features)
    
    # 4. Explicabilidade
    highlighted_terms = generate_highlighted_terms(text)
    suspicious_claims = extract_suspicious_claims(text, score)
    
    # Calcula risco de desinformação baseado no score e claims
    risk = (score / 5.0) * 100
    if any(c.severity == 'high' for c in suspicious_claims):
        risk = min(risk + 20, 100)
    
    # Mock de confidence, futuramente vindo do modelo ML
    confidence = 0.85 if score > 3 else 0.95

    response = AnalyzeResponse(
        email_id=email_id,
        sensationalism_score=score,
        label=label,
        confidence=confidence,
        highlighted_terms=highlighted_terms,
        disclaimer='Os resultados são baseados em heurísticas. Analise criticamente.',
        disinformation_risk=round(risk),
        suspicious_claims=suspicious_claims
    )
    
    # Armazena no cache
    analysis_cache[cache_key] = response
    
    return response
