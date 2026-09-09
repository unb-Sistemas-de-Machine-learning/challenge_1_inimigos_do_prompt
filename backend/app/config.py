from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_v1_str: str = "/api/v1"
    project_name: str = "Inimigos do Prompt API"
    model_backend: str = "sklearn" # or "bertimbau"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
