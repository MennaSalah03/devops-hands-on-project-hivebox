from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    "configs"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_url: str = "https://api.opensensemap.org/boxes/data"


config = Settings()