from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # JWT / Auth
    # NOTE: override SECRET_KEY in production via the .env file.
    SECRET_KEY: str = "CHANGE_ME_super_secret_dev_key_do_not_use_in_prod"
    ALGORITHM: str = "HS256"
    # Short-lived access token: sent on every request.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Long-lived refresh token: used to silently obtain a new access token,
    # so the user stays logged in without re-entering credentials.
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
