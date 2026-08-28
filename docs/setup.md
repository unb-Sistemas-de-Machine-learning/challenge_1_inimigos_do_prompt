# Guia de Configuração e Execução

Este guia orienta na configuração do ambiente de desenvolvimento, instalação das dependências, execução dos scripts de ingestão e visualização local da documentação.

---

## 1. Configurando o Ambiente Virtual Python

Recomendamos utilizar um ambiente virtual (`venv`) para gerenciar as dependências do projeto de forma isolada.

No seu terminal, execute os seguintes comandos:

=== "macOS / Linux"
    ```bash
    # Criar o ambiente virtual na pasta .venv
    python3 -m venv .venv

    # Ativar o ambiente virtual
    source .venv/bin/activate
    ```

=== "Windows (CMD)"
    ```cmd
    :: Criar o ambiente virtual na pasta .venv
    python -m venv .venv

    :: Ativar o ambiente virtual
    .venv\Scripts\activate.bat
    ```

=== "Windows (PowerShell)"
    ```powershell
    # Criar o ambiente virtual na pasta .venv
    python -m venv .venv

    # Ativar o ambiente virtual
    .venv\Scripts\Activate.ps1
    ```

---

## 2. Instalando as Dependências

Com o ambiente virtual ativado, instale os pacotes necessários descritos em `requirements.txt`:

```bash
pip install -r requirements.txt
```

> [!NOTE]
> Este comando irá instalar as bibliotecas de processamento (`pandas`, `beautifulsoup4`, etc.) e as ferramentas necessárias para rodar este site de documentação (`mkdocs` e `mkdocs-material`).

---

## 3. Executando os Scripts de Coleta de Dados

Com todas as dependências instaladas, você pode rodar os scripts de ingestão a partir da pasta raiz do projeto.

### A. Consolidar o Fake.br-Corpus
Este script faz o download do dataset de referência e faz o parse de seus metadados:
```bash
python src/downloader_fake_datasets.py
```
* **Destino:** Salva o arquivo consolidado em `data/fake_br_corpus.csv`.

### B. Coletar dados do Boatos.org
Executa o scraper para obter fake news recentes e suas checagens:
```bash
# Executa com as configurações padrão (5 páginas, 1s de delay)
python src/scraper_fake_news.py

# Personalizando número de páginas e delay entre requisições
python src/scraper_fake_news.py --pages 10 --delay 2.0
```
* **Destino:** Salva o arquivo em `data/scraped_fake_news.csv`.

### C. Coletar dados de Notícias de Tecnologia
Executa o scraper de portais de notícias de tecnologia (Manual do Usuário e G1):
```bash
# Executa com as configurações padrão (3 páginas, 1s de delay)
python src/scraper_tech_news.py

# Personalizando número de páginas e delay entre requisições
python src/scraper_tech_news.py --pages 5 --delay 1.5
```
* **Destino:** Salva o arquivo em `data/tech_news.csv`.

---

## 4. Visualizando a Documentação Localmente

O MkDocs permite visualizar as alterações nas páginas Markdown em tempo real usando um servidor web local.

### Iniciar o Servidor de Desenvolvimento
Rode o comando abaixo na raiz do projeto:
```bash
mkdocs serve
```

* **Acesso:** Abra o navegador em [http://127.0.0.1:8000](http://127.0.0.1:8000).
* **Hot Reload:** O site é atualizado automaticamente conforme você edita e salva arquivos na pasta `docs/`.

### Gerar os Arquivos HTML (Build de Produção)
Se desejar gerar a versão estática final para hospedagem no GitHub Pages ou outro servidor web:
```bash
mkdocs build --strict
```
* **Destino:** Os arquivos estáticos finais serão gerados no diretório `site/` na raiz do projeto.
* O parâmetro `--strict` garante que a compilação falhe caso existam links quebrados ou avisos pendentes.
