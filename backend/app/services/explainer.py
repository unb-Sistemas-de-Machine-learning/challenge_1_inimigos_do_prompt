import re
from typing import List
from nltk.tokenize import sent_tokenize
import nltk

from app.schemas.analyze import HighlightedTerm, SuspiciousClaim
from app.services.preprocessor import EXTREME_ADJECTIVES

# Garante download do punkt (necessário pro sent_tokenize)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    import threading
    threading.Thread(target=lambda: nltk.download('punkt_tab')).start()

def generate_highlighted_terms(text: str) -> List[HighlightedTerm]:
    """
    Identifica termos problemáticos no texto e atribui pesos/categorias.
    No MVP sem SHAP integrado, usamos heurísticas baseadas em léxico.
    """
    terms = []
    text_lower = text.lower()
    
    # 1. Procurar por adjetivos extremos (Lexicon de alarme)
    for pattern in EXTREME_ADJECTIVES:
        matches = set(re.findall(pattern, text_lower))
        for match in matches:
            if len(match) > 3: # Filtra matches muito curtos
                terms.append(HighlightedTerm(
                    term=match.capitalize(),
                    weight=0.6,
                    category="alarmist"
                ))

    # 2. Procurar palavras em CAPS (Hype)
    words = text.split()
    upper_words = [w for w in words if w.isupper() and len(re.sub(r'[^a-zA-Z]', '', w)) > 3]
    for w in set(upper_words):
        terms.append(HighlightedTerm(
            term=w,
            weight=0.4,
            category="hype"
        ))
        
    # 3. Estruturas de clickbait ("X%", "milhões", "substituir")
    clickbait_patterns = [r'\d{1,3}%', r'\bmilh[õo]es\b', r'\bsubstitui\w*']
    for pattern in clickbait_patterns:
        matches = set(re.findall(pattern, text_lower))
        for match in matches:
            terms.append(HighlightedTerm(
                term=match,
                weight=0.7,
                category="clickbait"
            ))

    # Remove duplicados e ordena por peso decrescente, limitado a 8
    unique_terms = {t.term.lower(): t for t in terms}.values()
    sorted_terms = sorted(unique_terms, key=lambda x: x.weight, reverse=True)
    
    return sorted_terms[:8]

def extract_suspicious_claims(text: str, score: float) -> List[SuspiciousClaim]:
    """
    Segmenta o texto e extrai sentenças que configuram claims suspeitas.
    """
    claims = []
    
    try:
        sentences = sent_tokenize(text)
    except Exception:
        # Fallback simples caso nltk falhe
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

    for sent in sentences:
        sent_lower = sent.lower()
        
        # Heurística 1: Percentuais extremos + promessas/ameaças
        if re.search(r'\d{2,3}%', sent_lower) and ('substituir' in sent_lower or 'garantido' in sent_lower or 'lucro' in sent_lower):
            claims.append(SuspiciousClaim(
                claim=sent[:150] + ("..." if len(sent) > 150 else ""),
                explanation="Hype exagerado, uso de percentuais absolutos sem contexto verificado.",
                severity="moderate"
            ))
            continue
            
        # Heurística 2: Afirmações não científicas sobre IA/Quântica
        if ('quântic' in sent_lower or 'consciência' in sent_lower) and ('agora' in sent_lower or 'alcançou' in sent_lower):
            claims.append(SuspiciousClaim(
                claim=sent[:150] + ("..." if len(sent) > 150 else ""),
                explanation="Possível desinformação conceitual. Atribuição de capacidades comerciais não comprovadas a tecnologias experimentais.",
                severity="high"
            ))
            continue
            
        # Heurística 3: Adjetivos extremos acumulados
        extreme_count = sum(1 for p in EXTREME_ADJECTIVES if re.search(p, sent_lower))
        if extreme_count >= 2:
            claims.append(SuspiciousClaim(
                claim=sent[:150] + ("..." if len(sent) > 150 else ""),
                explanation="Excesso de gatilhos emocionais e linguagem alarmista.",
                severity="moderate"
            ))

    # Limita a 5 claims
    return claims[:5]
