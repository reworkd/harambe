from functools import lru_cache

# from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env"))
    openai_api_key: str


@lru_cache()
def get_settings():
    return Settings()
