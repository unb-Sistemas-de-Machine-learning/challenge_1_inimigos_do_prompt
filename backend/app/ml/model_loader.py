import os
import joblib
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _model = None
    _vectorizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        backend = settings.model_backend.lower()
        artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
        
        logger.info(f"Carregando backend de modelo: {backend}")
        
        if backend == "bertimbau":
            # Para o MVP, se bertimbau não estiver treinado local, usamos fallback
            logger.warning("Backend BERTimbau ainda não implementado 100% no loader, usando fallback ou mock...")
            # Futuramente: self._model = transformers.pipeline(...)
            pass
        else:
            # Fallback (Sklearn baseline)
            try:
                model_path = os.path.join(artifacts_dir, "model.joblib")
                vec_path = os.path.join(artifacts_dir, "vectorizer.joblib")
                
                if os.path.exists(model_path) and os.path.exists(vec_path):
                    self._model = joblib.load(model_path)
                    self._vectorizer = joblib.load(vec_path)
                    logger.info("Modelo Sklearn carregado com sucesso.")
                else:
                    logger.warning("Artefatos ML não encontrados. O classificador usará modo heurístico (mock).")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo: {e}")

    @property
    def model(self):
        return self._model
        
    @property
    def vectorizer(self):
        return self._vectorizer

# Instância Singleton
ml_loader = ModelLoader()
