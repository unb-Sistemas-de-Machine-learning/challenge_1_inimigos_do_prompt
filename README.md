# Challenge 1 - Equipe Inimigos do prompt - Sistemas de Machine Learning 2026/02

## 🎯 Challenge Statement (Proposta)
"Ajudar leitores de newsletters de tecnologia a consumir conteúdos com mais senso crítico direto no e-mail, por meio de um pipeline de Machine Learning que quantifica o nível de sensacionalismo do texto e sinaliza alegações com potencial de desinformação/hype.
Saberemos que funcionou se:
O modelo superar um baseline de heurísticas baseadas em palavras-chave em métricas de classificação ($F_1\text{-score}$ e calibração de probabilidade) em um dataset anotado do nicho;
Em testes com leitores reais, o indicador alterar significativamente a confiança declarada dos usuários em notícias duvidosas/hiperbólicas e apresentar taxa de utilidade percebida superior a 70%."

---

## 💼 Objetivo de Negócio (Impacto Real)
- **Público-alvo:** Assinantes de newsletters de tecnologia no Brasil.
- **Impacto Prático:** Reduzir o pânico especulativo e blindar o leitor de desinformação técnica, permitindo um consumo crítico de notícias.
- **KPIs de Sucesso:**
  - **Mudança Comportamental de Confiança:** Medir a confiabilidade declarada do leitor antes de ver o score do modelo vs. depois (comportamento objetivo pré/pós-intervenção).
  - **Taxa de Utilidade Percebida (> 70%):** Percentual de usuários que avaliam o relatório final como útil.
  - **Engajamento com Explicabilidade (> 40%):** Cliques em "ver checagem detalhada" ou interação com os destaques e alertas.

---

## 🧠 Objetivo de ML (Modelo e Avaliação)
- **Predição (Multi-Target):**
  - **Target 1:** Score contínuo de sensacionalismo/clickbait (treinado em escala Likert de 1 a 5).
  - **Target 2:** Probabilidade de desinformação/claim verification (treinado em categorias de claims).
- **Métrica Principal:** **F1-Score** e **Calibração de Probabilidade**.
- **Justificativa:** Tratar sensacionalismo e desinformação como tarefas separadas evita confundir notícias verdadeiras e hiperbólicas com mentiras redigidas em tom neutro. O F1-score balanceia a detecção, enquanto a calibração garante que o score de probabilidade exibido ao usuário reflita a confiança real do modelo.

---

## 🚧 Escopo do Projeto
### ✅ O que o projeto TRATA (In-Scope)
* Notícias e artigos extraídos de newsletters de tecnologia em Português (Brasil).
* Processamento exclusivo de texto limpo (removendo HTML, menus e propagandas).
* Relatórios gerados com interpretabilidade (destaque dos termos que influenciaram a predição).
* Arquitetura em nuvem escalável com banco de dados em cache (para requisições repetidas).

### ❌ O que o projeto NÃO TRATA (Out-of-Scope)
* Análise de conteúdos multimídia (imagens, vídeos, áudios).
* Fact-checking dinâmico em tempo real (ex: varrer o Google em tempo real para checar fontes).
* Leitura ou moderação de e-mails pessoais/corporativos que não sejam newsletters cadastradas.

---

## 📋 Planejamento e As 6 Guiding Questions Refatoradas

**1. Dados: Aquisição, Representatividade e Rotulação (Ground Truth)**
- **A Pergunta:** De onde extrairemos um volume histórico de newsletters que reflita o hype atual, e como garantir uma anotação confiável sabendo que "fake news tech" geralmente são promessas não comprovadas?
- **Atividade:** 
  1) Mapear 10 portais/newsletters e criar script de web scraping.
  2) Criar um **Manual Simples de Anotação**, utilizando escala Likert (1 a 5) para sensacionalismo e tags categóricas para desinformação.
- **Recurso:** Terminal Linux, Node.js (Cheerio/Puppeteer) ou Python (BeautifulSoup). Manual de anotação e ferramenta de rotulação.
- **Responsável:** Membro 1.
- **Prazo:** 28/08/2026.

**2. Dados: Processamento e Ruído**
- **A Pergunta:** Como o pipeline vai limpar as tags HTML, links de patrocinadores e cabeçalhos dos e-mails, isolando apenas o texto das notícias para o classificador?
- **Atividade:** Desenvolver uma função de sanitização usando expressões regulares (Regex) para receber o HTML do e-mail e cuspir apenas texto limpo.
- **Recurso:** VSCode/Cursor AI, bibliotecas de conversão HTML-para-texto e um dataset de teste de 5 e-mails.
- **Responsável:** Membro 2.
- **Prazo:** 28/08/2026.

**3. Usuário: Integração, Atrito e Interpretabilidade**
- **A Pergunta:** Como entregar o relatório de sensacionalismo com baixo atrito e explicar o "porquê" da classificação sem interromper agressivamente a leitura do usuário?
- **Atividade:** Desenhar o fluxo do usuário (ex: o bot envia um resumo no topo da mensagem original) e definir como a explicação (interpretabilidade) será exibida.
- **Recurso:** Excalidraw ou Figma para desenhar o fluxo e questionário de validação com colegas.
- **Responsável:** Membro 3.
- **Prazo:** 04/09/2026.

**4. Modelo: Baseline, Tradeoffs e Valor Justificado**
- **A Pergunta:** Qual regra de palavras-chave (baseline) usaremos como ponto de partida e qual métrica (ex: F1-Score e Calibração) provará que o esforço computacional do ML realmente compensa?
- **Atividade:** Codificar um baseline simples (ex: `if` com contador de palavras como "revolucionário" ou "urgente") e definir o limiar de acurácia que o modelo de ML precisa bater para ser aceito.
- **Recurso:** Ambiente de desenvolvimento (Python/Jupyter) e o dataset limpo da etapa 2.
- **Responsável:** Membro 4.
- **Prazo:** 04/09/2026.

**5. Produção: Arquitetura de Ingestão e Custo**
- **A Pergunta:** Como estruturar o recebimento simultâneo dessas newsletters mantendo o custo de infraestrutura baixo e evitando o gargalo de processamento?
- **Atividade:** Criar a Prova de Conceito (PoC) de um servidor conectado a uma conta de e-mail via IMAP, isolado em um contêiner, que recebe as mensagens e as enfileira para processamento.
- **Recurso:** Docker, Node.js ou C#/.NET, e uma conta de e-mail de teste dedicada.
- **Responsável:** Membro 5.
- **Prazo:** 11/09/2026.

**6. Ética: Transparência e Danos**
- **A Pergunta:** Se o modelo cometer um falso positivo e classificar a notícia legítima de um criador de conteúdo como "Fake/Sensacionalista", qual é o mecanismo de mitigação de danos à reputação?
- **Atividade:** Redigir o termo de isenção de responsabilidade (disclaimer) que acompanhará as análises e criar um canal de feedback para usuários reportarem erros do modelo.
- **Recurso:** Documento de texto colaborativo.
- **Responsável:** Membros 1 e 2 (em par).
- **Prazo:** 11/09/2026.
