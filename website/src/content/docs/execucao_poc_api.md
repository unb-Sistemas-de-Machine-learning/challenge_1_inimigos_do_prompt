---
title: Execução da PoC Integrada
---

Esta é a sequência para testar a integração entre a API local e a extensão. Por padrão, ela usa os artefatos sklearn versionados em `backend/app/ml/artifacts/`; se eles não puderem ser carregados, a API usa o fallback heurístico.

## 1. Inicie a API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-api.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Confirme que o processo está ativo:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"status":"healthy","model_loaded":true,"model_backend":"sklearn"}
```

## 2. Teste a análise diretamente

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "IA vai DESTRUIR empregos?",
    "raw_text": "URGENTE! Esta IA revolucionária promete substituir 90% dos programadores."
  }'
```

Confira `model_loaded` no health check para saber se os artefatos foram carregados. A resposta preserva o disclaimer de análise crítica; o contrato completo está em [Backend API](../backend_api/).

## 3. Compile e carregue a extensão

```bash
cd extension
npm install
npm run build
```

Em `chrome://extensions`, ative o modo de desenvolvedor e use **Carregar sem compactação** para selecionar `extension/dist`.

## 4. Valide o fluxo no webmail

1. Mantenha a API em `localhost:8000`.
2. Abra uma mensagem no Gmail ou Outlook Live com mais de 30 caracteres.
3. Aguarde a extensão extrair o texto e enviar a requisição, ou use **Analisar E-mail da Aba Aberta** no side panel.
4. Confirme os grifos no corpo da mensagem e o resultado real no side panel.
5. Abra o dashboard pelo painel para conferir a mesma análise salva localmente; teste o slider ou o reporte de uma alegação para enviar feedback à API.

Use o console de service worker da página de extensões e o terminal da API para investigar erros de comunicação.

## Escopo e pendências

| Recurso | Estado atual |
| --- | --- |
| Extração Gmail/Outlook Live | Implementada com seletores de DOM. |
| Requisição API, CORS e cache local | Implementados para `localhost`. |
| Grifos no texto | Implementados como alteração simplificada de `innerHTML`. |
| Artefatos sklearn | Versionados em `backend/app/ml/artifacts/` e carregados pelo backend padrão. |
| BERTimbau na API | Pendente: loader ainda usa fallback. |
| Resultado real no side panel/dashboard | Implementado por broadcast e `chrome.storage.local`. |
| IMAP, fila e produção | Planejamento; não existem nesta PoC. |
