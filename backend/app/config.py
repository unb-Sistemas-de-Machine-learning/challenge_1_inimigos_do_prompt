from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_v1_str: str = "/api/v1"
    project_name: str = "Inimigos do Prompt API"
    model_backend: str = "bertimbau"  # "bertimbau", "sklearn", or "huggingface_api"
    hf_model_id: str = "gustant1/bertimbau-sensacionalismo"
    local_model_path: str = "models/bertimbau_sensacionalismo_final"
    huggingface_api_token: Optional[str] = None
    huggingface_api_url: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()

