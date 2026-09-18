from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_v1_str: str = "/api/v1"
    project_name: str = "Inimigos do Prompt API"
    model_backend: str = "bertimbau"  # "bertimbau" or "sklearn"
    hf_model_id: str = "gustant1/bertimbau-sensacionalismo"
    local_model_path: str = "models/bertimbau_sensacionalismo_final"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()

