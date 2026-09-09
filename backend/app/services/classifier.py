from app.ml.model_loader import ml_loader

def classify(text: str, features: dict) -> tuple[str, float]:
    """
    Retorna o label e o score de sensacionalismo (1 a 5).
    """
    model = ml_loader.model
    vectorizer = ml_loader.vectorizer
    
    # Se o modelo não foi carregado, usa um mock puramente baseado em heurísticas
    if not model or not vectorizer:
        return _heuristic_mock_classify(features)
        
    try:
        # Pipeline: vectoriza o texto e junta com as features numéricas
        # Para MVP Sklearn, o modelo pode receber só texto se foi um pipeline unificado, 
        # mas aqui faremos a lógica caso seja um text vectorizer
        X_vec = vectorizer.transform([text])
        
        # Obter probabilidades (assumindo modelo que tem predict_proba)
        # Class 1 = Hype
        probs = model.predict_proba(X_vec)[0]
        prob_hype = probs[1] if len(probs) > 1 else probs[0]
        
        # Adicionar peso de heurísticas (ensemble manual simples para MVP)
        heuristic_boost = (features["uppercase_words_percentage"] * 0.5 +
                           min(features["exclamation_density"], 0.2) +
                           features["extreme_adjectives_count"] * 0.1)
                           
        final_prob = min(prob_hype + heuristic_boost, 1.0)
        score = max(min(final_prob * 5, 5.0), 1.0)  # Escala Likert 1-5
        
        return _get_label(score), score

    except Exception:
        # Fallback seguro
        return _heuristic_mock_classify(features)

def _heuristic_mock_classify(features: dict) -> tuple[str, float]:
    """
    Classificador mock baseado apenas nas heurísticas (útil antes do modelo treinar).
    """
    score = 1.5 # Base
    
    score += features["uppercase_words_percentage"] * 10  # Ex: 10% upper -> +1
    score += features["exclamation_density"] * 5
    score += features["extreme_adjectives_count"] * 0.8
    
    score = max(min(score, 5.0), 1.0)
    
    return _get_label(score), score

def _get_label(score: float) -> str:
    if score < 2.5:
        return "Sóbrio"
    elif score < 3.8:
        return "Hype Moderado"
    else:
        return "Hype Elevado"
