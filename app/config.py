from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "SecurePulse"
    environment: str = "development"
    allowed_origins: List[str] = ["*"]
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()