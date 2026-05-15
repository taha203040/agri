from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    db_uri: str = "postgresql://postgres:0000@localhost:5432/myagri"
    model_name: str = "deepseek-chat"
    default_thread_id: str = "default"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"   


settings = Settings()