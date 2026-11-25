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
    kafka_enabled: bool = True
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_raw: str = "agri.docs.raw"
    kafka_topic_chunked: str = "agri.docs.chunked"
    kafka_topic_dlq: str = "agri.docs.dlq"
    pinecone_api_key: str
    pinecone_index: str = "agri-rag-e5"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    retrieval_k: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
