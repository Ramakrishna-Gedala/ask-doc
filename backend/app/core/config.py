# Configuration and environment variables
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API
    API_TITLE: str = "Ask-Doc API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/askdoc"
    )

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AWS/Bedrock
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "ask-doc-files")

    # Bedrock Models
    BEDROCK_EMBEDDING_MODEL: str = "amazon.titan-embed-text-v1"
    BEDROCK_LLM_MODEL: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_FILES_PER_USER: int = 20
    ALLOWED_FILE_TYPES: str = "pdf,csv,docx"

    @property
    def allowed_file_types_list(self) -> list:
        """Parse comma-separated file types to list"""
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]

    # RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K_CHUNKS: int = 5

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> list:
        """Parse comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
