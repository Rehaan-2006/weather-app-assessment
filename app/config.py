from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This automatically matches variables inside your .env file
    DATABASE_URL: str
    YOUTUBE_API_KEY: str = ""
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Instructs pydantic to look for a physical file named .env in the root
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Instantiate the settings object to make it importable
settings = Settings()