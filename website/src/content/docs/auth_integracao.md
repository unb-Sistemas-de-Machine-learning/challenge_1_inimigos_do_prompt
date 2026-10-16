---
title: Autenticação, Refatoração e Deploy em Nuvem
description: Documentação detalhada dos fluxos de autenticação Supabase, padrão Strategy e arquitetura de deploy em produção.
---

Esta documentação detalha a arquitetura de segurança, o fluxo de tokens JWT com o Supabase, a refatoração do motor de inferência via padrão Strategy e a topologia de deploy em nuvem.

---

## Fluxo Completo de Autenticação e Sessão (Supabase)

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuário
    participant UI as Extensão / Web Frontend
    participant Storage as chrome.storage.local
    participant Supabase as Supabase Auth (BaaS)
    participant Backend as FastAPI Backend

    User->>UI: Informa e-mail e senha
    UI->>Supabase: signInWithPassword({ email, password })
    Supabase-->>UI: Retorna Session com access_token (JWT)
    UI->>Storage: Persiste sessão no chromeStorage adapter
    
    Note over User, UI: Leitura de Newsletter no Gmail / Outlook
    UI->>Storage: Recupera access_token ativo
    UI->>Backend: POST /api/v1/analyze com Header Authorization: Bearer JWT
    
    Backend->>Backend: get_current_user extrai e valida payload do JWT
    alt Token Inválido ou Expirado
        Backend-->>UI: 401 Unauthorized
        UI->>User: Exibe tela de login / renovação de sessão
    else Token Válido
        Backend->>Backend: Executa inferência via Strategy e Explainer
        Backend-->>UI: 200 OK com análise completa
    end
```

---

## Topologia de Deploy e Integração em Nuvem

```mermaid
flowchart TB
    subgraph Client["Camada de Cliente"]
        ExtChrome["Extensão Google Chrome<br/>(dist-chrome)"]
        ExtFF["Extensão Mozilla Firefox<br/>(dist-firefox)"]
        Portal["Portal Documentação<br/>(GitHub Pages / Astro Starlight)"]
    end

    subgraph AuthProvider["Serviço de Identidade"]
        SB["Supabase Auth Cloud<br/>(Gerenciamento de Usuários & Emissão JWT)"]
    end

    subgraph BackendHost["Hospedagem da API (Render)"]
        DockerAPI["FastAPI em Contêiner Docker<br/>(inimigos-do-prompt-api.onrender.com)<br/>MODEL_BACKEND=gradio_space"]
    end

    subgraph MLCloud["Hospedagem de Modelos (Hugging Face)"]
        HFSpace["Hugging Face Space (Gradio)<br/>(gustant1-inimigos-prompt.hf.space)"]
        HFHub["Hugging Face Hub (Model Weights)<br/>(gustant1/bertimbau-sensacionalismo)"]
    end

    Client <-->|Autenticação & Tokens| SB
    ExtChrome & ExtFF -->|Chamadas REST com Bearer Token| DockerAPI
    DockerAPI <-->|REST API / Predict Call| HFSpace
    HFSpace -.->|Baixa pesos finetunados| HFHub
```

---

## Fase 1: Provedor de Autenticação (Supabase)

Adotou-se o **Supabase** como Backend-as-a-Service (BaaS) para autenticação, eliminando o risco e a complexidade de armazenamento manual de senhas e hashing criptográfico:

- **Controle de Acesso:** Usuários realizam cadastro e login utilizando e-mail e senha.
- **Tokens Padronizados:** Emissão de tokens JWT assinados via algoritmo HMAC-SHA256 contendo informações de usuário (`sub`, `email`, `exp`).

---

## Fase 2: Integração com o Frontend (Extensão Web)

No contexto de extensões Manifest V3, o `localStorage` tradicional pode não estar disponível em todos os contextos de execução (ex: Service Workers isolados). 

Para contornar essa restrição, foi desenvolvido um adaptador customizado (`chromeStorage`) em `extension/src/lib/supabase.ts`, implementando a interface `SupportedStorage` da biblioteca `@supabase/supabase-js` através das APIs nativas `chrome.storage.local`.

---

## Fase 3: Proteção de Rotas no FastAPI

O backend valida as requisições através do módulo `app/services/auth.py`, utilizando a injeção de dependência `Depends(get_current_user)` do FastAPI:

1. O cabeçalho `Authorization: Bearer <token>` é extraído pela classe `HTTPBearer`.
2. A aplicação verifica a presença de `SUPABASE_JWT_SECRET` nas configurações.
3. Decodifica o payload e confere o tempo de expiração (`exp`), rejeitando requisições inválidas ou expiradas com status `401 Unauthorized`.

---

## Fase 4: Padrão Strategy na Inferência

Para desacoplar a camada de API dos modelos de Machine Learning, implementou-se o padrão **Strategy**:

- **Interface Abstrata (`ModelStrategy`):** Exige a implementação do método `predict(text: str, features: dict) -> Tuple[str, float]`.
- **Implementações Intercambiáveis:**
  * `GradioSpaceStrategy`: Delega o processamento pesado de linguagem natural para o Hugging Face Space.
  * `BertimbauLocalStrategy`: Executa BERTimbau localmente via PyTorch / Transformers.
  * `SklearnStrategy`: Executa o classificador baseline scikit-learn.
  * `FallbackStrategy`: Heurística baseada em regras léxicas em caso de indisponibilidade de rede.

---

## Fase 5: Topologia de Produção no Render e Hugging Face

Para disponibilizar a solução sem custos de infraestrutura e contornar os limites de memória RAM dos planos gratuitos:

1. **Backend no Render:** O repositório possui o arquivo [`render.yaml`](file:///e:/challenge_1_inimigos_do_prompt/render.yaml), que provisiona um contêiner Docker leve rodando a API FastAPI com `MODEL_BACKEND="gradio_space"`.
2. **Inferência no Hugging Face:** O modelo BERTimbau ajustado finamente executa em um Space dedicado com Gradio, expondo o endpoint `/predict` consumido pelo backend.
