---
title: Backend API
---

O backend é uma API FastAPI para a PoC de análise de newsletters. Ele recebe o texto extraído pela extensão, produz uma classificação de hype e devolve termos e frases que justificam o resultado.

## Estado do modelo

O `ModelLoader` suporta dois backends principais para a classificação de sensacionalismo:

1. **BERTimbau Fine-Tuned (Principal):**
   * **Modelo:** `neuralmind/bert-base-portuguese-cased` ajustado finamente no dataset de newsletters tech.
   * **Hospedagem:** Disponível publicamente no Hugging Face Hub em [gustant1/bertimbau-sensacionalismo](https://huggingface.co/gustant1/bertimbau-sensacionalismo).
   * **Como rodar:** Ao configurar `MODEL_BACKEND=bertimbau` nas configurações/variáveis de ambiente, o backend utiliza a biblioteca `transformers` da Hugging Face para baixar e carregar os pesos diretamente do repositório remoto ou de uma pasta local baixada.

2. **Scikit-Learn Baseline (Fallback Local):**
   * Carrega os artefatos `model.joblib` e `vectorizer.joblib` versionados em `backend/app/ml/artifacts/`.
   * Vetorializa o texto com TF-IDF, calcula a probabilidade via `predict_proba` e aplica um ajuste heurístico ao score.

Se os artefatos estiverem ausentes ou a biblioteca do BERTimbau não for encontrada, o serviço utiliza um fallback heurístico puramente baseado em regras (caixa alta, densidade de exclamações e léxico alarmista).

## Rotas

### `GET /health`

Responde o estado do processo, o backend configurado e se o modelo foi carregado:

```json
{"status":"healthy","model_loaded":true,"model_backend":"sklearn"}
```

### `POST /api/v1/analyze`

Entrada:

```json
{
  "email_id": "opcional",
  "sender": "newsletter@exemplo.com",
  "subject": "Assunto opcional",
  "raw_text": "Texto ou HTML da newsletter"
}
```

Saída:

```json
{
  "email_id": "uuid-gerado-ou-informado",
  "sensationalism_score": 1.5,
  "label": "Sóbrio",
  "confidence": 0.95,
  "highlighted_terms": [],
  "disclaimer": "Os resultados são baseados em heurísticas. Analise criticamente.",
  "disinformation_risk": 30,
  "suspicious_claims": []
}
```

O score varia de 1 a 5 e o label é `Sóbrio`, `Hype Moderado` ou `Hype Elevado`. A confiança atual é um valor fixo condicionado ao score, não uma probabilidade calibrada. `disinformation_risk` é derivado do score e recebe um incremento se houver claim de severidade alta; não representa uma segunda predição independente.

### `POST /api/v1/feedback`

Recebe `false_positive` ou `confidence_slider` e registra uma linha JSON no arquivo local `backend/feedback_log.jsonl`. `email_id` é obrigatório; `claim_index`, `slider_value` e `comment` são opcionais.

```json
{
  "email_id": "id-da-analise",
  "feedback_type": "false_positive",
  "claim_index": 0,
  "comment": "A alegação possui fonte verificável."
}
```

O feedback não dispara retreinamento automático. A extensão chama essa rota: o side panel envia `confidence_slider`, e o dashboard envia `false_positive` ao reportar uma alegação. Os registros usam timestamp em UTC.

## Cache e limitações

A API mantém até 500 respostas em um `TTLCache` de uma hora. A chave usa somente os primeiros 200 caracteres do texto original; mensagens diferentes com o mesmo prefixo podem, portanto, compartilhar a resposta em cache. O objeto em cache também pode ter seu `email_id` substituído na próxima chamada.

O CORS aceita qualquer origem para facilitar o desenvolvimento da extensão. Antes de uma publicação, ele deve ser restringido ao identificador da extensão.

## Execução

```bash
cd backend
pip install -r requirements-api.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Com Docker:

```bash
cd backend
docker compose up --build
```
