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
import pandas as pd

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
    "contraditório", "exagerado",
]
LABEL_MAP_NEGATIVE = [  # legítimo → target=0
    "verdadeiro", "correto", "real", "confirmado", "verificado",
    "verdade", "comprovado",
]

MIN_CLAIM_WORDS = 8  # Descartar alegações muito curtas


def normalize_label(label_str: str) -> int | None:
    """Converte label original para 0 ou 1. Retorna None se inconclusivo."""
    if not isinstance(label_str, str):
        return None
    label_lower = label_str.lower().strip()
    for pos in LABEL_MAP_POSITIVE:
        if pos in label_lower:
            return 1
    for neg in LABEL_MAP_NEGATIVE:
        if neg in label_lower:
            return 0
    return None  # Label ambíguo → descartar


def is_relevant_category(category: str) -> bool:
    """Retorna True se a categoria da checagem for relevante para o projeto."""
    if not isinstance(category, str):
        return False
    cat_lower = category.lower()
    return any(rel in cat_lower for rel in RELEVANT_CATEGORIES)


def load_factchecks_br() -> pd.DataFrame:
    """
    Baixa o dataset FactChecks.br via Hugging Face datasets.
    Requer: pip install datasets
    """
    try:
        from datasets import load_dataset
        print("Carregando FactChecks.br do Hugging Face...")
        ds = load_dataset("fake-news-UFG/FactChecksbr", trust_remote_code=True)
        # O dataset pode ter splits diferentes; tentamos concatenar todos
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

    # 2. Inspeciona colunas para identificar campos de claim, label e categoria
    print(f"\nAmostra das primeiras linhas:\n{df_raw.head(3).to_string()}\n")

    # Tenta identificar automaticamente as colunas mais comuns do FactChecks.br
    # (claim, verdict/label, category/topic, source/agency)
    col_claim = next((c for c in df_raw.columns if "claim" in c.lower() or "text" in c.lower() or "alegacao" in c.lower()), None)
    col_label = next((c for c in df_raw.columns if "label" in c.lower() or "verdict" in c.lower() or "classificacao" in c.lower()), None)
    col_cat   = next((c for c in df_raw.columns if "categ" in c.lower() or "topic" in c.lower() or "assunto" in c.lower()), None)
    col_agency = next((c for c in df_raw.columns if "source" in c.lower() or "agency" in c.lower() or "agencia" in c.lower()), None)

    print(f"Coluna de claim detectada: {col_claim}")
    print(f"Coluna de label detectada: {col_label}")
    print(f"Coluna de categoria detectada: {col_cat}")
    print(f"Coluna de agência detectada: {col_agency}")

    if not col_claim or not col_label:
        print("\nNao foi possível detectar colunas de claim/label automaticamente.")
        print("Ajuste manualmente as variáveis col_claim e col_label neste script.")
        return

    # 3. Filtra por categoria (se disponível) e normaliza labels
    df = df_raw.copy()

    if col_cat:
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
        "agency": df[col_agency].values if col_agency else "desconhecida",
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
