from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from persistence.database import DatabaseSettings

DEFAULT_CURRICULUM_DIRECTORY = Path(__file__).parents[2] / "curriculum"


class Settings(BaseSettings):
    """The API's settings, read from the environment.

    ``CURRICULUM_DIRECTORY`` is where the course release is loaded from.
    """

    model_config = SettingsConfigDict(frozen=True)

    curriculum_directory: Path = DEFAULT_CURRICULUM_DIRECTORY
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
