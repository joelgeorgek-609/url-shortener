from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    KEYCLOAK_ISSUER: str
    KEYCLOAK_CLIENT_ID: str
    SERVICE_BASE_URL: str
    DISABLE_AUDIENCE_CHECK: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()