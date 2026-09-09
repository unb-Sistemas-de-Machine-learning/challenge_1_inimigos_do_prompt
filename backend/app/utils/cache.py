import hashlib
from cachetools import TTLCache

# Cache para armazenar as últimas análises. 
# TTL de 1 hora (3600 segundos), no máximo 500 itens.
analysis_cache = TTLCache(maxsize=500, ttl=3600)

def generate_cache_key(text: str) -> str:
    """
    Gera uma chave única baseada nos primeiros 200 caracteres do texto 
    para identificar newsletters idênticas rapidamente.
    """
    prefix = text[:200].encode('utf-8')
    return hashlib.sha256(prefix).hexdigest()
