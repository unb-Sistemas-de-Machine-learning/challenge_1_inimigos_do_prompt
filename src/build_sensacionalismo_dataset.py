"""
build_sensacionalismo_dataset.py
================================
Baixa o Fake.br-Corpus (USP/UFSCar), aplica filtros de domínio
para remover viés político, e salva um dataset limpo e balanceado
para treinar o classificador de Sensacionalismo/Hype (Tarefa 1).

Saída: data/dataset_sensacionalismo.csv
Colunas: text, label, target, uppercase_words_count, adjectives_count,
         emotiveness, avg_sentence_length, source
"""

import os
import re
import zipfile
import requests
import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
CORPUS_URL = "https://github.com/roneysco/Fake.br-Corpus/archive/refs/heads/master.zip"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
ZIP_PATH = os.path.join(DATA_DIR, "Fake.br-Corpus.zip")
EXTRACT_DIR = os.path.join(DATA_DIR, "Fake.br-Corpus-extracted")
OUTPUT_CSV = os.path.join(DATA_DIR, "dataset_sensacionalismo.csv")

# Termos estritamente político-partidários a serem filtrados.
# Qualquer texto com ALTA CONCENTRAÇÃO desses termos será descartado.
# Documentar aqui as escolhas editoriais do grupo conforme combinado.
POLITICAL_BLOCKLIST = [
    "lula", "bolsonaro", "stf", "senado", "câmara", "câmara dos deputados",
    "deputado", "petista", "golpista", "urna", "tse", "pleito eleitoral",
    "candidato presidencial", "pt ", " pp ", "psdb", "mdb ", "psl ",
    "governo federal", "ministério público", "procurador geral",
    "imposto de renda", "previdência social", "reforma trabalhista",
    "copa do mundo", "futebol", "campeonato", "jogador", "técnico",
    "pandemia", "covid", "vacina", "coronavírus", "ministério da saúde",
    "sus ", "ubs ", "sistema único de saúde"
]

# Termos que AUMENTAM a chance de ser tecnologia/ciência (bonus filter)
TECH_KEYWORDS = [
    "inteligência artificial", "ia ", " ai ", "machine learning",
    "algoritmo", "software", "hardware", "startup", "aplicativo", "app ",
    "internet", "rede", "servidor", "nuvem", "cloud", "dados", "hack",
    "criptomoeda", "bitcoin", "blockchain", "processador", "chip",
    "smartphone", "computador", "tecnologia", "inovação", "robô",
    "automação", "digital", "plataforma", "sistema", "código", "python",
    "ciência", "pesquisa", "universidade", "estudo", "cientistas",
    "engenharia", "satélite", "energia", "quantum", "quântico"
]

MIN_WORD_COUNT = 80
MAX_WORD_COUNT = 1500
MAX_POLITICAL_DENSITY = 0.015  # máx. de 1.5% do texto com termos políticos


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path):
        print(f"Arquivo ja existe, pulando download: {dest_path}")
        return
    print(f"Baixando corpus de: {url}")
    r = requests.get(url, stream=True)
    total = int(r.headers.get("content-length", 0))
    with open(dest_path, "wb") as f, tqdm(total=total, unit="iB", unit_scale=True) as bar:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            bar.update(len(chunk))
    print("Download concluido!")


