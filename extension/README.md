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

O manifesto injeta o content script no Gmail e no Outlook Live. Ele também declara permissões para `localhost`, `127.0.0.1` e Outlook na web; a URL usada pela API permanece fixa em `http://localhost:8000`.

A API carrega, por padrão, os artefatos sklearn versionados em `../backend/app/ml/artifacts/`. Se esses arquivos não estiverem disponíveis, o backend mantém um fallback heurístico.

## Limitações atuais

- A resposta real destaca termos no webmail, atualiza o side panel e é salva como `current_analysis` para o dashboard.
- O painel consulta `GET /health`, pode solicitar uma nova extração na aba ativa e oferece exemplos de hype e texto sóbrio que chamam a API real.
- A confirmação do slider envia `confidence_slider` e o dashboard envia `false_positive` para `POST /api/v1/feedback`.
- A aplicação dos destaques substitui `innerHTML`, abordagem limitada à demonstração.
- A análise automática ainda é iniciada uma única vez por ciclo de DOM; uma troca de mensagem sem remover o corpo pode não ser detectada.

Veja a [documentação da extensão](../website/src/content/docs/extensao_frontend.md) e o [guia de execução integrada](../website/src/content/docs/execucao_poc_api.md) para detalhes.
