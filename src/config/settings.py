from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_uri: str
    model_name: str
    deepseek_api_key: str
    langsmith_api_key: str
    langsmith_tracing: bool = True
    langsmith_project: str = "Myagriclt"
    default_thread_id: str = "default"
    log_level: str = "INFO"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    upload_dir: str = "data/uploads"
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
