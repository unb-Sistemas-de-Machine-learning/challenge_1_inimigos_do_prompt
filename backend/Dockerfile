FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Baixa os modelos do nltk pro cache do container
RUN python -c "import nltk; nltk.download('punkt_tab')"

# Copia o código
COPY app/ ./app/

# Expõe porta
EXPOSE 8000

# Comando pra iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
