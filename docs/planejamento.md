# Planejamento do Projeto

Abaixo estão detalhadas as diretrizes estratégicas e operacionais do projeto, organizadas através das **6 Guiding Questions** de Sistemas de Machine Learning.

---

## 📅 As 6 Guiding Questions Refatoradas

???+ note "1. Dados: Aquisição e Representatividade"
    * **A Pergunta:** De onde extrairemos um volume histórico de newsletters de tecnologia que reflita os jargões e o hype atual, garantindo que o modelo não aprenda com dados defasados?
    * **Atividade:** Mapear 10 portais de tecnologia/newsletters relevantes e criar um script de web scraping (ou exportação de e-mails) para montar o dataset cru inicial.
    * **Recurso:** Terminal Linux, Node.js (com Cheerio ou Puppeteer) ou Python (BeautifulSoup).
    * **Responsável:** Membro 1
    * **Prazo:** 28/08/2026

???+ note "2. Dados: Processamento e Ruído"
    * **A Pergunta:** Como o pipeline vai limpar as tags HTML, links de patrocinadores e cabeçalhos dos e-mails, isolando apenas o texto das notícias para o classificador?
    * **Atividade:** Desenvolver uma função de sanitização usando expressões regulares (Regex) para receber o HTML do e-mail e obter apenas texto limpo.
    * **Recurso:** VSCode/Cursor AI, bibliotecas de conversão HTML-para-texto e um dataset de teste de 5 e-mails.
    * **Responsável:** Membro 2
    * **Prazo:** 28/08/2026

???+ note "3. Usuário: Integração, Atrito e Interpretabilidade"
    * **A Pergunta:** Como entregar o relatório de sensacionalismo com baixo atrito e explicar o "porquê" da classificação sem interromper agressivamente a leitura do usuário?
    * **Atividade:** Desenhar o fluxo do usuário (ex: o bot envia um resumo no topo da mensagem original) e definir como a explicação (interpretabilidade) será exibida.
    * **Recurso:** Excalidraw ou Figma para desenhar o fluxo e questionário de validação com colegas.
    * **Responsável:** Membro 3
    * **Prazo:** 04/09/2026

???+ note "4. Modelo: Baseline, Tradeoffs e Valor Justificado"
    * **A Pergunta:** Qual regra de palavras-chave (baseline) usaremos como ponto de partida e qual métrica (ex: F1-Score ou Precisão) provará que o esforço computacional do ML realmente compensa?
    * **Atividade:** Codificar um baseline simples (ex: `if` com contador de palavras como "revolucionário" ou "urgente") e definir o limiar de acurácia que o modelo de ML precisa bater para ser aceito.
    * **Recurso:** Ambiente de desenvolvimento (Python/Jupyter) e o dataset limpo da etapa 2.
    * **Responsável:** Membro 4
    * **Prazo:** 04/09/2026

???+ note "5. Produção: Arquitetura de Ingestão e Custo"
    * **A Pergunta:** Como estruturar o recebimento simultâneo dessas newsletters mantendo o custo de infraestrutura baixo e evitando o gargalo de processamento?
    * **Atividade:** Criar a Prova de Conceito (PoC) de um servidor conectado a uma conta de e-mail via IMAP, isolado em um contêiner, que recebe as mensagens e as enfileira para processamento.
    * **Recurso:** Docker, Node.js ou C#/.NET, e uma conta de e-mail de teste dedicada.
    * **Responsável:** Membro 5
    * **Prazo:** 11/09/2026

???+ note "6. Ética: Transparência e Danos"
    * **A Pergunta:** Se o modelo cometer um falso positivo e classificar a notícia legítima de um criador de conteúdo como "Fake/Sensacionalista", qual é o mecanismo de mitigação de danos à reputação?
    * **Atividade:** Redigir o termo de isenção de responsabilidade (disclaimer) que acompanhará as análises e criar um canal de feedback para usuários reportarem erros do modelo.
    * **Recurso:** Documento de texto colaborativo.
    * **Responsável:** Membros 1 e 2 (em par)
    * **Prazo:** 11/09/2026

---

## 👥 Matriz de Responsabilidades e Cronograma

| Membro | Função/Área | Atividades Principais | Prazo Final |
| :--- | :--- | :--- | :--- |
| **Membro 1** | Aquisição de Dados & Ética | Web scraping de portais, mapeamento de fontes de dados, elaboração do termo de transparência. | 11/09/2026 |
| **Membro 2** | Processamento & Ética | Pipeline de limpeza de dados (Regex), remoção de ruído (HTML), termo de transparência. | 11/09/2026 |
| **Membro 3** | UX / Integração | Design da interface e fluxo do usuário, integração e interpretabilidade visual. | 04/09/2026 |
| **Membro 4** | Modelagem / ML | Implementação de baselines e avaliação de modelos baseado no F-0.5 Score. | 04/09/2026 |
| **Membro 5** | Engenharia / DevOps | Servidor de ingestão IMAP, conteinerização com Docker e PoC em produção. | 11/09/2026 |
