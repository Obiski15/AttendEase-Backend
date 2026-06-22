from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
