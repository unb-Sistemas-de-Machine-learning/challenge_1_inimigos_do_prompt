# Coleta e Ingestão de Dados

Esta seção detalha o fluxo de coleta, processamento de ruído e consolidação de dados utilizados para treinar e avaliar o modelo. O projeto consome tanto datasets consolidados de referência em Fake News quanto scrapings de portais ativos para manter os dados atualizados.

---

## 📂 Visão Geral dos Datasets Gerados

Os dados coletados são armazenados na pasta `data/` nos seguintes arquivos:

| Arquivo | Origem | Descrição | Registros |
| :--- | :--- | :--- | :--- |
| `fake_br_corpus.csv` | `Fake.br-Corpus` (GitHub) | Dataset de referência brasileiro com textos verdadeiros e falsos emparelhados e enriquecido com 27 atributos estatísticos de texto. | 7.200 |
| `scraped_fake_news.csv` | `Boatos.org` (Scraping) | Coleta sob demanda de artigos do portal de checagem Boatos.org contendo o texto do boato e o texto de checagem (debunking). | Variável |
| `tech_news.csv` | `Manual do Usuário` & `G1 Tecnologia` (Scraping) | Notícias reais de tecnologia recentes para servir como fonte de dados não sensacionalistas em português técnico. | Variável |

---

## 🛠️ Detalhes dos Scripts de Ingestão (`src/`)

### 1. Consolidificador do Fake.br-Corpus (`downloader_fake_datasets.py`)

Este script gerencia o ciclo completo de obtenção do corpus de referência `Fake.br-Corpus`:

* **Download & Extração:** Baixa o arquivo ZIP do repositório oficial do Fake.br-Corpus no GitHub e extrai os arquivos.
* **Processamento de Metadados:** Cada notícia possui um arquivo de texto correspondente de metadados estatísticos contendo informações do autor, categoria, data e 23 métricas linguísticas (como contagem de tokens, erros ortográficos, taxa de emotividade, quantidade de verbos no imperativo, etc.). O script faz o *parsing* estruturado desses atributos.
* **Saída:** Une textos e metadados gerando a tabela final `data/fake_br_corpus.csv`.

#### Campos Principais do CSV Gerado:
* `id`: Identificador único (ex: `fake_123`, `true_123`).
* `label`: Classificação do texto (`fake` ou `true`).
* `text`: Texto limpo da notícia.
* `author`, `link`, `category`, `date_of_publication`: Metadados da postagem.
* `tokens_count`, `words_without_punctuation`, `spelling_errors_percentage`, `emotiveness`, `uppercase_words_count` e mais 18 métricas linguísticas.

---

### 2. Scraper de Boatos (`scraper_fake_news.py`)

Responsável por raspar conteúdo do portal de checagem `Boatos.org`, um dos principais portais de debunking de fake news do Brasil.

* **Fluxo de Scraping:**
    1. Acessa as páginas de listagem (`https://www.boatos.org/page/{n}`).
    2. Extrai título, URL de destino, categoria e data de publicação.
    3. Entra em cada link coletado para obter os detalhes:
        * **Texto do Boato (Hoax):** Extraído de blocos `<blockquote>`.
        * **Texto de Checagem (Debunking):** Extraído de parágrafos normais limpos de publicidade e scripts.
* **Parâmetros de Linha de Comando:**
    * `--pages` (default: 5): Quantidade de páginas de listagem a percorrer.
    * `--delay` (default: 1.0): Tempo de espera (em segundos) entre requisições para evitar bloqueios (Politeness Policy).

---

### 3. Scraper de Notícias de Tecnologia (`scraper_tech_news.py`)

Utilizado para construir o conjunto de dados sob o domínio de tecnologia em português. Ele raspa duas fontes principais:

* **Manual do Usuário (`manualdousuario.net`):**
    * Foco em análises críticas e notícias aprofundadas sobre tecnologia e sociedade.
    * Extrai os textos principais a partir da classe `.e-content`.
* **G1 Tecnologia (`g1.globo.com/tecnologia`):**
    * Notícias factuais de tecnologia no Brasil.
    * Extrai artigos iterando pelo feed de paginação pública e obtendo parágrafos com a classe `.content-text__container`.
* **Parâmetros de Linha de Comando:**
    * `--pages` (default: 3): Páginas de listagem raspadas por fonte.
    * `--delay` (default: 1.0): Tempo de espera entre as requisições.

---

## 🛡️ Boas Práticas e Política de Polidez (Politeness Policy)

Para garantir o bom comportamento dos scrapers e evitar sobrecarga nos servidores das fontes:
1. **User Agent Real:** Todos os scrapers enviam um cabeçalho `User-Agent` simulando um navegador moderno (Chrome no macOS) para passar em firewalls básicos.
2. **Tempo de Atraso (Delays):** Por padrão, há uma pausa de pelo menos 1.0 segundo entre cada requisição GET de artigo para respeitar os servidores.
3. **Tratamento de Erros:** Exceções de conexão e códigos HTTP de erro (diferentes de 200) são tratados para que uma falha em uma página não interrompa todo o processo de coleta.
