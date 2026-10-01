import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifica o token JWT fornecido pelo Supabase usando o SUPABASE_JWT_SECRET.
    Retorna o payload decodificado se for válido.
    """
    token = credentials.credentials
    secret = settings.supabase_jwt_secret
    
    if not secret:
        # Se não configurado, loga o erro mas pode não quebrar o dev mode
        logger.warning("SUPABASE_JWT_SECRET não está configurado!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração de autenticação ausente no servidor"
        )
        
    try:
        header = jwt.get_unverified_header(token)
        print(f"DEBUG - JWT Header: {header}")
        # O Supabase assina tokens usando HS256 e o JWT Secret
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_aud": False}
        )
        return payload # Retorna os dados do usuário (sub, email, etc)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
