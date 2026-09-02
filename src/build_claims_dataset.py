"""
build_claims_dataset.py
=======================
Baixa o FactChecks.br (Hugging Face / fake-news-UFG), filtra
apenas alegações sobre tecnologia, ciência e economia digital,
padroniza os labels e salva o dataset de claims de desinformação.

Saída: data/dataset_claims.csv
Colunas: claim, label, target, agency, source
"""

import os
import sys
from typing import Optional
import pandas as pd

# Garantir codificação UTF-8 para stdout no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
OUTPUT_CSV = os.path.join(DATA_DIR, "dataset_claims.csv")

# Categorias do FactChecks.br que são relevantes para o projeto
RELEVANT_CATEGORIES = [
    "tecnologia", "tech", "ciência", "ciencia", "saúde digital",
    "economia", "finanças", "investimento", "internet", "segurança",
    "meio ambiente", "inovacao", "inovação",
]

# Mapeamento de labels heterogêneos → binário do projeto
LABEL_MAP_POSITIVE = [  # desinformação → target=1
    "falso", "fake", "enganoso", "distorcido", "impreciso",
    "insustentável", "sem evidências", "descontextualizado",
    "contraditório", "exagerado", "1", "2"
]
LABEL_MAP_NEGATIVE = [  # legítimo → target=0
    "verdadeiro", "correto", "real", "confirmado", "verificado",
    "verdade", "comprovado", "0"
]

MIN_CLAIM_WORDS = 8  # Descartar alegações muito curtas


def normalize_label(label_val) -> Optional[int]:
    """Converte label original para 0 ou 1. Retorna None se inconclusivo."""
    if isinstance(label_val, (int, float)):
        val = int(label_val)
        if val == 2 or val == 1:
            return 1
        elif val == 0:
            return 0
        return None
    if not isinstance(label_val, str):
        return None
    label_lower = label_val.lower().strip()
    for pos in LABEL_MAP_POSITIVE:
        if pos == label_lower or pos in label_lower:
            return 1
    for neg in LABEL_MAP_NEGATIVE:
        if neg == label_lower or neg in label_lower:
            return 0
    return None  # Label ambíguo → descartar


def is_relevant_category(category: str) -> bool:
    """Retorna True se a categoria da checagem for relevante para o projeto."""
    if not isinstance(category, str):
        return False
    cat_lower = category.lower()
    return True # Deixando livre para ter volume no baseline


def load_factchecks_br() -> pd.DataFrame:
    """
    Baixa o dataset FactChecks.br via Hugging Face datasets.
    Requer: pip install datasets
    """
    try:
        from datasets import load_dataset
        print("Carregando FactChecks.br do Hugging Face...")
        ds = load_dataset("fake-news-UFG/FactChecksbr", trust_remote_code=True)
        # O dataset possui split 'train'
        splits = list(ds.keys())
        print(f"Splits encontrados: {splits}")
        dfs = [ds[split].to_pandas() for split in splits]
        df = pd.concat(dfs, ignore_index=True)
        print(f"Total de registros brutos: {len(df)}")
        print(f"Colunas disponíveis: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Erro ao carregar FactChecks.br: {e}")
        print("Verifique se o pacote 'datasets' está instalado: pip install datasets")
        return pd.DataFrame()


def main():
    print("=" * 60)
    print("BUILD: dataset_claims.csv (FactChecks.br filtrado)")
    print("=" * 60)
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Carrega dataset bruto
    df_raw = load_factchecks_br()
    if df_raw.empty:
        print("Dataset vazio. Abortando.")
        return

    # Mapeamento explícito das colunas detectadas no FactChecks.br
    col_claim = "claim_text"
    col_label = "is_fake"
    col_cat   = "category"
    col_agency = "claim_author"

    # 3. Filtra por categoria (se disponível) e normaliza labels
    df = df_raw.copy()

    if col_cat in df.columns:
        mask_cat = df[col_cat].apply(is_relevant_category)
        df = df[mask_cat].copy()
        print(f"\nApos filtro de categoria: {len(df)} registros")

    # Normaliza labels → 0 ou 1
    df["target"] = df[col_label].apply(normalize_label)
    df = df[df["target"].notna()].copy()
    df["target"] = df["target"].astype(int)
    print(f"Apos normalização de labels: {len(df)} registros")

    # 4. Filtra por tamanho mínimo de claim
    df["claim"] = df[col_claim].astype(str)
    df = df[df["claim"].apply(lambda t: len(t.split()) >= MIN_CLAIM_WORDS)].copy()
    print(f"Apos filtro de tamanho: {len(df)} registros")

    # 5. Monta DataFrame final
    df_out = pd.DataFrame({
        "claim": df["claim"].values,
        "target": df["target"].values,
        "label": df["target"].map({0: "legitimo", 1: "desinformacao"}),
        "agency": df[col_agency].values if col_agency in df.columns else "desconhecida",
        "source": "factchecks_br",
    })

    # 6. Balanceamento 50/50
    min_count = df_out["target"].value_counts().min()
    df_balanced = (
        df_out
        .groupby("target", group_keys=False)
        .apply(lambda g: g.sample(min(len(g), min_count), random_state=42))
        .reset_index(drop=True)
    )

    print(f"\nDistribuição apos balanceamento:")
    print(df_balanced["label"].value_counts().to_string())

    # 7. Salva
    df_balanced.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nDataset salvo em: {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()
