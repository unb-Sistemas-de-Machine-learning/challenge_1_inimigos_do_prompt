# Extensão Chrome — Inimigos do Prompt

Extensão Chrome Manifest V3 da PoC. Ela observa mensagens abertas no Gmail e Outlook Live, extrai o texto visível e solicita uma análise à API FastAPI local.

## Desenvolvimento

```bash
npm install
npm run dev
```

O servidor Vite usa a porta `5173`. Para produzir a extensão carregável pelo Chrome:

```bash
npm run build
```

Em `chrome://extensions`, ative o modo de desenvolvedor e use **Carregar sem compactação** para selecionar `dist/`.

## Dependência da API

O endpoint está fixo em `http://localhost:8000/api/v1/analyze`. Antes de testar a extensão, inicie a API a partir de `../backend`:

```bash
pip install -r requirements-api.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O manifesto concede acesso apenas a Gmail, Outlook Live e ao host local da API. A análise disponível é heurística enquanto não existirem artefatos sklearn em `backend/app/ml/artifacts/`.

## Limitações atuais

- A resposta real é usada para destacar termos no webmail, mas ainda não abastece o side panel nem o dashboard.
- O botão **Simular Análise (POC)** popula essas telas com dados fictícios.
- Os controles de feedback e reporte são visuais e não chamam a rota de feedback da API.
- A aplicação dos destaques substitui `innerHTML`, abordagem limitada à demonstração.

Veja a [documentação da extensão](../website/src/content/docs/extensao_frontend.md) e o [guia de execução integrada](../website/src/content/docs/execucao_poc_api.md) para detalhes.
