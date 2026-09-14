---
title: Guia de Configuração e Execução
---

O repositório tem três projetos independentes: o pipeline Python/ML na raiz, a API em `backend/` e a extensão em `extension/`. O site de documentação é um quarto projeto, em `website/`.

## 1. Pipeline Python e dados

Na raiz do repositório, crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Gere os dados e avalie o baseline:

```bash
python src/build_sensacionalismo_dataset.py
python src/generate_sample_dataset.py
python src/merge_datasets.py
python src/train_baseline.py
```

Os comandos de download e scraping exigem acesso à internet. Os dados resultantes ficam em `data/` e não são versionados.

## 2. API FastAPI

Em outro terminal, instale as dependências específicas e inicie a API:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-api.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Alternativamente, com Docker:

```bash
cd backend
docker compose up --build
```

A API fica disponível em `http://localhost:8000`; a especificação OpenAPI está em `http://localhost:8000/api/v1/openapi.json`. O endpoint `GET /health` responde em `http://localhost:8000/health`.

> [!IMPORTANT]
> Sem `backend/app/ml/artifacts/model.joblib` e `vectorizer.joblib`, a API usa o classificador heurístico. O script `train_baseline.py` avalia modelos, mas ainda não exporta esses artefatos.

## 3. Extensão Chrome

```bash
cd extension
npm install
npm run build
```

No Chrome, abra `chrome://extensions`, ative o modo de desenvolvedor e carregue a pasta `extension/dist`. A extensão possui permissões apenas para Gmail, Outlook Live e `http://localhost:8000`.

## 4. Site de documentação

O site usa Astro Starlight, não MkDocs. Para executá-lo localmente:

```bash
cd website
npm install
npm run dev
```

Para gerar o site estático:

```bash
npm run build
```
