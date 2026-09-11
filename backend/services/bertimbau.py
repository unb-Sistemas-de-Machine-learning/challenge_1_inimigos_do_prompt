"""
Serviço de classificação local usando o BERTimbau fine-tunado.
Fase A: inferência 100% local, sem chamadas externas.
Fase B (futuro): enriquecer o resultado com análise do Gemini.
"""

import os
from functools import lru_cache
from transformers import pipeline
from models import AnalyzeRequest, AnalyzeResponse

# Caminho do modelo salvo pelo treinamento (relativo à raiz do projeto)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, "..", "models", "bertimbau_sensacionalismo_final")

# Mapeamento do label interno do modelo para o label amigável da API
_LABEL_MAP = {
    "LABEL_0": "Sóbrio",
    "LABEL_1": "Sensacionalista",
    # O fine-tuning define id2label, então estes nomes também podem aparecer:
    "sobrio": "Sóbrio",
    "sensacionalista": "Sensacionalista",
}


@lru_cache(maxsize=1)
def _load_pipeline():
    """
    Carrega o pipeline uma única vez na memória e reutiliza em todas as
    requisições (singleton via lru_cache). Roda na CPU por padrão —
    suficiente para latência < 200 ms por e-mail.
    """
    return pipeline(
        task="text-classification",
        model=MODEL_PATH,
        tokenizer=MODEL_PATH,
        device=-1,          # -1 = CPU; mude para 0 para usar GPU (CUDA/DirectML não suportado aqui)
        truncation=True,
        max_length=256,
    )


async def analyze_email_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Classifica um e-mail como Sóbrio ou Sensacionalista.
    O texto de assunto (se fornecido) é concatenado ao corpo para dar
    mais contexto ao modelo, reproduzindo o mesmo formato do treino.
    """
    classifier = _load_pipeline()

    # Monta o texto da mesma forma que foi usado no treino
    text = request.raw_text
    if request.subject:
        text = f"{request.subject}\n\n{request.raw_text}"

    result = classifier(text)[0]

    raw_label = result["label"]
    friendly_label = _LABEL_MAP.get(raw_label, raw_label)
    confidence = round(float(result["score"]), 4)

    return AnalyzeResponse(
        email_id=request.email_id,
        label=friendly_label,
        confidence=confidence,
    )
