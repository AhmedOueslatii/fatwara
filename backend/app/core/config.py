from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:localdevpassword@db:5432/fatwara"

    JWT_SECRET: str = "dev-only-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7

    TTN_SANDBOX: bool = True
    TTN_BASE_URL: str = ""
    TTN_CLIENT_ID: str = ""
    TTN_CLIENT_SECRET: str = ""
    TTN_MOCK_MODE: str = "accept"  # accept | reject | timeout | random

    TEIF_SCHEMA_VERSION: str = "1.8.7"
    TEIF_STRICT_VALIDATION: bool = False

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_CERTS: str = "certs"
    MINIO_SECURE: bool = False

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
