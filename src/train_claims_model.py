import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DATASET_PATH = os.path.join(DATA_DIR, "dataset_claims.csv")
ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "ml", "artifacts"))

def main():
    print("=" * 60)
    print("TREINO: Classificador de Alegações (Claims)")
    print("=" * 60)

    if not os.path.exists(DATASET_PATH):
        print(f"Erro: Arquivo não encontrado em {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset carregado com {len(df)} registros. Colunas encontradas: {list(df.columns)}")

    # Correção à prova de falhas: recria o 'target' se ele não estiver no CSV
    if 'target' not in df.columns:
        if 'label' in df.columns:
            df['target'] = df['label'].map({'legitimo': 0, 'desinformacao': 1})
            print("Coluna 'target' recriada a partir da coluna 'label'.")
        else:
            print("Erro: O dataset não possui as colunas 'target' nem 'label'.")
            return

    df = df.dropna(subset=['claim', 'target'])
    X = df['claim'].astype(str)
    y = df['target'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_vec, y_train)

    print("\n--- Avaliação no conjunto de teste ---")
    y_pred = model.predict(X_test_vec)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=["Legítimo (0)", "Desinformação (1)"]))
    
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    model_path = os.path.join(ARTIFACTS_DIR, "claims_model.joblib")
    vec_path = os.path.join(ARTIFACTS_DIR, "claims_vectorizer.joblib")

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vec_path)

    print(f"\nArtefatos salvos com sucesso no diretório do backend!")
    print(f"- {model_path}")
    print(f"- {vec_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()