import torch
import logging
from app.ml.model_loader import ml_loader

logger = logging.getLogger(__name__)

def classify(text: str, features: dict) -> tuple[str, float]:
    """
    Retorna o label e o score de sensacionalismo (1 a 5).
    """
    backend_type = ml_loader.backend_type
    model = ml_loader.model
    
    if backend_type == "bertimbau" and model is not None and ml_loader.tokenizer is not None:
        try:
            tokenizer = ml_loader.tokenizer
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)[0]
                
            # Classe 1 = sensacionalista (Hype)
            prob_hype = probs[1].item() if len(probs) > 1 else probs[0].item()
            
            # Pequeno ajuste heurístico para textos com caixa alta/exclamações
            heuristic_boost = (features.get("uppercase_words_percentage", 0) * 0.2 +
                               min(features.get("exclamation_density", 0), 0.1) +
                               features.get("extreme_adjectives_count", 0) * 0.05)
            
            final_prob = min(prob_hype + heuristic_boost, 1.0)
            score = max(min(1.0 + final_prob * 4.0, 5.0), 1.0)  # Mapeia 0-1 em escala 1-5
            
            return _get_label(score), round(score, 2)
        except Exception as e:
            logger.error(f"Erro durante classificação BERTimbau: {e}")
            return _heuristic_mock_classify(features)

    vectorizer = ml_loader.vectorizer
    if model is not None and vectorizer is not None:
        try:
            X_vec = vectorizer.transform([text])
            probs = model.predict_proba(X_vec)[0]
            prob_hype = probs[1] if len(probs) > 1 else probs[0]
            
            heuristic_boost = (features.get("uppercase_words_percentage", 0) * 0.5 +
                               min(features.get("exclamation_density", 0), 0.2) +
                               features.get("extreme_adjectives_count", 0) * 0.1)
                               
            final_prob = min(prob_hype + heuristic_boost, 1.0)
            score = max(min(1.0 + final_prob * 4.0, 5.0), 1.0)
            return _get_label(score), round(score, 2)
        except Exception:
            return _heuristic_mock_classify(features)

    # Fallback heurístico
    return _heuristic_mock_classify(features)

def _heuristic_mock_classify(features: dict) -> tuple[str, float]:
    """
    Classificador mock baseado apenas nas heurísticas.
    """
    score = 1.5
    score += features.get("uppercase_words_percentage", 0) * 10
    score += features.get("exclamation_density", 0) * 5
    score += features.get("extreme_adjectives_count", 0) * 0.8
    score = max(min(score, 5.0), 1.0)
    return _get_label(score), round(score, 2)

def _get_label(score: float) -> str:
    if score < 2.5:
        return "Sóbrio"
    elif score < 3.8:
        return "Hype Moderado"
    else:
        return "Hype Elevado"

