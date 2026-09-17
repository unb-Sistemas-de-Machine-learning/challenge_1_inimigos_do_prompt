import os
import joblib
import logging
import torch
from app.config import settings

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _model = None
    _tokenizer = None
    _vectorizer = None
    _backend_type = "sklearn"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        backend = settings.model_backend.lower()
        self._backend_type = backend
        
        logger.info(f"Carregando backend de modelo: {backend}")
        
        if backend == "bertimbau":
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                
                # Procura primeiro a pasta local do modelo
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
                local_model_path = os.path.join(root_dir, settings.local_model_path)
                
                loaded = False
                if os.path.exists(local_model_path) and (
                    os.path.exists(os.path.join(local_model_path, "model.safetensors")) or
                    os.path.exists(os.path.join(local_model_path, "pytorch_model.bin")) or
                    os.path.exists(os.path.join(local_model_path, "config.json"))
                ):
                    try:
                        logger.info(f"Carregando modelo BERTimbau local de: {local_model_path}")
                        self._tokenizer = AutoTokenizer.from_pretrained(local_model_path)
                        self._model = AutoModelForSequenceClassification.from_pretrained(local_model_path)
                        loaded = True
                    except Exception as local_err:
                        logger.warning(f"Falha ao carregar modelo local ({local_err}). Tentando Hugging Face Hub.")

                if not loaded:
                    model_path = settings.hf_model_id
                    logger.info(f"Carregando modelo BERTimbau do Hugging Face Hub: {model_path}")
                    self._tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self._model = AutoModelForSequenceClassification.from_pretrained(model_path)

                self._model.eval()
                logger.info("Modelo BERTimbau (PyTorch) e Tokenizer carregados com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo BERTimbau: {e}. Usando modo de fallback.")
                self._backend_type = "fallback"
        else:
            # Fallback (Sklearn baseline)
            artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
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
                logger.error(f"Erro ao carregar modelo Sklearn: {e}")

    @property
    def model(self):
        return self._model

    @property
    def tokenizer(self):
        return self._tokenizer
        
    @property
    def vectorizer(self):
        return self._vectorizer

    @property
    def backend_type(self):
        return self._backend_type

# Instância Singleton
ml_loader = ModelLoader()

