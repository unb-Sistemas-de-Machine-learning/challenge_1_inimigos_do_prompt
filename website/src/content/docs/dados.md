---
title: Coleta e Preparação de Dados
---

Esta página descreve o pipeline que existe hoje no diretório `src/`. Os arquivos em `data/` são gerados localmente, não fazem parte do repositório e precisam ser produzidos antes do treinamento.

## Fluxograma do Pipeline de Dados

```mermaid
flowchart TD
    subgraph Fontes["Fontes Externas"]
        F1["Fake.br-Corpus (GitHub)"]
        F2["FactChecks.br (Hugging Face)"]
        F3["Web Scraping (G1 / Manual do Usuário)"]
        F4["Web Scraping (Boatos.org)"]
    end

    subgraph Scripts["Processamento & Normalização"]
        S1["build_sensacionalismo_dataset.py"]
        S2["build_claims_dataset.py"]
        S3["scraper_tech_news.py"]
        S4["scraper_fake_news.py"]
        S5["generate_sample_dataset.py"]
    end

    subgraph Datasets["Datasets Gerados (data/)"]
        D1[("dataset_sensacionalismo.csv")]
        D2[("dataset_claims.csv")]
        D3[("tech_news.csv")]
        D4[("scraped_fake_news.csv")]
        D5[("dataset_hype_treino.csv")]
    end

    subgraph Merge["Consolidação & Split"]
        M1["merge_datasets.py"]
        DF[("dataset_final_treino.csv")]
        TR[("train.csv (80%)")]
        TE[("test.csv (20%)")]
    end

    subgraph Treino["Consumo em Modelagem"]
        TB["train_baseline.py<br/>(TF-IDF + Naive Bayes / RegLog)"]
        BT["Fine-Tuning BERTimbau<br/>(neuralmind/bert-base-portuguese-cased)"]
    end

    F1 --> S1 --> D1
    F2 --> S2 --> D2
    F3 --> S3 --> D3
    F4 --> S4 --> D4
    S5 --> D5

    D1 & D5 --> M1
    M1 --> DF --> TR & TE
    TR & TE --> TB
    TR & TE --> BT
```

---

## Estrutura e Transformação dos Registros

```mermaid
flowchart LR
    Raw["Texto Bruto / Notícia"] --> Clean["Sanitização Regex & HTML"]
    Clean --> Feat["Extração de Sinais Linguísticos"]
    
    subgraph Sinais["Features Heurísticas"]
        Feat --> F1["uppercase_words_percentage"]
        Feat --> F2["exclamation_density"]
        Feat --> F3["extreme_adjectives_count"]
    end

    Clean --> Label["Mapeamento de Classes"]
    Label --> L1["0: Sóbrio"]
    Label --> L2["1: Sensacionalista"]
```

---

## Fontes e saídas atuais

| Script | Fonte | Saída | Uso atual |
| --- | --- | --- | --- |
| `build_sensacionalismo_dataset.py` | Fake.br-Corpus | `dataset_sensacionalismo.csv` | Fonte principal para o classificador binário de hype. |
| `build_claims_dataset.py` | FactChecks.br (Hugging Face) | `dataset_claims.csv` | Preparação para a tarefa futura de alegações; ainda não é consumido pela API. |
| `scraper_tech_news.py` | Manual do Usuário e G1 Tecnologia | `tech_news.csv` | Coleta de textos tecnológicos não rotulados. |
| `scraper_fake_news.py` | Boatos.org | `scraped_fake_news.csv` | Coleta de boatos e textos de desmentido; ainda não entra no merge de treino. |
| `generate_sample_dataset.py` | Exemplos sintéticos do projeto | `dataset_hype_treino.csv` | Dataset demonstrativo para validar o pipeline. |
| `merge_datasets.py` | Datasets de sensacionalismo e de amostra | `dataset_final_treino.csv`, `train.csv`, `test.csv` | Consolidação, deduplicação, balanceamento e split estratificado. |

> [!NOTE]
> O diretório `data/` está no `.gitignore`. Assim, não há dataset nem métricas reproduzíveis versionadas neste repositório.

## Pipeline de sensacionalismo

`build_sensacionalismo_dataset.py` baixa o Fake.br-Corpus, remove textos fora dos limites de tamanho e textos com alta incidência de termos político-partidários. Em seguida, equilibra as duas classes e salva texto, rótulo, target e algumas métricas linguísticas extraídas do corpus.

No estado atual, `target=1` corresponde à classe `fake` do corpus e é renomeado para `sensacionalista`; `target=0` corresponde à classe `true` e é renomeado para `sobrio`. Essa é uma aproximação para a tarefa de hype, não uma anotação humana direta de sensacionalismo. Além disso, o filtro de tecnologia é apenas preferencial: a verificação estrita está desativada no código. Esses limites devem ser considerados ao interpretar resultados.

## Alegações e risco de desinformação

`build_claims_dataset.py` baixa FactChecks.br, normaliza os rótulos para `legitimo` (0) e `desinformacao` (1), remove alegações curtas e tenta balancear as classes. Atualmente o filtro de categoria aceita todas as categorias para manter volume.

O arquivo gerado é preparatório. O endpoint da API ainda não usa um classificador treinado com essas alegações: o campo `disinformation_risk` é uma heurística derivada do score de hype e das frases encontradas.

## Scrapers

Os dois scrapers usam `requests`, BeautifulSoup, um `User-Agent` de navegador e o parâmetro `--delay` para reduzir a carga sobre os sites.

- `scraper_tech_news.py` extrai título, URL, data quando disponível e corpo de artigos do Manual do Usuário e G1.
- `scraper_fake_news.py` extrai título, URL, categoria, o texto do boato (quando presente) e os parágrafos de desmentido do Boatos.org.

Como os seletores HTML dependem dos sites externos, as coletas podem deixar de funcionar quando suas páginas forem alteradas. Os resultados também não recebem rótulo automaticamente nem são integrados ao dataset final por enquanto.

## Sequência recomendada

```bash
# Dados reais para o classificador de hype
python src/build_sensacionalismo_dataset.py

# Dados demonstrativos, se for necessário completar a segunda fonte do merge
python src/generate_sample_dataset.py

# Consolidação e splits
python src/merge_datasets.py

# Avaliação dos baselines
python src/train_baseline.py
```

Para preparar o dataset de alegações, execute separadamente:

```bash
python src/build_claims_dataset.py
```
