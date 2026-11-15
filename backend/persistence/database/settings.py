from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Where the database is, read from ``DATABASE_URL`` or the ``.env`` file."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_", env_file=".env", extra="ignore", frozen=True
    )

    url: str
