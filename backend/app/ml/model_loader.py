import os
import joblib
import logging
import torch
from app.config import settings

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    
    # Modelos de Sensacionalismo (Hype)
    _model = None
    _tokenizer = None
    _vectorizer = None
    
    # Modelos de Desinformação (Claims)
    _claims_model = None
    _claims_vectorizer = None
    
    _backend_type = "sklearn"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        backend = settings.model_backend.lower()
        self._backend_type = backend
        artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "artifacts"))
        
        logger.info(f"Carregando backend de modelo de Sensacionalismo: {backend}")
        
        # 1. CARREGAR MODELO PRINCIPAL (SENSACIONALISMO)
        if backend == "bertimbau":
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                
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
            # Fallback (Sklearn baseline para sensacionalismo)
            try:
                model_path = os.path.join(artifacts_dir, "model.joblib")
                vec_path = os.path.join(artifacts_dir, "vectorizer.joblib")
                
                if os.path.exists(model_path) and os.path.exists(vec_path):
                    self._model = joblib.load(model_path)
                    self._vectorizer = joblib.load(vec_path)
                    logger.info("Modelo Sklearn (Sensacionalismo) carregado com sucesso.")
                else:
                    logger.warning("Artefatos de Sensacionalismo não encontrados.")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo Sklearn: {e}")

        # 2. CARREGAR MODELO DE DESINFORMAÇÃO (CLAIMS - ISSUE #30)
        try:
            claims_model_path = os.path.join(artifacts_dir, "claims_model.joblib")
            claims_vec_path = os.path.join(artifacts_dir, "claims_vectorizer.joblib")
            
            if os.path.exists(claims_model_path) and os.path.exists(claims_vec_path):
                self._claims_model = joblib.load(claims_model_path)
                self._claims_vectorizer = joblib.load(claims_vec_path)
                logger.info("Modelo e Vectorizer de Claims (Desinformação) carregados com sucesso.")
            else:
                logger.warning("Artefatos de Claims não encontrados. A API retornará risco 0% (Fallback).")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de Claims: {e}")

    def predict_claims_risk(self, claims: list[str]) -> tuple[int, list[dict]]:
        """
        Analisa uma lista de alegações (frases) extraídas do e-mail.
        Retorna o risco agregado (0-100) e a lista de claims suspeitas.
        """
        # Fallback de degradação graciosa caso os artefatos não existam
        if not self._claims_model or not self._claims_vectorizer or not claims:
            return 0, []

        try:
            # Vetoriza as frases extraídas
            vec_claims = self._claims_vectorizer.transform(claims)
            
            # predict_proba retorna matriz: [[prob_classe_0, prob_classe_1], ...]
            probs = self._claims_model.predict_proba(vec_claims)
            
            suspicious_claims = []
            max_risk = 0.0

            for claim, prob in zip(claims, probs):
                risk_prob = prob[1] # Probabilidade de ser desinformação (Classe 1)
                
                # Guarda o maior risco encontrado no e-mail inteiro
                if risk_prob > max_risk:
                    max_risk = risk_prob

                # Se a IA tiver mais de 50% de certeza que é desinformação, flagamos
                if risk_prob > 0.5:
                    severity = "high" if risk_prob > 0.75 else "medium"
                    suspicious_claims.append({
                        "claim": claim,
                        "severity": severity,
                        "explanation": f"Padrão de desinformação detectado com {risk_prob*100:.1f}% de confiança."
                    })

            # Converte probabilidade máxima para um inteiro de 0 a 100
            aggregate_risk = int(max_risk * 100)
            return aggregate_risk, suspicious_claims

        except Exception as e:
            logger.error(f"Erro durante a predição de Claims: {e}")
            return 0, []

    # Properties
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