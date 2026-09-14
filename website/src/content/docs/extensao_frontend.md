---
title: Extensão Web Frontend
---

A extensão é uma PoC Chrome Manifest V3 construída com React 19, TypeScript, Vite, Tailwind CSS e `@crxjs/vite-plugin`.

## O que funciona hoje

- Observa o DOM do Gmail e do Outlook Live.
- Extrai o assunto e o texto visível da mensagem.
- Envia o texto ao service worker, que consulta a API FastAPI e guarda a resposta no cache local.
- Destaca no HTML da mensagem os termos retornados como relevantes.
- Atualiza o side panel com a análise real, incluindo estado de conexão da API e ação para extrair a mensagem da aba ativa.
- Oferece exemplos de hype e texto sóbrio que consultam a API real.
- Oferece um dashboard que abre a análise real armazenada e pode exportá-la em JSON.
- Envia feedback de confiança e reporte de falso positivo à API.

## Estrutura efetiva

```text
extension/
├── manifest.json
├── index.html                 # Side panel
├── dashboard.html             # Dashboard em aba
└── src/
    ├── App.tsx                # UI do side panel
    ├── background/service-worker.ts
    ├── content/
    │   ├── extractor.ts
    │   ├── highlighter.ts
    │   └── index.ts
    ├── dashboard/
    │   ├── Dashboard.tsx
    │   └── main.tsx
    ├── services/api.ts
    └── types/index.ts
```

O content script é injetado em `https://mail.google.com/*` e `https://outlook.live.com/*`. O manifesto também declara acesso a `http://localhost:8000/*`, `http://127.0.0.1:8000/*` e `https://outlook.office.com/*`; porém, não há injeção de content script para este último. O endpoint usado está fixo em `src/services/api.ts` como `http://localhost:8000`.

## Comunicação atual

O content script envia `ANALYZE_EMAIL`. O service worker consulta o cache ou a API, guarda a resposta em `current_analysis`, responde ao content script e transmite `ANALYSIS_RESULT` para as views abertas. O content script usa a resposta para aplicar os grifos.

Ao abrir, o side panel verifica `GET /health`, recupera `current_analysis` e passa a escutar as mensagens. O dashboard lê a mesma chave, portanto exibe a análise real mais recente, inclusive quando veio do cache. A ação manual de análise reenvia `TRIGGER_EXTRACTION` para a aba ativa.

O side panel chama `POST /api/v1/feedback` com `confidence_slider`; o dashboard envia `false_positive` com o índice da alegação. Se a chamada do dashboard falhar, ele ainda marca o item como reportado apenas na interface daquela sessão.

## Desenvolvimento e build

```bash
cd extension
npm install
npm run dev
```

Para gerar a versão carregável pelo Chrome:

```bash
npm run build
```

Carregue `extension/dist` em `chrome://extensions` com o modo de desenvolvedor ativado.

## Limitações da PoC

- Não usa Zustand, Radix/shadcn ou componentes em `src/sidepanel/`; essas referências pertencem a uma arquitetura anterior.
- A aplicação dos destaques modifica `innerHTML`, portanto não é uma estratégia robusta para páginas complexas de webmail.
- A análise é iniciada uma única vez por ciclo de DOM e pode não acompanhar a troca de mensagens em todos os fluxos do Gmail/Outlook.
- Os exemplos de hype e texto sóbrio chamam a API local; não são respostas fictícias.
