# Instalar dependências (necessário no Colab)
!pip install -q transformers datasets accelerate scikit-learn pandas

import os
import numpy as np
import pandas as pd
from sklearn.metrics import fbeta_score, classification_report
from transformers import (
    BertTokenizerFast,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from datasets import Dataset, DatasetDict
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Dispositivo detectado: {device}')
if device == 'cpu':
    print('[AVISO] GPU nao detectada! O fine-tuning sera muito lento. Use Colab com GPU T4.')

# Se estiver no Colab, faça o upload manual do CSV ou clone o repositório:
# !git clone https://github.com/unb-Sistemas-de-Machine-learning/challenge_1_inimigos_do_prompt.git
# %cd challenge_1_inimigos_do_prompt

TRAIN_CSV = '../data/train.csv'
TEST_CSV  = '../data/test.csv'

# Fallback: usa dataset_final_treino.csv se splits nao existirem
if not os.path.exists(TRAIN_CSV):
    from sklearn.model_selection import train_test_split
    df_all = pd.read_csv('../data/dataset_final_treino.csv')
    df_train, df_test = train_test_split(df_all, test_size=0.2, stratify=df_all['target'], random_state=42)
else:
    df_train = pd.read_csv(TRAIN_CSV)
    df_test  = pd.read_csv(TEST_CSV)

print(f'Treino: {len(df_train)} | Teste: {len(df_test)}')
print(df_train['label'].value_counts())

MODEL_NAME = 'neuralmind/bert-base-portuguese-cased'
MAX_LEN    = 256  # BERTimbau suporta até 512 tokens; 256 é suficiente para newsletters

tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch['text'],
        padding='max_length',
        truncation=True,
        max_length=MAX_LEN,
    )

# Converte DataFrames para formato HuggingFace Dataset
hf_train = Dataset.from_pandas(df_train[['text', 'target']].rename(columns={'target': 'labels'}))
hf_test  = Dataset.from_pandas(df_test[['text', 'target']].rename(columns={'target': 'labels'}))

hf_train = hf_train.map(tokenize, batched=True)
hf_test  = hf_test.map(tokenize, batched=True)

hf_train.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
hf_test.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])

print('Tokenizacao concluida!')

# Metrica customizada: F-0.5 Score (peso duplo para Precisao, minimiza Falsos Positivos)
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    f05  = fbeta_score(labels, predictions, beta=0.5, pos_label=1, average='binary')
    f1   = fbeta_score(labels, predictions, beta=1.0, pos_label=1, average='binary')
    prec = fbeta_score(labels, predictions, beta=0.01, pos_label=1, average='binary')  # ~precisao pura
    return {
        'f0_5_score': f05,
        'f1_score':   f1,
        'precision':  prec,
    }

model = BertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    id2label={0: 'sobrio', 1: 'sensacionalista'},
    label2id={'sobrio': 0, 'sensacionalista': 1},
)

training_args = TrainingArguments(
    output_dir='../models/bertimbau_sensacionalismo',
    eval_strategy='epoch',
    save_strategy='epoch',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model='f0_5_score',
    greater_is_better=True,
    logging_steps=50,
    fp16=(device == 'cuda'),  # Mixed precision somente com GPU
    report_to='none',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=hf_train,
    eval_dataset=hf_test,
    compute_metrics=compute_metrics,
)

print('Modelo e Trainer configurados!')

print('Iniciando fine-tuning do BERTimbau...')
trainer.train()
print('Fine-tuning concluido!')

results = trainer.evaluate()
print('\nResultados finais no conjunto de teste:')
for k, v in results.items():
    print(f'  {k}: {v:.4f}')

# Classificação detalhada
preds = trainer.predict(hf_test)
y_pred = np.argmax(preds.predictions, axis=-1)
y_true = preds.label_ids
print('\nRelatório de Classificação completo:')
print(classification_report(y_true, y_pred, target_names=['Sobrio', 'Sensacionalista']))

save_path = '../models/bertimbau_sensacionalismo_final'
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)
print(f'Modelo salvo em: {save_path}')
print('Para usar a API, aponte MODEL_PATH para este diretorio.')
