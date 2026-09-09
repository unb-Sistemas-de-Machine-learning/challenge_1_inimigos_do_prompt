---
title: Backend API
---
# Backend API - Inimigos do Prompt

O projeto utiliza um backend em **FastAPI** para realizar as predições de inteligência artificial sobre newsletters capturadas pelo frontend, com foco no suporte à interpretabilidade.

## Stack Tecnológica

* **Framework API:** FastAPI / Uvicorn (Alta performance e geração automática de Swagger/OpenAPI)
* **Validação de Dados:** Pydantic (Garante tipagem forte baseada no contrato do TypeScript da extensão)
* **Modelos ML:** Suporte duplo via `ModelLoader` para o pipeline base com scikit-learn (Regressão Logística + TF-IDF) e fallback avançado via BERTimbau (`transformers`).
* **Cache em Memória:** `cachetools` (TTL Cache de 1 hora para evitar reprocessamento de newsletters muito comuns).

## Arquitetura de Pastas (`backend/`)

A estrutura interna do servidor foi desenhada para separar domínios:

```text
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── analyze.py     # Ponto principal de predição
│           └── feedback.py    # Recepção de avaliações de usuários
├── ml/
│   ├── artifacts/             # Modelos serializados (.joblib)
│   └── model_loader.py        # Singleton para carregar o modelo apenas uma vez na inicialização
├── schemas/
│   ├── analyze.py             # Modelos Pydantic (AnalyzeRequest, AnalyzeResponse)
│   └── feedback.py            # Modelos Pydantic (FeedbackRequest)
├── services/
│   ├── analyzer.py            # Orquestração principal
│   ├── classifier.py          # Wrapper de predição sobre o ModelLoader
│   ├── explainer.py           # Interpretabilidade (SHAP/LIME ou Heurísticas textuais)
│   └── preprocessor.py        # Limpeza do HTML extraído e engenharia de features
└── utils/
    └── cache.py               # Configurações de caching para otimizar tempo de resposta
```

---

## Documentação de Endpoints

### `POST /api/v1/analyze`

Endpoint responsável por receber o conteúdo extraído da aba do navegador, processá-lo e devolver as pontuações e termos destacados.

**Corpo da Requisição (JSON):**
```json
{
  "email_id": "uuid-opcional",
  "sender": "newsletter@exemplo.com",
  "subject": "Título Sensacionalista Aqui",
  "raw_text": "Corpo limpo do email sem scripts e footers..."
}
```

**Corpo da Resposta (JSON):**
Retorna o score de 1 a 5, o label textual e arrays de termos para a extensão grifar:
```json
{
  "email_id": "123e4567-e89b-12d3-a456-426614174000",
  "sensationalism_score": 4.2,
  "label": "Hype Elevado",
  "confidence": 0.95,
  "highlighted_terms": [
    {
      "term": "Revolucionário",
      "weight": 0.9,
      "category": "hype"
    }
  ],
  "disclaimer": "Os resultados são baseados em heurísticas. Analise criticamente.",
  "disinformation_risk": 78,
  "suspicious_claims": [
    {
      "claim": "A substituição de 90% dos programadores",
      "explanation": "Hype exagerado, projeção não comprovada por fontes técnicas.",
      "severity": "moderate"
    }
  ]
}
```

### `POST /api/v1/feedback`

Coleta feedback dos usuários para medir a confiança e apontar falsos positivos, viabilizando o "Active Learning" futuro.

**Corpo da Requisição (JSON):**
```json
{
  "email_id": "123e4567-e89b-12d3-a456-426614174000",
  "feedback_type": "false_positive",
  "claim_index": 2,
  "slider_value": null,
  "comment": "Modelo errou aqui, o assunto é científico de fato"
}
```

---

## Como Rodar Localmente

Recomendamos utilizar a configuração via **Docker** para garantir consistência e facilitar a orquestração.

### Via Docker Compose
Na pasta raiz do backend (`backend/`), execute:
```bash
docker-compose up --build
```
O servidor estará disponível em `http://localhost:8000`. Acesse `http://localhost:8000/docs` para visualizar a interface interativa do Swagger.

### Via Python Venv (Desenvolvimento)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-api.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
