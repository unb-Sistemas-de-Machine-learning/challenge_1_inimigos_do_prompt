---
title: Extensão Web Frontend
---

A extensão é uma PoC Chrome Manifest V3 construída com React 19, TypeScript, Vite, Tailwind CSS e `@crxjs/vite-plugin`.

## O que funciona hoje

- Observa o DOM do Gmail e do Outlook Live.
- Extrai o assunto e o texto visível da mensagem.
- Envia o texto ao service worker, que consulta a API FastAPI e guarda a resposta no cache local.
- Destaca no HTML da mensagem os termos retornados como relevantes.
- Abre um side panel ao clicar no ícone da extensão.
- Oferece um dashboard que pode exportar a análise carregada em JSON.

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

O manifesto permite acesso somente a `https://mail.google.com/*`, `https://outlook.live.com/*` e `http://localhost:8000/*`. O endpoint da API está fixo em `src/services/api.ts`.

## Comunicação atual

O content script envia a mensagem `ANALYZE_EMAIL`. O service worker devolve `ANALYSIS_RESULT` apenas como resposta àquela chamada, então o content script recebe a análise e aplica os grifos.

O side panel escuta mensagens globais, mas o service worker não publica a resposta para ele. Além disso, somente a ação **Simular Análise (POC)** grava `current_analysis`, que é a chave que o dashboard lê. Logo, a visualização de análise real no painel e no dashboard ainda não está conectada.

O envio de feedback no side panel e o reporte no dashboard são visuais: não chamam `POST /api/v1/feedback` no estado atual.

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
- O modo simulado contém dados fixos e não representa uma resposta do backend.
