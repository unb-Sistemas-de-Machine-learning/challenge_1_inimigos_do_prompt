---
title: Autenticação, Refatoração e Deploy
description: Documentação das etapas de implementação de autenticação, refatoração do backend usando o padrão Strategy e deploy utilizando o Hugging Face.
---

Esta documentação detalha o plano de implementação executado para integrar o sistema de autenticação, refatorar o processamento de inferência e realizar a integração na nuvem.

## Fase 1: Escolha do Provedor de Autenticação (Supabase)

A primeira etapa consistiu em definir como gerenciaríamos a identidade dos usuários de forma segura. Em vez de implementar e manter um sistema de gerenciamento de senhas próprio, a escolha foi o **Supabase**, que oferece uma solução de autenticação robusta como serviço (BaaS).

Com isso, garantimos um fluxo seguro de login, delegando a responsabilidade de criação de contas, validação e geração de tokens JWT ao provedor. Nossa aplicação e banco de dados se mantêm mais enxutos e focados no negócio principal.

## Fase 2: Integração com o Frontend (Astro/Extensão)

Na segunda fase, integramos o provedor de autenticação com a nossa interface web frontend e a extensão de navegador.

O fluxo de configuração consistiu em:
- Implementar a biblioteca cliente do Supabase na interface.
- Criar os componentes e telas de Login e Cadastro.
- Salvar e manter a sessão ativa utilizando persistência. No contexto da extensão, aplicamos um adaptador customizado usando `chrome.storage.local` para manter os tokens compatíveis com o formato exigido pelo Manifest V3.
- Em cada requisição de análise, o frontend obtém o token JWT ativo da sessão e o prepara para ser enviado ao backend.

## Fase 3: Proteção do Backend (FastAPI)

O nosso Backend em **FastAPI** foi arquitetado de forma a não armazenar nem gerenciar senhas ativamente. Ele atua apenas verificando a legitimidade do JWT gerado pelo frontend.

O fluxo de proteção de rota funciona da seguinte maneira:
- O frontend envia a requisição (ex: pedido de análise de sensacionalismo) com o token no cabeçalho `Authorization: Bearer <token>`.
- O FastAPI extrai este JWT e realiza a verificação de integridade e assinatura para atestar que o token foi emitido pelo Supabase do nosso projeto.
- Se o token for válido e não estiver expirado, o acesso à rota é liberado e a requisição é processada. Caso contrário, um erro 401 é retornado.

## Fase 4: Refatoração com o Padrão Strategy

Para tornar o processamento de Machine Learning modular e preparado para integrações externas, aplicamos o **Padrão Strategy** (Strategy Pattern) na camada de inferência do backend.

As principais mudanças foram:
- **Organização das Partes dos Modelos**: Isolamos o código existente responsável pela análise, separando implementações e definindo contratos claros.
- **Criação de Interface Base**: Definimos uma estratégia base que obriga toda classe de modelo a implementar um método padronizado para retornar a análise do texto.
- **Estratégia Hugging Face**: Criamos uma estratégia específica que conecta o nosso sistema com a nuvem do Hugging Face. Essa classe carrega a chave de API do provedor (armazenada em `.env`), monta a requisição (payload), envia para o servidor externo e converte o retorno para o padrão que a nossa aplicação espera.

Essa estrutura nos permite alterar provedores ou voltar para um modelo local sem afetar as lógicas das rotas (endpoints).

## Fase 5: Deploy e Integração no Hugging Face

A quinta e última fase consolidou todo o fluxo usando a integração do modelo com a API de Inferência do Hugging Face, efetuando o deploy da solução de inferência.

A arquitetura refatorada estabelece a seguinte jornada da requisição (do clique do usuário até a exibição do resultado):

1. **Autenticação**: O usuário realiza o login pelo Site/Extensão e o Supabase valida, retornando um JWT autêntico.
2. **Requisição Segura**: O Site/Extensão envia o texto da newsletter para a API do nosso Backend, passando o JWT no cabeçalho.
3. **Validação**: O Backend recebe a chamada e atesta que o JWT é válido.
4. **Aplicação da Estratégia**: Após liberar o acesso, o Backend aciona a estratégia configurada (Hugging Face Strategy).
5. **Processamento Externo**: A classe injeta a chave de API (do `.env`) e encaminha o texto para ser inferido na nuvem do Hugging Face.
6. **Retorno do Modelo**: A API do Hugging Face analisa o texto, identifica padrões de sensacionalismo e devolve a resposta para o nosso Backend.
7. **Resposta ao Cliente**: O Backend normaliza esse resultado e despacha para o Frontend, que exibe os indicadores de forma visual na tela do usuário.
