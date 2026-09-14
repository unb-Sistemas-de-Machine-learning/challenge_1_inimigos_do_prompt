---
title: Backend API
---

O backend é uma API FastAPI para a PoC de análise de newsletters. Ele recebe o texto extraído pela extensão, produz uma classificação de hype e devolve termos e frases que justificam o resultado.

## Estado do modelo

`ModelLoader` carrega `backend/app/ml/artifacts/model.joblib` e `vectorizer.joblib`, artefatos sklearn versionados no repositório. Com eles disponíveis, o serviço vetorializa o texto, usa `predict_proba` e acrescenta um pequeno ajuste heurístico ao score.

Se os artefatos estiverem ausentes ou não puderem ser carregados, o serviço usa o fallback heurístico com:

- percentual de palavras em caixa alta;
- densidade de exclamações;
- ocorrências de um léxico de termos extremos, como “revolucionário”, “urgente” e “destruir”.

A opção de configuração `MODEL_BACKEND=bertimbau` ainda não carrega nem executa BERTimbau; ela mantém o fallback.

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
