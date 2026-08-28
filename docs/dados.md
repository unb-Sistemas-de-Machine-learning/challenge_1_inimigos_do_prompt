# Coleta e Ingestão de Dados

Esta seção detalha o fluxo de coleta, processamento de ruído e consolidação de dados utilizados para treinar e avaliar o modelo. Como o foco do projeto é identificar **sensacionalismo, clickbait e hype tecnológico**, o sistema consome dados via web scraping balanceando portais classificados como "sóbrios" (jornalismo factual) e textos focados em promessas exageradas.

---

## Visão Geral dos Datasets Gerados

Os dados coletados são armazenados na pasta `data/` nos seguintes arquivos:

| Arquivo | Origem | Descrição | Registros |
| :--- | :--- | :--- | :--- |
| `tech_sobrio.csv` | `Manual do Usuário` & `G1 Tecnologia` (Scraping) | Notícias factuais e análises críticas sobre tecnologia para servir como base de textos confiáveis (não sensacionalistas). | Variável |
| `tech_hype.csv` | Portais de Criptomoedas, Tech Clickbait (Scraping) | Coleta de artigos com títulos caça-cliques, viés apocalíptico sobre IA ou promessas hiperbólicas. | Variável |
| `dataset_hype_treino.csv` | Pipeline Interno (`feature_engineering.py`) | Dataset consolidado contendo textos limpos de ambos os CSVs anteriores, enriquecido com atributos estatísticos de texto (sinais de hype). | Variável |

---

## Detalhes dos Scripts de Ingestão (`src/`)

### 1. Scraper de Tecnologia Sóbria (`scraper_tech_sobrio.py`)

Utilizado para construir o conjunto de dados sob o domínio de tecnologia com viés neutro, descritivo e factual. Ele raspa duas fontes principais:

* **Manual do Usuário (`manualdousuario.net`):**
    * Foco em análises críticas e notícias aprofundadas sobre tecnologia e sociedade.
    * Extrai os textos principais a partir da classe `.e-content`.
* **G1 Tecnologia (`g1.globo.com/tecnologia`):**
    * Notícias factuais de tecnologia no Brasil sem exageros estruturais.
    * Extrai artigos iterando pelo feed de paginação pública e obtendo parágrafos com a classe `.content-text__container`.
* **Parâmetros de Linha de Comando:**
    * `--pages` (default: 3): Páginas de listagem raspadas por fonte.
    * `--delay` (default: 1.0): Tempo de espera entre as requisições.

---

### 2. Scraper de Tecnologia Sensacionalista (`scraper_tech_hype.py`)

Responsável por raspar conteúdo focado em angariar cliques fáceis, usando apelo à urgência, FOMO (Fear Of Missing Out) ou pânico.

* **Fluxo de Scraping:**
    1. Acessa páginas de listagem de sites conhecidos por clickbait técnico, portais de hype financeiro (cripto) ou tabloides de tecnologia.
    2. Extrai título, URL de destino e data de publicação.
    3. Entra em cada link coletado para extrair o texto completo, focando na linguagem utilizada.
* **Parâmetros de Linha de Comando:**
    * `--pages` (default: 5): Quantidade de páginas de listagem a percorrer.
    * `--delay` (default: 1.0): Tempo de espera (em segundos) entre requisições.

---

### 3. Sanitização e Extração de Sinais de Hype (`feature_engineering.py`)

Substituindo a dependência de datasets acadêmicos prontos, este script processa o texto raspado para extrair ativamente sinais de sensacionalismo para o modelo.

* **Limpeza de Ruído (Sanitização):** Remove tags HTML residuais, links de patrocinadores, botões de redes sociais e rodapés, isolando o corpo textual da notícia.
* **Criação de Atributos (Feature Engineering):** Varre o texto limpo em busca de padrões estruturais de linguagem hiperbólica.
* **Saída:** Une os dados sóbrios e os de hype gerando a tabela final `data/dataset_hype_treino.csv`.

#### Campos Principais do CSV Gerado:
* `id`: Identificador único.
* `label`: Classificação do texto (`sobrio` ou `hype`).
* `text`: Texto limpo e higienizado da notícia.
* `uppercase_words_percentage`: Densidade de palavras escritas totalmente em CAIXA ALTA.
* `exclamation_density`: Contagem e frequência de pontuação extrema (ex: `!!!`, `?!`).
* `extreme_adjectives_count`: Contagem da ocorrência de léxico de alarme (ex: "revolucionário", "urgente", "assustador", "fim", "milagroso").

---

## Boas Práticas e Política de Polidez (Politeness Policy)

Para garantir o bom comportamento dos scrapers e evitar sobrecarga nos servidores das fontes:
1. **User Agent Real:** Todos os scrapers enviam um cabeçalho `User-Agent` simulando um navegador moderno para passar em firewalls básicos.
2. **Tempo de Atraso (Delays):** Por padrão, há uma pausa de pelo menos 1.0 segundo entre cada requisição GET de artigo para respeitar os servidores.
3. **Tratamento de Erros:** Exceções de conexão e códigos HTTP de erro (diferentes de 200) são tratados para que uma falha em uma página não interrompa todo o processo de coleta.