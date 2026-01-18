from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/hcp_crm"
    groq_api_key: str = ""
    groq_model: str = "gemma2-9b-it"
    secondary_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
