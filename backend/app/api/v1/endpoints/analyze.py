import uuid
from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, HighlightedTerm, SuspiciousClaim

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(payload: AnalyzeRequest):
    from app.services.preprocessor import clean_text, extract_hype_features
    from app.services.classifier import classify
    from app.services.explainer import generate_highlighted_terms
    from app.utils.cache import analysis_cache, generate_cache_key
    from app.ml.model_loader import ml_loader
    import re
    
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
    
    # 3. ClassificaçãoConcluí as tarefas solicitadas! Aqui está um resumo das alterações que fiz:

Endpoint e Instanciação Localizados: O endpoint POST /analyze e a montagem da resposta final (AnalyzeResponse) foram identificados em backend/app/api/v1/endpoints/analyze.py.
Divisão de Frases: Inseri a importação do módulo re e incluí a lógica [f.strip() for f in re.split(r'[.!?]+', text) if f.strip()] para dividir o texto original antes da montagem da resposta.
Injeção do ML Loader: Substiui a antiga função extract_suspicious_claims e incluí a importação e chamada de risk_score, claims_list = ml_loader.predict_claims_risk(frases_extraidas).
Atualização da Resposta Final: O disinformation_risk agora recebe o risk_score de forma direta e sem os cálculos heurísticos de outrora. O campo suspicious_claims também recebe diretamente a saída claims_list.
Ajustes de Schema (Pydantic): Verifiquei o modelo em backend/app/schemas/analyze.py. Notei que o classificador estava retornando "medium", mas o Pydantic só permitia Literal['moderate', 'high'] para o campo de severidade. Adicionei os valores 'low', e 'medium' aos permitidos para prevenir possíveis falhas de validação.
Se houver mais alguma melhoria, só pedir!
    label, score = classify(text, features)
    
    # 4. Explicabilidade
    highlighted_terms = generate_highlighted_terms(text)
    
    # Dividir texto do payload em frases simples
    frases_extraidas = [f.strip() for f in re.split(r'[.!?]+', text) if f.strip()]
    
    risk_score, claims_list = ml_loader.predict_claims_risk(frases_extraidas)
    
    # Mock de confidence, futuramente vindo do modelo ML
    confidence = 0.85 if score > 3 else 0.95

    response = AnalyzeResponse(
        email_id=email_id,
        sensationalism_score=score,
        label=label,
        confidence=confidence,
        highlighted_terms=highlighted_terms,
        disclaimer='Os resultados são baseados em heurísticas. Analise criticamente.',
        disinformation_risk=risk_score,
        suspicious_claims=claims_list
    )
    
    # Armazena no cache
    analysis_cache[cache_key] = response
    
    return response
