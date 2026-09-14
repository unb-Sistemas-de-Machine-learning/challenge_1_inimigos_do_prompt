---
title: Backend API
---

O backend é uma API FastAPI para a PoC de análise de newsletters. Ele recebe o texto extraído pela extensão, produz uma classificação de hype e devolve termos e frases que justificam o resultado.

## Estado do modelo

`ModelLoader` tenta carregar `backend/app/ml/artifacts/model.joblib` e `vectorizer.joblib`. Esses artefatos não estão versionados. Quando ausentes, o serviço usa um classificador heurístico com:

- percentual de palavras em caixa alta;
- densidade de exclamações;
- ocorrências de um léxico de termos extremos, como “revolucionário”, “urgente” e “destruir”.

Com artefatos sklearn válidos, o código aplica o vetorizador ao texto, usa `predict_proba` e adiciona um pequeno ajuste heurístico. A opção de configuração `MODEL_BACKEND=bertimbau` ainda não carrega nem executa BERTimbau; ela mantém o fallback.

## Rotas

### `GET /health`

Responde apenas se o processo está ativo:

```json
{"status":"ok"}
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

Recebe `false_positive` ou `confidence_slider` e registra uma linha JSON no arquivo local `backend/feedback_log.jsonl`. O feedback não dispara retreinamento automático.

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
