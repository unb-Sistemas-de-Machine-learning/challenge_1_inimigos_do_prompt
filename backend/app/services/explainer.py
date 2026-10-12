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
    Lista os sinais linguísticos de sensacionalismo encontrados no texto.

    Só retorna sinais que também alimentam o `heuristic_boost` do classificador
    (adjetivos extremos e palavras em CAPS). Os pesos são apenas níveis de
    intensidade qualitativos (não são contribuições medidas, como SHAP).
    Números/percentuais NÃO são sinais de sensacionalismo e ficam de fora.
    """
    terms = []
    text_lower = text.lower()

    # 1. Adjetivos extremos (léxico de alarme)
    for pattern in EXTREME_ADJECTIVES:
        matches = set(re.findall(pattern, text_lower))
        for match in matches:
            if len(match) > 3:  # Filtra matches muito curtos
                terms.append(HighlightedTerm(
                    term=match.capitalize(),
                    weight=0.6,
                    category="alarmist"
                ))

    # 2. Palavras em CAPS
    words = text.split()
    upper_words = [w for w in words if w.isupper() and len(re.sub(r'[^a-zA-Z]', '', w)) > 3]
    for w in set(upper_words):
        terms.append(HighlightedTerm(
            term=w,
            weight=0.4,
            category="hype"
        ))

    # Remove duplicados e ordena por peso decrescente, limitado a 8
    unique_terms = {t.term.lower(): t for t in terms}.values()
    sorted_terms = sorted(unique_terms, key=lambda x: x.weight, reverse=True)

    return sorted_terms[:8]

def extract_suspicious_claims(text: str, score: float, highlighted_terms: List[HighlightedTerm] = None) -> List[SuspiciousClaim]:
    """
    Extrai trechos com linguagem enfática (adjetivos extremos, CAPS, exclamações).

    Não avalia veracidade: apenas indica onde o tom do texto é mais sensacionalista.
    O campo `severity` é mantido por compatibilidade com a API, mas a extensão
    não o exibe.
    """
    claims = []

    try:
        sentences = sent_tokenize(text)
    except Exception:
        # Fallback simples caso nltk falhe
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    for sent in sentences:
        sent_lower = sent.lower()
        reasons = []

        adjectives = [m.group(0) for p in EXTREME_ADJECTIVES for m in [re.search(p, sent_lower)] if m]
        if adjectives:
            reasons.append("adjetivos extremos: " + ", ".join(f"'{a}'" for a in adjectives))

        caps = [w for w in sent.split() if w.isupper() and len(re.sub(r'[^a-zA-Z]', '', w)) > 3]
        if caps:
            reasons.append("palavras em CAPS: " + ", ".join(f"'{w}'" for w in caps[:3]))

        if sent.count('!') >= 1:
            reasons.append("exclamação")

        if not reasons:
            continue

        claims.append(SuspiciousClaim(
            claim=sent[:150] + ("..." if len(sent) > 150 else ""),
            explanation="Linguagem enfática (" + "; ".join(reasons) + ").",
            severity="high" if len(reasons) >= 2 else "moderate"
        ))

    # Prioriza trechos com mais sinais e limita a 5
    claims.sort(key=lambda c: c.severity != "high")
    return claims[:5]
