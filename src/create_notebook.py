import os
import json

def create_baseline_notebook(notebook_path):
    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
    
    nb_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 🧠 Modelo Baseline Inicial - Projeto Inimigos do Prompt\n",
    "\n",
    "Este notebook estabelece a **linha de base (baseline)** para o modelo de Machine Learning capaz de identificar **sensacionalismo e hype** em notícias de tecnologia.\n",
    "\n",
    "## 🎯 Objetivos\n",
    "1. Carregar o dataset rotulado `data/dataset_hype_treino.csv`.\n",
    "2. Vetorizar os textos em linguagem natural usando **TF-IDF (Term Frequency - Inverse Document Frequency)**.\n",
    "3. Treinar dois classificadores lineares/estatísticos simples (**Multinomial Naive Bayes** e **Regressão Logística**).\n",
    "4. Avaliar os modelos focando no **$F_{0.5}$-Score** (que prioriza a Precisão para mitigar Falsos Positivos)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.feature_extraction.text import TfidfVectorizer\n",
    "from sklearn.linear_model import LogisticRegression\n",
    "from sklearn.naive_bayes import MultinomialNB\n",
    "from sklearn.metrics import (\n",
    "    accuracy_score, precision_score, recall_score, f1_score, \n",
    "    fbeta_score, classification_report, confusion_matrix, ConfusionMatrixDisplay\n",
    ")\n",
    "\n",
    "# Estilo dos gráficos\n",
    "sns.set_theme(style=\"whitegrid\")\n",
    "print(\"✅ Bibliotecas importadas com sucesso!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Carregamento e Inspeção dos Dados"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "csv_path = os.path.join(\"..\", \"data\", \"dataset_hype_treino.csv\")\n",
    "\n",
    "if not os.path.exists(csv_path):\n",
    "    # Se executado dentro da pasta notebooks/\n",
    "    csv_path = \"../data/dataset_hype_treino.csv\"\n",
    "\n",
    "df = pd.read_csv(csv_path)\n",
    "print(f\"Total de registros: {len(df)}\")\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Distribuição das classes\n",
    "plt.figure(figsize=(6, 4))\n",
    "sns.countplot(data=df, x='label', palette='viridis')\n",
    "plt.title('Distribuição das Classes no Dataset Piloto')\n",
    "plt.xlabel('Classe')\n",
    "plt.ylabel('Quantidade')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Divisão de Dados e Vetorização (TF-IDF)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "X = df['text']\n",
    "y = df['target'] # 0: Sóbrio, 1: Sensacionalista\n",
    "\n",
    "# Divisão 75% Treino e 25% Teste mantendo a proporção de classes (stratify)\n",
    "X_train, X_test, y_train, y_test = train_test_split(\n",
    "    X, y, test_size=0.25, random_state=42, stratify=y\n",
    ")\n",
    "\n",
    "# Vetorização por TF-IDF\n",
    "vectorizer = TfidfVectorizer(\n",
    "    ngram_range=(1, 2),\n",
    "    max_features=1000,\n",
    "    sublinear_tf=True\n",
    ")\n",
    "\n",
    "X_train_vec = vectorizer.fit_transform(X_train)\n",
    "X_test_vec = vectorizer.transform(X_test)\n",
    "\n",
    "print(f\"Treino: {X_train_vec.shape} | Teste: {X_test_vec.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Treinamento e Avaliação dos Modelos Baseline\n",
    "\n",
    "Testaremos dois classificadores clássicos:\n",
    "- **Multinomial Naive Bayes**\n",
    "- **Regressão Logística**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "models = {\n",
    "    \"Naive Bayes (MultinomialNB)\": MultinomialNB(),\n",
    "    \"Regressão Logística\": LogisticRegression(random_state=42)\n",
    "}\n",
    "\n",
    "results = []\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n",
    "\n",
    "for idx, (name, model) in enumerate(models.items()):\n",
    "    model.fit(X_train_vec, y_train)\n",
    "    y_pred = model.predict(X_test_vec)\n",
    "    \n",
    "    acc = accuracy_score(y_test, y_pred)\n",
    "    prec = precision_score(y_test, y_pred, pos_label=1)\n",
    "    rec = recall_score(y_test, y_pred, pos_label=1)\n",
    "    f1 = f1_score(y_test, y_pred, pos_label=1)\n",
    "    # F-0.5 Score dá peso 0.5 para Recall e 1.0 para Precisão (prioriza Precisão)\n",
    "    f05 = fbeta_score(y_test, y_pred, beta=0.5, pos_label=1)\n",
    "    \n",
    "    results.append({\n",
    "        \"Modelo\": name,\n",
    "        \"Acurácia\": acc,\n",
    "        \"Precisão\": prec,\n",
    "        \"Recall\": rec,\n",
    "        \"F1-Score\": f1,\n",
    "        \"F-0.5 Score (Alvo)\": f05\n",
    "    })\n",
    "    \n",
    "    # Matriz de Confusão Visual\n",
    "    cm = confusion_matrix(y_test, y_pred)\n",
    "    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[\"Sóbrio\", \"Sensacionalista\"])\n",
    "    disp.plot(ax=axes[idx], cmap='Blues', colorbar=False)\n",
    "    axes[idx].set_title(f\"Matriz de Confusão: {name}\")\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Tabela de Comparação de Desempenho"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "results_df = pd.DataFrame(results)\n",
    "display(results_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 📌 Conclusão e Próximos Passos\n",
    "- Este notebook estabeleceu o **piso de desempenho** para o projeto.\n",
    "- Qualquer arquitetura mais avançada (ex: Fine-Tuning de BERTimbau ou LLMs) deve obter um **$F_{0.5}$-Score** superior a este baseline com um custo computacional justificado."
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb_content, f, indent=1, ensure_ascii=False)
    print(f"Jupyter Notebook gerado com sucesso em: {notebook_path}")

if __name__ == "__main__":
    nb_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notebooks", "01_modelo_baseline.ipynb"))
    create_baseline_notebook(nb_file)
