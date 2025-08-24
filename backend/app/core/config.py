from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    env: str = Field(default="dev", alias="ENV")
    app_name: str = Field(default="ttq-platform", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")
    log_file: str = Field(default="logs/app.log", alias="LOG_FILE")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8080, alias="PORT")

    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ttq_dev", alias="POSTGRES_DB")
    postgres_user: str = Field(default="ttq", alias="POSTGRES_USER")
    postgres_password: str = Field(default="ttq", alias="POSTGRES_PASSWORD")

    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    secret_key: str = Field(default="changeme-in-dev", alias="SECRET_KEY")

    class Config:
        extra = "ignore"
        env_file = ".env"

settings = Settings()