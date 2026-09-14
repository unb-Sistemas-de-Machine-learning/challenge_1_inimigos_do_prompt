---
title: Execução da PoC Integrada
---

Esta é a sequência para testar a integração disponível entre a API local e a extensão. Ela valida o fluxo heurístico atual; não exige modelo treinado.

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
{"status":"ok"}
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

Sem artefatos de ML, a resposta terá disclaimer de heurísticas. O contrato completo está em [Backend API](../backend_api/).

## 3. Compile e carregue a extensão

```bash
cd extension
npm install
npm run build
```

Em `chrome://extensions`, ative o modo de desenvolvedor e use **Carregar sem compactação** para selecionar `extension/dist`.

## 4. Valide o fluxo no webmail

1. Mantenha a API em `localhost:8000`.
2. Abra uma mensagem no Gmail ou Outlook Live com mais de 50 caracteres.
3. Aguarde a extensão extrair o texto e enviar a requisição.
4. Confirme, no corpo da mensagem, os grifos dos termos retornados pela API.

Use o console de service worker da página de extensões e o terminal da API para investigar erros de comunicação.

## Escopo e pendências

| Recurso | Estado atual |
| --- | --- |
| Extração Gmail/Outlook Live | Implementada com seletores de DOM. |
| Requisição API, CORS e cache local | Implementados para `localhost`. |
| Grifos no texto | Implementados como alteração simplificada de `innerHTML`. |
| Modelo sklearn treinado | Pendente: não há artefatos no repositório. |
| BERTimbau na API | Pendente: loader ainda usa fallback. |
| Resultado real no side panel/dashboard | Pendente: não há sincronização da resposta. |
| IMAP, fila e produção | Planejamento; não existem nesta PoC. |
