import os
import sys
import pandas as pd
import numpy as np

# Garantir codificação UTF-8 para stdout no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, fbeta_score, classification_report, confusion_matrix

def train_and_evaluate_baseline(csv_path):
    print("=" * 60)
    print("PROJETO INIMIGOS DO PROMPT - MODELO BASELINE INICIAL")
    print("=" * 60)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {csv_path}. Execute src/generate_sample_dataset.py primeiro.")
        
    # 1. Carregamento dos dados
    df = pd.read_csv(csv_path)
    print(f"-> Dataset carregado com sucesso: {len(df)} amostras.")
    print(f"-> Distribuição das classes:\n{df['label'].value_counts()}\n")
    
    # 2. Divisão Treino/Teste
    X = df['text']
    y = df['target'] # 0: sobrio, 1: sensacionalista
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"-> Conjunto de Treino: {len(X_train)} amostras | Teste: {len(X_test)} amostras")
    
    # 3. Vetorização TF-IDF
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=1000,
        sublinear_tf=True
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print("-> Vetorização TF-IDF concluída com sucesso.\n")
    
    # 4. Modelos Baseline
    models = {
        "Naive Bayes (MultinomialNB)": MultinomialNB(),
        "Regressão Logística": LogisticRegression(random_state=42)
    }
    
    results = []
    
    for name, model in models.items():
        print("-" * 50)
        print(f"Treinando e Avaliando: {name}")
        print("-" * 50)
        
        model.fit(X_train_vec, y_train)
        y_pred = model.predict(X_test_vec)
        
        # Cálculo das Métricas
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, pos_label=1)
        rec = recall_score(y_test, y_pred, pos_label=1)
        f1 = f1_score(y_test, y_pred, pos_label=1)
        
        # Métrica Principal do Projeto: F-0.5 Score (Prioriza Precisão)
        f05 = fbeta_score(y_test, y_pred, beta=0.5, pos_label=1)
        
        print(f"Acurácia:     {acc:.4f}")
        print(f"Precisão:     {prec:.4f}")
        print(f"Recall:       {rec:.4f}")
        print(f"F1-Score:     {f1:.4f}")
        print(f"F-0.5 Score (Metrica Alvo): {f05:.4f}")
        print("\nMatriz de Confusao:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print("\nRelatório de Classificacao:")
        print(classification_report(y_test, y_pred, target_names=["Sóbrio", "Sensacionalista"]))
        
        results.append({
            "Modelo": name,
            "Acurácia": acc,
            "Precisão": prec,
            "Recall": rec,
            "F1-Score": f1,
            "F-0.5 Score (Piso Alvo)": f05
        })
        
    print("=" * 60)
    print("RESUMO DOS RESULTADOS DO BASELINE")
    print("=" * 60)
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    print("=" * 60)
    
    return res_df

if __name__ == "__main__":
    csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dataset_hype_treino.csv"))
    train_and_evaluate_baseline(csv_file)
