# Extensão Web — Inimigos do Prompt

Extensão para navegadores baseada em Manifest V3 desenvolvida com React 19, TypeScript, Vite e Tailwind CSS. Observa newsletters abertas no Gmail e Outlook Live, extrai o conteúdo textual e consulta a API FastAPI para destacar trechos sensacionalistas e exibir a análise no painel lateral.

---

## Fluxo de Execução da Extensão

```mermaid
sequenceDiagram
    actor User as Usuário
    participant DOM as Webmail DOM (Gmail/Outlook)
    participant CS as Content Script
    participant SW as Service Worker
    participant Auth as Supabase Auth
    participant API as FastAPI Backend
    participant UI as Side Panel / Dashboard

    User->>DOM: Abre newsletter
    DOM->>CS: Mutação detectada no DOM
    CS->>CS: Extrai e sanitiza texto
    CS->>SW: Mensagem ANALYZE_EMAIL
    SW->>Auth: Recupera JWT da sessão ativa
    SW->>API: POST /api/v1/analyze (Bearer JWT)
    API-->>SW: Score, termos e alegações
    SW->>SW: Grava no chrome.storage (current_analysis)
    SW-->>CS: Termos para destaque
    CS->>DOM: Injeta grifos inline (<mark>)
    SW-->>UI: Dispara evento com resultado
    UI->>User: Exibe métricas, risco e explicação
```

---

## Desenvolvimento e Compilação

Instale as dependências:

```bash
npm install
```

Crie o arquivo de configuração local a partir do modelo:

```bash
cp .env.example .env
```

Preencha as credenciais do seu projeto Supabase no `.env` (`VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY`). Opcionalmente, defina `VITE_API_URL` se o backend não estiver rodando no padrão `http://localhost:8000`.

### Modo Desenvolvimento (Vite)

```bash
npm run dev
```

### Compilação de Produção

- **Para Google Chrome:**
  ```bash
  npm run build:chrome
  ```
  Os arquivos compilados são gerados em `extension/dist-chrome/`. Acesse `chrome://extensions`, ative o **Modo do desenvolvedor** e clique em **Carregar sem compactação**, selecionando `extension/dist-chrome`.

- **Para Mozilla Firefox:**
  ```bash
  npm run build:firefox
  ```
  Os arquivos compilados são gerados em `extension/dist-firefox/`. Acesse `about:debugging#/runtime/this-firefox`, clique em **Carregar extensão temporária** e aponte para `extension/dist-firefox/manifest.json`.

---

## Comunicação com o Backend

A extensão envia as requisições autenticadas para:
* `POST /api/v1/analyze`: Análise textual de newsletters.
* `POST /api/v1/feedback`: Envio de ajustes no slider de sensibilidade ou reporte de falsos positivos.
* `GET /health`: Monitoramento de conectividade com a API.

Todas as chamadas para rotas protegidas injetam automaticamente o token JWT retornado pelo Supabase no cabeçalho `Authorization: Bearer <token>`.
