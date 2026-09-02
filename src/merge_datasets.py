"""
merge_datasets.py
=================
Consolida todas as fontes de dados em um único arquivo final de treino
para o classificador de Sensacionalismo/Hype (Tarefa 1).

Fontes:
  - data/dataset_sensacionalismo.csv  (Fake.br-Corpus filtrado)
  - data/dataset_hype_treino.csv      (Newsletters reais raspadas pelo grupo)

Saída: data/dataset_final_treino.csv
Colunas: text, label, target, source
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

SOURCES = {
    "dataset_sensacionalismo.csv": {"text_col": "text",  "target_col": "target", "label_col": "label"},
    "dataset_hype_treino.csv":     {"text_col": "text",  "target_col": "target", "label_col": "label"},
}

OUTPUT_CSV = os.path.join(DATA_DIR, "dataset_final_treino.csv")
OUTPUT_TRAIN = os.path.join(DATA_DIR, "train.csv")
OUTPUT_TEST  = os.path.join(DATA_DIR, "test.csv")

TEST_SIZE   = 0.20
RANDOM_SEED = 42


def load_source(filename: str, cfg: dict) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[AVISO] Arquivo nao encontrado, pulando: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, encoding="utf-8")
    # Normaliza para colunas padrão
    df_out = pd.DataFrame({
        "text":   df[cfg["text_col"]],
        "target": df[cfg["target_col"]].astype(int),
        "label":  df[cfg["label_col"]],
        "source": filename.replace(".csv", ""),
    })
    df_out = df_out.dropna(subset=["text", "target"])
    df_out = df_out[df_out["text"].str.strip().str.len() > 0]
    return df_out


def main():
    print("=" * 60)
    print("MERGE: Consolidando fontes em dataset_final_treino.csv")
    print("=" * 60)

    frames = []
    for filename, cfg in SOURCES.items():
        df = load_source(filename, cfg)
        if not df.empty:
            print(f"  {filename}: {len(df)} registros carregados")
            frames.append(df)

    if not frames:
        print("Nenhuma fonte de dados encontrada. Execute os scripts de build primeiro.")
        return

    # 1. Concatena todas as fontes
    df_all = pd.concat(frames, ignore_index=True)

    # 2. Remove duplicatas exatas pelo texto
    before = len(df_all)
    df_all = df_all.drop_duplicates(subset=["text"])
    print(f"\nDuplicatas removidas: {before - len(df_all)}")

    # 3. Balanceamento 50/50 global
    min_count = df_all["target"].value_counts().min()
    df_balanced = (
        df_all
        .groupby("target", group_keys=False)
        .apply(lambda g: g.sample(min(len(g), min_count), random_state=RANDOM_SEED))
        .reset_index(drop=True)
    )

    print(f"\nDistribuicao apos balanceamento global:")
    print(df_balanced["label"].value_counts().to_string())
    print(f"\nDistribuicao por fonte:")
    print(df_balanced["source"].value_counts().to_string())

    # 4. Salva dataset completo
    df_balanced.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nDataset final salvo: {OUTPUT_CSV} ({len(df_balanced)} registros)")

    # 5. Gera split train/test estratificado
    df_train, df_test = train_test_split(
        df_balanced,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=df_balanced["target"],
    )

    df_train.to_csv(OUTPUT_TRAIN, index=False, encoding="utf-8")
    df_test.to_csv(OUTPUT_TEST, index=False, encoding="utf-8")

    print(f"Split de treino salvo: {OUTPUT_TRAIN} ({len(df_train)} registros)")
    print(f"Split de teste salvo:  {OUTPUT_TEST} ({len(df_test)} registros)")
    print("=" * 60)


if __name__ == "__main__":
    main()
