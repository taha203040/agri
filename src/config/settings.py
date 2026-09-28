from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_uri: str
    model_name: str
    deepseek_api_key: str

    default_thread_id: str = "default"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

