# Challenge 1 - Equipe Inimigos do prompt - Sistemas de Machine Learning 2026/02

## Challenge Statement
"Ajudar assinantes de newsletters de tecnologia (como o Techdrop) a consumir notícias com mais senso crítico em seus e-mails, com um sistema que prevê o grau de sensacionalismo e a probabilidade de desinformação de cada pauta — e saberemos que funcionou se, em um teste com leitores reais, o modelo acertar a classificação melhor que um baseline de regras de palavras-chave e os usuários relatarem que o relatório de veracidade influenciou sua percepção sobre as notícias.”

---

## Objetivo de Negócio (Impacto Real)
- **Público-alvo:** Assinantes de newsletters de tecnologia no Brasil.
- **Impacto Prático:** Reduzir o pânico especulativo e blindar o leitor de desinformação técnica, permitindo um consumo crítico de notícias.
- **KPIs de Sucesso:**
  - **Influência na Percepção (> 70%):** Leitores que relatam mudança de visão após usar a ferramenta.
  - **Engajamento com Explicabilidade (> 40%):** Interação com destaques e alertas.
  - **CSAT (Credibilidade):** Nota >= 4.0/5.0 em testes de uso contínuo.

---

## Objetivo de ML (Modelo e Avaliação)
- **Predição:** Nível de sensacionalismo/hype em textos jornalísticos e informativos.
- **Métrica Principal:** **F-0.5 Score** (Otimizando a Precisão).
- **Justificativa:** O erro mais prejudicial em moderação de conteúdo é o *Falso Positivo* (rotular indevidamente um autor legítimo como sensacionalista). Focar na Precisão previne que o sistema aja como um "censor injusto", priorizando a confiança e a credibilidade das predições.

---

## Escopo do Projeto
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

## Planejamento e As 6 Guiding Questions Refatoradas

**1. Dados: Aquisição e Representatividade**
- **A Pergunta:** De onde extrairemos um volume histórico de newsletters de tecnologia que reflita os jargões e o hype atual, garantindo que o modelo não aprenda com dados defasados?
- **Atividade:** Mapear 10 portais de tecnologia/newsletters relevantes e criar um script de web scraping (ou exportação de e-mails) para montar o dataset cru inicial.
- **Recurso:** Terminal Linux, Node.js (com Cheerio ou Puppeteer) ou Python (BeautifulSoup).
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
- **A Pergunta:** Qual regra de palavras-chave (baseline) usaremos como ponto de partida e qual métrica (ex: F1-Score ou Precisão) provará que o esforço computacional do ML realmente compensa?
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
