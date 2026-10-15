---
title: Extensão Web Frontend
---

A extensão do **Inimigos do Prompt** é construída com suporte a múltiplos navegadores (Google Chrome e Mozilla Firefox) no modelo Manifest V3, utilizando React 19, TypeScript, Vite, Tailwind CSS e `@crxjs/vite-plugin`.

---

## Arquitetura Interna da Extensão

```mermaid
flowchart TD
    subgraph WebmailTab["Aba do Navegador (Gmail / Outlook)"]
        DOM["DOM da Mensagem"]
        Extr["extractor.ts<br/>(Sanitização & Extração)"]
        High["highlighter.ts<br/>(Injeção de tags &lt;mark&gt;)"]
        CS["Content Script Entry (index.ts)"]
        
        DOM -->|Observa mutações| Extr
        Extr --> CS
        CS -->|Repassa termos| High
        High -->|Destaca no texto| DOM
    end

    subgraph BackgroundWorker["Service Worker (Manifest V3)"]
        SW["service-worker.ts"]
        LocalCache[("chrome.storage.local<br/>Cache de Análises & Sessão")]
        APIClient["api.ts (Fetch com Bearer JWT)"]
        
        SW <--> LocalCache
        SW --> APIClient
    end

    subgraph ExtensionUI["Interface do Usuário (Side Panel & Dashboard)"]
        AuthView["Auth.tsx<br/>(Login/Cadastro Supabase)"]
        Panel["App.tsx<br/>(Side Panel Interativo)"]
        Dash["Dashboard.tsx<br/>(dashboard.html - Aba Completa)"]
    end

    CS <-->|chrome.runtime.sendMessage| SW
    SW <-->|chrome.runtime.onMessage| Panel
    SW <-->|chrome.runtime.onMessage| Dash
    AuthView --> LocalCache
    APIClient <-->|REST API| BackendServer["FastAPI Backend / Nuvem"]
```

---

## Máquina de Estados do Side Panel

```mermaid
stateDiagram-v2
    [*] --> ChecandoAutenticacao
    
    ChecandoAutenticacao --> Deslogado: Sem sessão ativa
    ChecandoAutenticacao --> Autenticado: Sessão Supabase válida
    
    Deslogado --> Autenticado: Login / Cadastro realizado
    Autenticado --> Deslogado: Logout
    
    state Autenticado {
        [*] --> VerificandoAPI
        VerificandoAPI --> APIOffline: GET /health falhou
        VerificandoAPI --> APIOnline: GET /health sucesso
        
        APIOffline --> VerificandoAPI: Tentar reconectar
        
        APIOnline --> AguardandoLeitura: Sem newsletter na aba ativa
        AguardandoLeitura --> Analisando: Extração automática ou manual
        Analisando --> ExibindoAnalise: Resposta da API recebida
        
        state ExibindoAnalise {
            [*] --> VisualizacaoMetricas
            VisualizacaoMetricas --> EnviandoFeedback: Ajuste de slider ou reporte
            EnviandoFeedback --> VisualizacaoMetricas: Feedback gravado
        }
    }
```

---

## Funcionalidades Implementadas

- **Detecção e Extração Automática:** Monitora as abas do Gmail (`mail.google.com`) e Outlook Live (`outlook.live.com`), isolando o conteúdo de newsletters e descartando rodapés, menus e rastreadores.
- **Autenticação Integrada:** Telas completas de Login e Cadastro conectadas ao Supabase, gerenciando tokens JWT com persistência segura no `chrome.storage.local`.
- **Destaque Visual de Tom (Highlighter):** Grifa no próprio corpo da mensagem os termos que mais contribuíram para o score de sensacionalismo.
- **Painel Lateral com Diagnóstico:** Exibe status da API, termômetro de hype (1 a 5), alegações enfáticas, slider de confiança calibrável e atalho para análise manual.
- **Dashboard Abrangente:** Tela em aba dedicada (`dashboard.html`) para inspecionar métricas linguísticas, dados da análise e exportação em formato JSON.
- **Suporte Multi-Navegador:** Compilação nativa para **Chrome** (`side_panel`) e **Firefox** (`sidebar_action`).

---

## Estrutura Efetiva do Código

```text
extension/
├── manifest.json              # Manifesto base V3
├── index.html                 # Interface do Side Panel
├── dashboard.html             # Interface do Dashboard
├── vite.config.ts             # Script de build inteligente (Chrome/Firefox)
└── src/
    ├── App.tsx                # Componente principal do Side Panel
    ├── Auth.tsx               # Interface de autenticação Supabase
    ├── lib/
    │   └── supabase.ts        # Cliente Supabase com storage adapter
    ├── background/
    │   └── service-worker.ts  # Worker de mensageria e orquestração
    ├── content/
    │   ├── extractor.ts       # Seletores de DOM e higienização
    │   ├── highlighter.ts     # Injetor de estilos e tags <mark>
    │   └── index.ts           # Inicializador do content script
    ├── dashboard/
    │   ├── Dashboard.tsx      # Dashboard detalhado
    │   └── main.tsx
    ├── services/
    │   └── api.ts             # Cliente HTTP com injeção de JWT
    └── types/
        └── index.ts           # Definição de tipos TypeScript
```

---

## Configuração e Compilação

Crie o arquivo `extension/.env` a partir do template:

```bash
cd extension
cp .env.example .env
```

Preencha as variáveis do Supabase e a URL da API:
```ini
VITE_SUPABASE_URL=https://SEU_PROJETO.supabase.co
VITE_SUPABASE_ANON_KEY=SUA_CHAVE_ANON
VITE_API_URL=http://localhost:8000
```

### Comandos de Build

```bash
# Instalar dependências
npm install

# Compilar para Google Chrome:
npm run build:chrome
# Gera pasta extension/dist-chrome/

# Compilar para Mozilla Firefox:
npm run build:firefox
# Gera pasta extension/dist-firefox/
```

- **Google Chrome:** Vá em `chrome://extensions`, ative o *Modo do desenvolvedor* e selecione `extension/dist-chrome` em **Carregar sem compactação**.
- **Mozilla Firefox:** Vá em `about:debugging#/runtime/this-firefox`, clique em **Carregar extensão temporária** e selecione o arquivo `extension/dist-firefox/manifest.json`.