def extract_zip(zip_path, dest_dir):
    if os.path.exists(dest_dir):
        print(f"Diretório extraído ja existe, pulando extração: {dest_dir}")
        return
    print(f"Extraindo {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    print("Extração concluida!")


def calc_political_density(text_lower: str) -> float:
    """Calcula a proporção de tokens políticos no texto."""
    words = text_lower.split()
    if not words:
        return 0.0
    hits = sum(1 for term in POLITICAL_BLOCKLIST if term in text_lower)
    return hits / len(words)


def has_tech_signal(text_lower: str) -> bool:
    """Retorna True se ao menos um termo tech/ciência aparecer no texto."""
    return any(kw in text_lower for kw in TECH_KEYWORDS)


def is_valid(text: str) -> bool:
    """Aplica todos os filtros e retorna True se o texto for aceito."""
    if not isinstance(text, str) or not text.strip():
        return False
    words = text.split()
    word_count = len(words)
    if word_count < MIN_WORD_COUNT or word_count > MAX_WORD_COUNT:
        return False
    text_lower = text.lower()
    if calc_political_density(text_lower) > MAX_POLITICAL_DENSITY:
        return False
    # Prioridade para textos com sinal tech (não obrigatório, mas preferido)
    # Descomente a linha abaixo para filtro ESTRITO de tecnologia:
    # if not has_tech_signal(text_lower): return False
    return True


def parse_meta(filepath: str) -> dict:
    """Lê arquivo de metadados do Fake.br e retorna dicionário de atributos."""
    meta = {}
    if not os.path.exists(filepath):
        return meta
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f.readlines()]
    field_map = [
        ("tokens_count", 4),
        ("words_without_punctuation", 5),
        ("types_count", 6),
        ("avg_sentence_length", 8),
        ("adjectives_count", 14),
        ("modal_verbs_count", 16),
        ("uppercase_words_count", 25),
        ("emotiveness", 22),
    ]
    for name, idx in field_map:
        if len(lines) > idx:
            val = lines[idx]
            try:
                meta[name] = float(val.replace(",", "."))
            except ValueError:
                meta[name] = None
    return meta


def load_corpus(corpus_base: str) -> pd.DataFrame:
    """Lê todos os arquivos .txt do Fake.br-Corpus e monta um DataFrame."""
    full_texts = os.path.join(corpus_base, "full_texts")
    categories = {
        "fake": {"text_dir": "fake", "meta_dir": "fake-meta-information", "label": "sensacionalista", "target": 1},
        "true": {"text_dir": "true", "meta_dir": "true-meta-information", "label": "sobrio", "target": 0},
    }
    rows = []
    for cat, cfg in categories.items():
        text_dir = os.path.join(full_texts, cfg["text_dir"])
        meta_dir = os.path.join(full_texts, cfg["meta_dir"])
        if not os.path.exists(text_dir):
            print(f"Diretório nao encontrado: {text_dir}")
            continue
        files = [f for f in os.listdir(text_dir) if f.endswith(".txt")]
        print(f"Processando {len(files)} arquivos de classe '{cat}'...")
        for fname in tqdm(files, desc=f"Lendo {cat}"):
            file_num = fname.split(".")[0]
            text_path = os.path.join(text_dir, fname)
            meta_path = os.path.join(meta_dir, f"{file_num}-meta.txt")
            if not os.path.exists(meta_path):
                meta_path = os.path.join(meta_dir, fname)

            with open(text_path, "r", encoding="utf-8", errors="ignore") as tf:
                text = tf.read().strip()

            meta = parse_meta(meta_path)
            rows.append({
                "text": text,
                "label": cfg["label"],
                "target": cfg["target"],
                "source": "fake_br_corpus",
                **meta,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("BUILD: dataset_sensacionalismo.csv (Fake.br-Corpus filtrado)")
    print("=" * 60)
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Download e extração
    download_file(CORPUS_URL, ZIP_PATH)
    extract_zip(ZIP_PATH, EXTRACT_DIR)

    # 2. Carrega corpus bruto
    corpus_base = os.path.join(EXTRACT_DIR, "Fake.br-Corpus-master")
    df_raw = load_corpus(corpus_base)
    print(f"\nCorpus bruto: {len(df_raw)} registros")
    print(df_raw["label"].value_counts().to_string())

    # 3. Aplica filtros
    print("\nAplicando filtros de domínio...")
    mask = df_raw["text"].apply(is_valid)
    df_filtered = df_raw[mask].copy()
    print(f"Apos filtragem: {len(df_filtered)} registros")
    print(df_filtered["label"].value_counts().to_string())

    # 4. Balanceamento: garante proporção 50/50 entre classes
    min_count = df_filtered["label"].value_counts().min()
    df_balanced = (
        df_filtered
        .groupby("label", group_keys=False)
        .apply(lambda g: g.sample(min_count, random_state=42))
        .reset_index(drop=True)
    )
    print(f"\nApos balanceamento (50/50): {len(df_balanced)} registros")
    print(df_balanced["label"].value_counts().to_string())

    # 5. Salva
    cols = ["text", "label", "target", "source",
            "uppercase_words_count", "adjectives_count",
            "emotiveness", "avg_sentence_length"]
    cols_present = [c for c in cols if c in df_balanced.columns]
    df_balanced[cols_present].to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nDataset salvo em: {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()
