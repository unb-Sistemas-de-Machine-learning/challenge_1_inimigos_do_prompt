---
title: Início
description: Documentação do Inimigos do Prompt
template: splash
hero:
  title: Inimigos do Prompt
  tagline: Nossa missão é combater o sensacionalismo e a desinformação no consumo de notícias técnicas e newsletters de tecnologia por meio de IA aplicada.
  image:
    file: ../../assets/logo_inimigos.png
  actions:
    - text: Começar a ler
      link: /challenge_1_inimigos_do_prompt/planejamento/
      icon: right-arrow
      variant: primary
---

## Boas-vindas ao Projeto Inimigos do Prompt!

Este projeto é desenvolvido para a disciplina de **Sistemas de Machine Learning** (semestre 2026/02) pela equipe **Inimigos do Prompt**.

Nossa missão é combater o sensacionalismo e a desinformação no consumo de notícias técnicas e newsletters de tecnologia por meio de inteligência artificial aplicada.

> [!IMPORTANT]
> A implementação disponível é uma PoC local. Ela analisa mensagens abertas no Gmail e Outlook Live com artefatos sklearn versionados, destaca termos no webmail e apresenta a análise no side panel e dashboard. O risco de desinformação continua heurístico: não há uma segunda predição independente nem fact-checking em tempo real.

---

## Declaração do Desafio (Challenge Statement)

> "Ajudar assinantes de newsletters de tecnologia (como o *Techdrop*) a consumir notícias com mais senso crítico em seus e-mails, com um sistema que prevê o grau de sensacionalismo e a probabilidade de desinformação de cada pauta — e saberemos que funcionou se, em um teste com leitores reais, o modelo acertar a classificação melhor que um baseline de regras de palavras-chave e os usuários relatarem que o relatório de veracidade influenciou sua percepção sobre as notícias."

---

## Objetivos do Projeto

As seções seguintes registram os objetivos de produto e de avaliação do projeto. Elas não descrevem funcionalidades já entregues; para o estado implementado, consulte [Arquitetura da Extensão](../arquitetura/), [Extensão Web](../extensao_frontend/) e [Backend API](../backend_api/).

### Objetivo de Negócio (Impacto Real)
* **Público-alvo:** Assinantes de newsletters de tecnologia no Brasil.
* **Impacto Prático:** Reduzir o pânico especulativo e blindar o leitor de desinformação técnica, permitindo um consumo crítico de notícias.
* **KPIs de Sucesso:**
    * **Influência na Percepção (> 70%):** Proporção de leitores que relatam mudança ou refinamento de visão após usar a ferramenta.
    * **Engajamento com Explicabilidade (> 40%):** Interação ativa dos usuários com os destaques de termos e alertas explicativos.
    * **CSAT (Satisfação e Credibilidade):** Nota média de satisfação $\ge 4.0/5.0$ em testes de uso contínuo.

### Objetivo de ML (Modelo e Avaliação)
* **Tarefa avaliada no baseline:** Identificar e classificar o nível de sensacionalismo e exagero (*hype*) em textos jornalísticos/informativos.
* **Métrica do baseline:** **F-0.5 Score** (priorizando a **precisão**).
* **Justificativa Técnica:**
    > [!IMPORTANT]
    > O erro mais prejudicial em moderação de conteúdo é o **Falso Positivo** (rotular incorretamente um artigo legítimo ou autor sério como sensacionalista). Ao focar no F-0.5 Score, aumentamos o peso da Precisão sobre a revocação (*recall*), minimizando esses alarmes falsos e fortalecendo a credibilidade das predições do sistema.

> [!NOTE]
> A inferência disponível é uma PoC com artefatos sklearn versionados. O risco de desinformação é derivado do score e das regras de alegações, não uma predição independente. Veja [Dados](../dados/) e [Backend API](../backend_api/) para as limitações atuais.

---

## Escopo do Projeto

### O que o projeto TRATA (In-Scope)
* Notícias e artigos extraídos de newsletters de tecnologia em **Português (Brasil)**.
* Processamento exclusivo de **texto limpo** (removendo tags HTML, menus de navegação, rodapés e propagandas).
* Relatórios gerados com **interpretabilidade** (exibição de termos/frases chave que mais influenciaram a predição).
* Arquitetura em nuvem escalável contendo banco de dados em cache para requisições repetidas.

### O que o projeto NÃO TRATA (Out-of-Scope)
* Análise de conteúdos multimídia (imagens, vídeos, áudios).
* Fact-checking dinâmico em tempo real (ex: varrer motores de busca em tempo real para verificar fatos).
* Leitura ou moderação de e-mails pessoais/corporativos que não sejam newsletters cadastradas no serviço.

---

## Equipe


<div class="team-grid">
  <a href="https://github.com/cvbmiranda" target="_blank" class="team-card">
    <img src="https://github.com/cvbmiranda.png" alt="cvbmiranda" class="team-avatar" />
    <span class="team-name">cvbmiranda</span>
  </a>
  <a href="https://github.com/gus-ant" target="_blank" class="team-card">
    <img src="https://github.com/gus-ant.png" alt="gus-ant" class="team-avatar" />
    <span class="team-name">gus-ant</span>
  </a>
  <a href="https://github.com/Szervinsk" target="_blank" class="team-card">
    <img src="https://github.com/Szervinsk.png" alt="Szervinsk" class="team-avatar" />
    <span class="team-name">Szervinsk</span>
  </a>
  <a href="https://github.com/arthurgomes1290" target="_blank" class="team-card">
    <img src="https://github.com/arthurgomes1290.png" alt="arthurgomes1290" class="team-avatar" />
    <span class="team-name">arthurgomes1290</span>
  </a>
  <a href="https://github.com/CaioHabibe" target="_blank" class="team-card">
    <img src="https://github.com/CaioHabibe.png" alt="CaioHabibe" class="team-avatar" />
    <span class="team-name">CaioHabibe</span>
  </a>
</div>
