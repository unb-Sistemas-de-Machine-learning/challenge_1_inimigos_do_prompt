# Início

## Boas-vindas ao Projeto Inimigos do Prompt!

Este projeto é desenvolvido para a disciplina de **Sistemas de Machine Learning** (semestre 2026/02) pela equipe **Inimigos do Prompt**.

Nossa missão é combater o sensacionalismo e a desinformação no consumo de notícias técnicas e newsletters de tecnologia por meio de inteligência artificial aplicada.

---

## Declaração do Desafio (Challenge Statement)

> "Ajudar assinantes de newsletters de tecnologia (como o *Techdrop*) a consumir notícias com mais senso crítico em seus e-mails, com um sistema que prevê o grau de sensacionalismo e a probabilidade de desinformação de cada pauta — e saberemos que funcionou se, em um teste com leitores reais, o modelo acertar a classificação melhor que um baseline de regras de palavras-chave e os usuários relatarem que o relatório de veracidade influenciou sua percepção sobre as notícias."

---

## Objetivos do Projeto

### Objetivo de Negócio (Impacto Real)
* **Público-alvo:** Assinantes de newsletters de tecnologia no Brasil.
* **Impacto Prático:** Reduzir o pânico especulativo e blindar o leitor de desinformação técnica, permitindo um consumo crítico de notícias.
* **KPIs de Sucesso:**
    * **Influência na Percepção (> 70%):** Proporção de leitores que relatam mudança ou refinamento de visão após usar a ferramenta.
    * **Engajamento com Explicabilidade (> 40%):** Interação ativa dos usuários com os destaques de termos e alertas explicativos.
    * **CSAT (Satisfação e Credibilidade):** Nota média de satisfação $\ge 4.0/5.0$ em testes de uso contínuo.

### Objetivo de ML (Modelo e Avaliação)
* **Predição:** Identificar e classificar o nível de sensacionalismo e exagero (*hype*) em textos jornalísticos/informativos.
* **Métrica Principal:** **F-0.5 Score** (Priorizando a **Precisão**).
* **Justificativa Técnica:**
    > [!IMPORTANT]
    > O erro mais prejudicial em moderação de conteúdo é o **Falso Positivo** (rotular incorretamente um artigo legítimo ou autor sério como sensacionalista). Ao focar no F-0.5 Score, aumentamos o peso da Precisão sobre a revocação (*recall*), minimizando esses alarmes falsos e fortalecendo a credibilidade das predições do sistema.

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

<style>
  .team-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
    margin-top: 30px;
  }
  .team-card {
    text-decoration: none !important;
    color: inherit !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 150px;
    padding: 20px 15px;
    border-radius: 12px;
    background: var(--md-code-bg-color, rgba(128, 128, 128, 0.05));
    border: 1px solid rgba(128, 128, 128, 0.15);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  }
  .team-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    border-color: var(--md-typeset-a-color, #3f51b5);
  }
  .team-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin-bottom: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    border: 2px solid var(--md-default-bg-color, #fff);
  }
  .team-name {
    font-size: 0.95rem;
    font-weight: 600;
    text-align: center;
    word-break: break-all;
  }
</style>

<div class="team-grid">
  <a href="https://github.com/cvbmiranda" target="_blank" class="team-card">
    <img src="https://github.com/cvbmiranda.png" alt="cvbmiranda" class="team-avatar">
    <span class="team-name">cvbmiranda</span>
  </a>
  <a href="https://github.com/gus-ant" target="_blank" class="team-card">
    <img src="https://github.com/gus-ant.png" alt="gus-ant" class="team-avatar">
    <span class="team-name">gus-ant</span>
  </a>
  <a href="https://github.com/Szervinsk" target="_blank" class="team-card">
    <img src="https://github.com/Szervinsk.png" alt="Szervinsk" class="team-avatar">
    <span class="team-name">Szervinsk</span>
  </a>
  <a href="https://github.com/arthurgomes1290" target="_blank" class="team-card">
    <img src="https://github.com/arthurgomes1290.png" alt="arthurgomes1290" class="team-avatar">
    <span class="team-name">arthurgomes1290</span>
  </a>
  <a href="https://github.com/CaioHabibe" target="_blank" class="team-card">
    <img src="https://github.com/CaioHabibe.png" alt="CaioHabibe" class="team-avatar">
    <span class="team-name">CaioHabibe</span>
  </a>
</div>
