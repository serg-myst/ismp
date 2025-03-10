from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV = Path(__file__).resolve().parent.parent


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_v1_prefix: str = "/api/ismp/v1"


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="db_")

    host: str
    port: str
    name: str
    user: str
    password: str
    echo: bool

    def db_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


settings = BaseConfig()
db_settings = DatabaseConfig()
