try:
    import torch
except ImportError:
    torch = None
import logging
import requests
from typing import Protocol, Tuple
from app.ml.model_loader import ml_loader
from app.config import settings

logger = logging.getLogger(__name__)

def _get_label(score: float) -> str:
    if score < 2.5:
        return "Sóbrio"
    elif score < 3.8:
        return "Hype Moderado"
    else:
        return "Hype Elevado"

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


# ==========================================
# 1. DEFINIÇÃO DA INTERFACE STRATEGY
# ==========================================
class ModelStrategy(Protocol):
    def predict(self, text: str, features: dict) -> Tuple[str, float]:
        ...

# ==========================================
# 2. ESTRATÉGIAS ESPECÍFICAS
# ==========================================
class BertimbauLocalStrategy:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def predict(self, text: str, features: dict) -> Tuple[str, float]:
        if self.model is None or self.tokenizer is None:
            return _heuristic_mock_classify(features)
            
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)[0]
                
            prob_hype = probs[1].item() if len(probs) > 1 else probs[0].item()
            
            heuristic_boost = (features.get("uppercase_words_percentage", 0) * 0.2 +
                               min(features.get("exclamation_density", 0), 0.1) +
                               features.get("extreme_adjectives_count", 0) * 0.05)
            
            final_prob = min(prob_hype + heuristic_boost, 1.0)
            score = max(min(1.0 + final_prob * 4.0, 5.0), 1.0)
            
            return _get_label(score), round(score, 2)
        except Exception as e:
            logger.error(f"Erro durante classificação BERTimbau: {e}")
            return _heuristic_mock_classify(features)


class SklearnStrategy:
    def __init__(self, model, vectorizer):
        self.model = model
        self.vectorizer = vectorizer

    def predict(self, text: str, features: dict) -> Tuple[str, float]:
        if self.model is None or self.vectorizer is None:
            return _heuristic_mock_classify(features)
            
        try:
            X_vec = self.vectorizer.transform([text])
            probs = self.model.predict_proba(X_vec)[0]
            prob_hype = probs[1] if len(probs) > 1 else probs[0]
            
            heuristic_boost = (features.get("uppercase_words_percentage", 0) * 0.5 +
                               min(features.get("exclamation_density", 0), 0.2) +
                               features.get("extreme_adjectives_count", 0) * 0.1)
                               
            final_prob = min(prob_hype + heuristic_boost, 1.0)
            score = max(min(1.0 + final_prob * 4.0, 5.0), 1.0)
            return _get_label(score), round(score, 2)
        except Exception as e:
            logger.error(f"Erro durante classificação Sklearn: {e}")
            return _heuristic_mock_classify(features)


class HuggingFaceAPIStrategy:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def predict(self, text: str, features: dict) -> Tuple[str, float]:
        if not self.api_url or not self.headers.get("Authorization"):
             logger.error("HuggingFace API URL ou Token ausentes.")
             return _heuristic_mock_classify(features)
             
        try:
            payload = {"inputs": text}
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # A estrutura pode variar. Geralmente é [[{'label': 'LABEL_1', 'score': 0.9}, ...]]
            probs = data[0] if isinstance(data, list) and isinstance(data[0], list) else data
            
            hype_score_value = 0.5
            for pred in probs:
                 # Ajuste essa label de acordo com a saída do seu modelo no Hugging Face
                 if pred.get('label', '') in ('LABEL_1', 'HYPE', '1', 1):
                     hype_score_value = pred.get('score', 0.5)
                     break
                     
            heuristic_boost = (features.get("uppercase_words_percentage", 0) * 0.2 +
                               min(features.get("exclamation_density", 0), 0.1) +
                               features.get("extreme_adjectives_count", 0) * 0.05)
                               
            final_prob = min(hype_score_value + heuristic_boost, 1.0)
            score = max(min(1.0 + final_prob * 4.0, 5.0), 1.0)
            return _get_label(score), round(score, 2)
            
        except Exception as e:
             logger.error(f"Erro durante classificação na API HuggingFace: {e}")
             return _heuristic_mock_classify(features)


class FallbackStrategy:
    def predict(self, text: str, features: dict) -> Tuple[str, float]:
        return _heuristic_mock_classify(features)

# ==========================================
# 3. O CONTEXTO QUE AS ROTAS UTILIZAM
# ==========================================
class ClassifierContext:
    def __init__(self, strategy: ModelStrategy):
        self._strategy = strategy
        
    def set_strategy(self, strategy: ModelStrategy):
        self._strategy = strategy
        
    def predict(self, text: str, features: dict) -> Tuple[str, float]:
        return self._strategy.predict(text, features)


# ==========================================
# 4. INICIALIZAÇÃO
# ==========================================
_strategy = FallbackStrategy()

if settings.model_backend == "huggingface_api":
    _strategy = HuggingFaceAPIStrategy(
         api_url=settings.huggingface_api_url,
         api_token=settings.huggingface_api_token
    )
elif settings.model_backend == "bertimbau":
    _strategy = BertimbauLocalStrategy(
         model=ml_loader.model,
         tokenizer=ml_loader.tokenizer
    )
elif settings.model_backend == "sklearn":
    _strategy = SklearnStrategy(
         model=ml_loader.model,
         vectorizer=ml_loader.vectorizer
    )

_context = ClassifierContext(_strategy)

def classify(text: str, features: dict) -> tuple[str, float]:
    """
    Função principal que a API usa (mantendo a compatibilidade).
    Repassa a requisição para a estratégia atualmente configurada.
    """
    return _context.predict(text, features)
