import os
import json
import pandas as pd

def main():
    # Caminhos relativos à raiz do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    log_file = os.path.join(project_root, "backend", "feedback_log.jsonl")
    output_dir = os.path.join(project_root, "data")
    output_file = os.path.join(output_dir, "feedback_dataset.csv")
    
    if not os.path.exists(log_file):
        print(f"Arquivo não encontrado: {log_file}")
        return

    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
                
            if record.get("feedback_type") == "false_positive":
                text = record.get("original_text")
                if not text:
                    text = record.get("comment")
                    
                if text and text.strip():
                    records.append({
                        "text": text.strip(),
                        "label": 0,
                        "source": "user_feedback"
                    })

    if not records:
        print("Nenhum registro válido de false_positive encontrado.")
        return

    df_new = pd.DataFrame(records)
    
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(output_file):
        df_existing = pd.read_csv(output_file)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    # Remove textos duplicados
    df_combined.drop_duplicates(subset=["text"], keep="last", inplace=True)
    
    df_combined.to_csv(output_file, index=False)
    print(f"Processado(s) {len(df_new)} novo(s) registro(s). Salvo em {output_file}")

if __name__ == "__main__":
    main()
