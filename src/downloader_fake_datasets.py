import os
import zipfile
import requests
import pandas as pd
from tqdm import tqdm

def download_file(url, dest_path):
    print(f"Iniciando download de: {url}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    with open(dest_path, 'wb') as file, tqdm(
        desc=os.path.basename(dest_path),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    print("Download concluído!")

def extract_zip(zip_path, extract_to):
    print(f"Extraindo {zip_path} para {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extração concluída!")

def parse_metadata_file(filepath):
    """
    Lê o arquivo de meta-informação e retorna um dicionário com os campos mapeados.
    Baseado na estrutura do Fake.br-Corpus.
    """
    if not os.path.exists(filepath):
        return {}
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip() for line in f.readlines()]
    
    # Mapeamento padrão dos metadados do Fake.br
    metadata = {}
    
    # Atributos básicos (Linhas 1 a 4)
    if len(lines) >= 1: metadata['author'] = lines[0]
    if len(lines) >= 2: metadata['link'] = lines[1]
    if len(lines) >= 3: metadata['category'] = lines[2]
    if len(lines) >= 4: metadata['date_of_publication'] = lines[3]
    
    # Atributos numéricos/estatísticos (Linhas 5 a 27)
    fields = [
        ('tokens_count', 4),
        ('words_without_punctuation', 5),
        ('types_count', 6),
        ('characters_count', 7),
        ('avg_sentence_length', 8),
        ('avg_word_length', 9),
        ('verbs_count', 10),
        ('subjunctive_verbs_count', 11),
        ('imperative_verbs_count', 12),
        ('nouns_count', 13),
        ('adjectives_count', 14),
        ('adverbs_count', 15),
        ('modal_verbs_count', 16),
        ('singular_first_pronouns_count', 17),
        ('plural_first_pronouns_count', 18),
        ('pronouns_count', 19),
        ('second_personal_pronouns_count', 20),
        ('spelling_errors_percentage', 21),
        ('emotiveness', 22),
        ('diversity', 23),
        ('links_count', 24),
        ('uppercase_words_count', 25),
        ('pausality', 26)
    ]
    
    for name, idx in fields:
        if len(lines) > idx:
            val = lines[idx]
            try:
                # Tenta converter para float ou int, se possível
                if '.' in val or ',' in val:
                    val = float(val.replace(',', '.'))
                else:
                    val = int(val)
            except ValueError:
                pass
            metadata[name] = val
            
    return metadata

def process_corpus(base_dir):
    print("Processando textos e metadados do Corpus...")
    full_texts_dir = os.path.join(base_dir, "full_texts")
    
    # Listar arquivos nas pastas fake e true
    fake_texts_dir = os.path.join(full_texts_dir, "fake")
    true_texts_dir = os.path.join(full_texts_dir, "true")
    
    fake_meta_dir = os.path.join(full_texts_dir, "fake-meta-information")
    true_meta_dir = os.path.join(full_texts_dir, "true-meta-information")
    
    data = []
    
    # Processar Fake News
    if os.path.exists(fake_texts_dir):
        fake_files = [f for f in os.listdir(fake_texts_dir) if f.endswith('.txt')]
        print(f"Encontrados {len(fake_files)} arquivos de Fake News.")
        for f in tqdm(fake_files, desc="Processando Fake News"):
            file_num = f.split('.')[0]
            text_path = os.path.join(fake_texts_dir, f)
            meta_path = os.path.join(fake_meta_dir, f"{file_num}-meta.txt")
            
            # Se não achar com -meta.txt, tenta sem
            if not os.path.exists(meta_path):
                meta_path = os.path.join(fake_meta_dir, f)
                
            # Ler texto
            with open(text_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                text_content = file_obj.read().strip()
                
            # Ler metadados
            meta_dict = parse_metadata_file(meta_path)
            
            # Adicionar dados compilados
            row = {
                'id': f"fake_{file_num}",
                'label': 'fake',
                'text': text_content,
                **meta_dict
            }
            data.append(row)
            
    # Processar True News
    if os.path.exists(true_texts_dir):
        true_files = [f for f in os.listdir(true_texts_dir) if f.endswith('.txt')]
        print(f"Encontrados {len(true_files)} arquivos de True News.")
        for f in tqdm(true_files, desc="Processando True News"):
            file_num = f.split('.')[0]
            text_path = os.path.join(true_texts_dir, f)
            meta_path = os.path.join(true_meta_dir, f"{file_num}-meta.txt")
            
            # Se não achar com -meta.txt, tenta sem
            if not os.path.exists(meta_path):
                meta_path = os.path.join(true_meta_dir, f)
                
            # Ler texto
            with open(text_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                text_content = file_obj.read().strip()
                
            # Ler metadados
            meta_dict = parse_metadata_file(meta_path)
            
            # Adicionar dados compilados
            row = {
                'id': f"true_{file_num}",
                'label': 'true',
                'text': text_content,
                **meta_dict
            }
            data.append(row)
            
    df = pd.DataFrame(data)
    return df

def main():
    zip_url = "https://github.com/roneysco/Fake.br-Corpus/archive/refs/heads/master.zip"
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    zip_path = os.path.join(data_dir, "Fake.br-Corpus.zip")
    extracted_dir = os.path.join(data_dir, "Fake.br-Corpus-extracted")
    
    # 1. Download
    if not os.path.exists(zip_path):
        download_file(zip_url, zip_path)
    else:
        print("Arquivo zip já existe, pulando download.")
        
    # 2. Extract
    if not os.path.exists(extracted_dir):
        extract_zip(zip_path, extracted_dir)
    else:
        print("Pasta extraída já existe, pulando extração.")
        
    # 3. Process
    corpus_base = os.path.join(extracted_dir, "Fake.br-Corpus-master")
    df = process_corpus(corpus_base)
    
    # 4. Save to CSV
    output_csv = os.path.join(data_dir, "fake_br_corpus.csv")
    print(f"Salvando dataset consolidado em: {output_csv}")
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Processamento completo! Total de registros: {len(df)}")

if __name__ == "__main__":
    main()
