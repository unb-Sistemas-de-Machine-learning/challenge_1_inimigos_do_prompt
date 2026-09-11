import os
import numpy as np
import pandas as pd
from sklearn.metrics import fbeta_score, classification_report
from transformers import BertTokenizerFast, BertForSequenceClassification
from datasets import Dataset
import torch
import torch_directml
from torch.utils.data import DataLoader
from tqdm import tqdm

def main():
    device = torch_directml.device(0)
    print(f'Dispositivo detectado (DirectML): {device}')
    print("Nome:", torch_directml.device_name(0))

    TRAIN_CSV = 'data/train.csv'
    TEST_CSV  = 'data/test.csv'

    if not os.path.exists(TRAIN_CSV):
        from sklearn.model_selection import train_test_split
        df_all = pd.read_csv('data/dataset_final_treino.csv')
        df_train, df_test = train_test_split(df_all, test_size=0.2, stratify=df_all['target'], random_state=42)
    else:
        df_train = pd.read_csv(TRAIN_CSV)
        df_test  = pd.read_csv(TEST_CSV)

    print(f'Treino: {len(df_train)} | Teste: {len(df_test)}')

    MODEL_NAME = 'neuralmind/bert-base-portuguese-cased'
    MAX_LEN    = 256
    BATCH_SIZE = 8
    EPOCHS     = 3
    LR         = 2e-5

    tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(
            batch['text'],
            padding='max_length',
            truncation=True,
            max_length=MAX_LEN,
        )

    hf_train = Dataset.from_pandas(df_train[['text', 'target']].rename(columns={'target': 'labels'}))
    hf_test  = Dataset.from_pandas(df_test[['text', 'target']].rename(columns={'target': 'labels'}))

    hf_train = hf_train.map(tokenize, batched=True)
    hf_test  = hf_test.map(tokenize, batched=True)

    hf_train.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
    hf_test.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])

    train_loader = DataLoader(hf_train, batch_size=BATCH_SIZE, shuffle=True)
    test_loader  = DataLoader(hf_test, batch_size=BATCH_SIZE*2)

    model = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        id2label={0: 'sobrio', 1: 'sensacionalista'},
        label2id={'sobrio': 0, 'sensacionalista': 1},
    )
    model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)

    print('Iniciando fine-tuning do BERTimbau no DirectML (Custom Loop)...')
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        progress_bar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{EPOCHS}')
        for batch in progress_bar:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        print(f'Epoch {epoch+1} Loss: {total_loss/len(train_loader):.4f}')
        
        model.eval()
        all_preds = []
        all_labels = []
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=-1)
                
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        f05 = fbeta_score(all_labels, all_preds, beta=0.5, pos_label=1, average='binary')
        print(f'Eval F0.5 Score: {f05:.4f}')

    print('\nRelatório de Classificação Final:')
    print(classification_report(all_labels, all_preds, target_names=['Sobrio', 'Sensacionalista']))

    save_path = 'models/bertimbau_sensacionalismo_final'
    model.cpu().save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f'Modelo salvo em: {save_path}')

if __name__ == '__main__':
    main()
