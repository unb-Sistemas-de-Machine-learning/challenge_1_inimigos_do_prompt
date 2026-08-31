import os
import json

NOTEBOOK_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "notebooks", "02_fine_tuning_bertimbau.ipynb")
)

NB = {
 "nbformat": 4,
 "nbformat_minor": 5,
 "metadata": {
  "language_info": {"name": "python"},
  "kernelspec": {"name": "python3", "display_name": "Python 3"}
 },
 "cells": [

  # ── Célula 0: Título ──────────────────────────────────────────────────────
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Fine-Tuning BERTimbau — Detecção de Sensacionalismo\n",
    "\n",
    "**Projeto:** Inimigos do Prompt  \n",
    "**Objetivo:** Ajustar finamente o modelo `neuralmind/bert-base-portuguese-cased` (BERTimbau)\n",
    "no dataset consolidado de newsletters tech para superar o baseline de TF-IDF em F-0.5 Score.\n",
    "\n",
    "> **Ambiente recomendado:** Google Colab ou Kaggle Notebook com GPU T4 ativa.\n",
    "> No Colab: Ambiente → Alterar tipo de runtime → GPU.\n"
   ]
  },

  # ── Célula 1: Instalação de dependências ──────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Instalar dependências (necessário no Colab)\n",
    "!pip install -q transformers datasets accelerate scikit-learn pandas"
   ]
  },

  # ── Célula 2: Imports ─────────────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "from sklearn.metrics import fbeta_score, classification_report\n",
    "from transformers import (\n",
    "    BertTokenizerFast,\n",
    "    BertForSequenceClassification,\n",
    "    TrainingArguments,\n",
    "    Trainer,\n",
    ")\n",
    "from datasets import Dataset, DatasetDict\n",
    "import torch\n",
    "\n",
    "device = 'cuda' if torch.cuda.is_available() else 'cpu'\n",
    "print(f'Dispositivo detectado: {device}')\n",
    "if device == 'cpu':\n",
    "    print('[AVISO] GPU nao detectada! O fine-tuning sera muito lento. Use Colab com GPU T4.')"
   ]
  },

  # ── Célula 3: Carregar dados ───────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Se estiver no Colab, faça o upload manual do CSV ou clone o repositório:\n",
    "# !git clone https://github.com/unb-Sistemas-de-Machine-learning/challenge_1_inimigos_do_prompt.git\n",
    "# %cd challenge_1_inimigos_do_prompt\n",
    "\n",
    "TRAIN_CSV = '../data/train.csv'\n",
    "TEST_CSV  = '../data/test.csv'\n",
    "\n",
    "# Fallback: usa dataset_final_treino.csv se splits nao existirem\n",
    "if not os.path.exists(TRAIN_CSV):\n",
    "    from sklearn.model_selection import train_test_split\n",
    "    df_all = pd.read_csv('../data/dataset_final_treino.csv')\n",
    "    df_train, df_test = train_test_split(df_all, test_size=0.2, stratify=df_all['target'], random_state=42)\n",
    "else:\n",
    "    df_train = pd.read_csv(TRAIN_CSV)\n",
    "    df_test  = pd.read_csv(TEST_CSV)\n",
    "\n",
    "print(f'Treino: {len(df_train)} | Teste: {len(df_test)}')\n",
    "print(df_train['label'].value_counts())"
   ]
  },

  # ── Célula 4: Tokenização ─────────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "MODEL_NAME = 'neuralmind/bert-base-portuguese-cased'\n",
    "MAX_LEN    = 256  # BERTimbau suporta até 512 tokens; 256 é suficiente para newsletters\n",
    "\n",
    "tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)\n",
    "\n",
    "def tokenize(batch):\n",
    "    return tokenizer(\n",
    "        batch['text'],\n",
    "        padding='max_length',\n",
    "        truncation=True,\n",
    "        max_length=MAX_LEN,\n",
    "    )\n",
    "\n",
    "# Converte DataFrames para formato HuggingFace Dataset\n",
    "hf_train = Dataset.from_pandas(df_train[['text', 'target']].rename(columns={'target': 'labels'}))\n",
    "hf_test  = Dataset.from_pandas(df_test[['text', 'target']].rename(columns={'target': 'labels'}))\n",
    "\n",
    "hf_train = hf_train.map(tokenize, batched=True)\n",
    "hf_test  = hf_test.map(tokenize, batched=True)\n",
    "\n",
    "hf_train.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])\n",
    "hf_test.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])\n",
    "\n",
    "print('Tokenizacao concluida!')"
   ]
  },

  # ── Célula 5: Definir métricas ────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Metrica customizada: F-0.5 Score (peso duplo para Precisao, minimiza Falsos Positivos)\n",
    "def compute_metrics(eval_pred):\n",
    "    logits, labels = eval_pred\n",
    "    predictions = np.argmax(logits, axis=-1)\n",
    "    f05  = fbeta_score(labels, predictions, beta=0.5, pos_label=1, average='binary')\n",
    "    f1   = fbeta_score(labels, predictions, beta=1.0, pos_label=1, average='binary')\n",
    "    prec = fbeta_score(labels, predictions, beta=0.01, pos_label=1, average='binary')  # ~precisao pura\n",
    "    return {\n",
    "        'f0_5_score': f05,\n",
    "        'f1_score':   f1,\n",
    "        'precision':  prec,\n",
    "    }"
   ]
  },

  # ── Célula 6: Modelo e TrainingArguments ─────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "model = BertForSequenceClassification.from_pretrained(\n",
    "    MODEL_NAME,\n",
    "    num_labels=2,\n",
    "    id2label={0: 'sobrio', 1: 'sensacionalista'},\n",
    "    label2id={'sobrio': 0, 'sensacionalista': 1},\n",
    ")\n",
    "\n",
    "training_args = TrainingArguments(\n",
    "    output_dir='../models/bertimbau_sensacionalismo',\n",
    "    eval_strategy='epoch',\n",
    "    save_strategy='epoch',\n",
    "    num_train_epochs=3,\n",
    "    per_device_train_batch_size=16,\n",
    "    per_device_eval_batch_size=32,\n",
    "    learning_rate=2e-5,\n",
    "    warmup_ratio=0.1,\n",
    "    weight_decay=0.01,\n",
    "    load_best_model_at_end=True,\n",
    "    metric_for_best_model='f0_5_score',\n",
    "    greater_is_better=True,\n",
    "    logging_steps=50,\n",
    "    fp16=(device == 'cuda'),  # Mixed precision somente com GPU\n",
    "    report_to='none',\n",
    ")\n",
    "\n",
    "trainer = Trainer(\n",
    "    model=model,\n",
    "    args=training_args,\n",
    "    train_dataset=hf_train,\n",
    "    eval_dataset=hf_test,\n",
    "    compute_metrics=compute_metrics,\n",
    ")\n",
    "\n",
    "print('Modelo e Trainer configurados!')"
   ]
  },

  # ── Célula 7: Treinamento ─────────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "print('Iniciando fine-tuning do BERTimbau...')\n",
    "trainer.train()\n",
    "print('Fine-tuning concluido!')"
   ]
  },

  # ── Célula 8: Avaliação final ─────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = trainer.evaluate()\n",
    "print('\\nResultados finais no conjunto de teste:')\n",
    "for k, v in results.items():\n",
    "    print(f'  {k}: {v:.4f}')\n",
    "\n",
    "# Classificação detalhada\n",
    "preds = trainer.predict(hf_test)\n",
    "y_pred = np.argmax(preds.predictions, axis=-1)\n",
    "y_true = preds.label_ids\n",
    "print('\\nRelatório de Classificação completo:')\n",
    "print(classification_report(y_true, y_pred, target_names=['Sobrio', 'Sensacionalista']))"
   ]
  },

  # ── Célula 9: Salvar modelo ───────────────────────────────────────────────
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "save_path = '../models/bertimbau_sensacionalismo_final'\n",
    "trainer.save_model(save_path)\n",
    "tokenizer.save_pretrained(save_path)\n",
    "print(f'Modelo salvo em: {save_path}')\n",
    "print('Para usar a API, aponte MODEL_PATH para este diretorio.')"
   ]
  },

  # ── Célula 10: Conclusão ──────────────────────────────────────────────────
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Conclusao e Comparacao com o Baseline\n",
    "\n",
    "Compare o **F-0.5 Score** obtido aqui com o valor registrado em\n",
    "`notebooks/01_modelo_baseline.ipynb`.\n",
    "\n",
    "| Modelo | F-0.5 Score |\n",
    "|--------|-------------|\n",
    "| Baseline (TF-IDF + Logistic Regression) | *ver notebook 01* |\n",
    "| **Fine-Tuning BERTimbau** | *registrar aqui* |\n",
    "\n",
    "Se o BERTimbau superar o baseline, o investimento em fine-tuning esta justificado e o modelo\n",
    "pode ser integrado a API de producao (`src/api.py`).\n"
   ]
  }
 ]
}


def main():
    os.makedirs(os.path.dirname(NOTEBOOK_PATH), exist_ok=True)
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(NB, f, indent=1, ensure_ascii=False)
    print(f"Notebook gerado: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
