import re
from bs4 import BeautifulSoup

# Léxico de alarme mapeado do docs/dados.md
EXTREME_ADJECTIVES = [
    r'\brevolucion\w*', r'\burgente\b', r'\bassustador\w*', 
    r'\bfim\b', r'\bmilagros\w*', r'\bincr[íi]vel\b', 
    r'\bchocante\b', r'\bdefinitivo\b', r'\bdestrui\w*'
]

def clean_text(raw_text: str) -> str:
    """
    Remove HTML residual, URLs, e normaliza espaços.
    """
    if not raw_text:
        return ""
        
    # Remover HTML
    soup = BeautifulSoup(raw_text, "html.parser")
    text = soup.get_text(separator=" ")
    
    # Remover URLs e emails
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Normalizar espaços
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_hype_features(text: str) -> dict:
    """
    Extrai as features estruturais de hype para o classificador baseline.
    """
    if not text:
        return {
            "uppercase_words_percentage": 0.0,
            "exclamation_density": 0.0,
            "extreme_adjectives_count": 0,
            "sentence_count": 0
        }
    
    words = text.split()
    total_words = len(words)
    if total_words == 0:
        return {
            "uppercase_words_percentage": 0.0,
            "exclamation_density": 0.0,
            "extreme_adjectives_count": 0,
            "sentence_count": 0
        }
    
    # % de palavras totalmente em UPPERCASE (com mais de 1 letra pra ignorar 'A', 'E', 'O')
    upper_words = [w for w in words if w.isupper() and len(re.sub(r'[^a-zA-Z]', '', w)) > 1]
    uppercase_words_percentage = len(upper_words) / total_words
    
    # Densidade de exclamações (! e ?!)
    exclamations = text.count('!')
    exclamation_density = exclamations / (total_words / 10.0) if total_words > 10 else 0.0
    
    # Contagem de adjetivos extremos
    text_lower = text.lower()
    extreme_count = 0
    for pattern in EXTREME_ADJECTIVES:
        extreme_count += len(re.findall(pattern, text_lower))
        
    # Contagem básica de sentenças
    sentence_count = len(re.split(r'[.!?]+', text))
    
    return {
        "uppercase_words_percentage": uppercase_words_percentage,
        "exclamation_density": exclamation_density,
        "extreme_adjectives_count": extreme_count,
        "sentence_count": sentence_count
    }
