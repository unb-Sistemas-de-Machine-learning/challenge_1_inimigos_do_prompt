---
title: Arquitetura da Extensão Web
---

Esta página descreve a implementação atual da PoC, não a arquitetura planejada.

## Fluxo implementado

```mermaid
sequenceDiagram
    actor User as Usuário
    participant CS as Content Script
    participant SW as Service Worker
    participant API as FastAPI

    User->>CS: Abre uma mensagem no Gmail ou Outlook Live
    CS->>CS: Extrai assunto e texto limpo do DOM
    CS->>SW: ANALYZE_EMAIL
    SW->>SW: Consulta chrome.storage.local
    SW->>API: POST /api/v1/analyze (se não houver cache)
    API-->>SW: Score, termos e claims heurísticos
    SW-->>CS: ANALYSIS_RESULT
    CS->>CS: Destaca termos no corpo da mensagem
```

O content script usa os seletores `.a3s.aiL` no Gmail e `.x_WordSection1` ou `[aria-label="Corpo da mensagem"]` no Outlook. A extração remove scripts, estilos, iframes, `footer` e alguns seletores de descadastro. A API faz uma segunda limpeza de HTML e URLs.

## Componentes existentes

| Camada | Implementação atual |
| --- | --- |
| Manifesto | Chrome Manifest V3 com `sidePanel`, `storage` e `activeTab`. |
| Content script | `src/content/`: extrai a mensagem, solicita a análise e injeta `<mark>` no HTML da mensagem. |
| Service worker | `src/background/service-worker.ts`: faz cache local e chama `http://localhost:8000/api/v1/analyze`. |
| Interface | React 19, TypeScript, Vite, Tailwind e Lucide. Há um side panel (`index.html`) e um dashboard (`dashboard.html`). |
| API | FastAPI com cache em memória e classificador sklearn quando há artefatos; caso contrário, heurísticas. |

Não há Zustand, Radix/shadcn, DOMPurify, SHAP nem LIME no código atual. A explicabilidade é feita por léxico: palavras alarmistas, texto em caixa alta e alguns padrões de clickbait.

## Estado do painel e do dashboard

O resultado da análise real retorna ao content script para aplicar os grifos. O service worker não transmite esse resultado ao side panel nem o grava como `current_analysis`. Por isso, o side panel pode permanecer sem dados e o dashboard só recebe dados quando se usa a ação **Simular Análise (POC)**, que grava uma resposta fictícia no storage.

O botão da extensão abre o side panel por aba. O dashboard é aberto pelo botão da interface React e permite exportar o JSON carregado.

## Limitações conhecidas

- A flag `hasAnalyzed` evita reanalisar a mesma página, mas pode impedir nova análise ao trocar de mensagem sem que o corpo desapareça do DOM.
- O highlighter substitui `innerHTML`; isso é adequado apenas à PoC e pode afetar elementos ou listeners do webmail.
- As permissões e os seletores estão limitados a Gmail e Outlook Live; Outlook corporativo não está no manifesto atual.
- A URL da API é fixa em `localhost`, portanto não há configuração de ambiente nem serviço remoto.

## Estrutura efetiva

```text
extension/
├── manifest.json
├── src/
│   ├── background/service-worker.ts
│   ├── content/{extractor,highlighter,index}.ts
│   ├── dashboard/{Dashboard,main}.tsx
│   ├── services/api.ts
│   ├── types/index.ts
│   ├── App.tsx
│   └── main.tsx
├── index.html
└── dashboard.html
```
