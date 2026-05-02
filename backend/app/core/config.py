from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    DATABASE_URL: str = ""
    TTN_CLIENT_ID: str = ""
    TTN_CLIENT_SECRET: str = ""
    TTN_SANDBOX: bool = True
    TEIF_SCHEMA_VERSION: str = "1.8.7"
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"

settings = Settings()