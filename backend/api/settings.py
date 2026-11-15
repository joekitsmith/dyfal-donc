from datetime import timedelta
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from persistence.database import DatabaseSettings

DEFAULT_CURRICULUM_DIRECTORY = Path(__file__).parents[2] / "curriculum"
DEFAULT_SELECTION_LIFETIME_SECONDS = 3600
DEFAULT_TTS_URL = "http://localhost:8001"
DEFAULT_TTS_TIMEOUT_SECONDS = 30.0


class Settings(BaseSettings):
    """The API's settings, read from the environment.

    ``CURRICULUM_DIRECTORY`` is where the course release is loaded from, and
    ``SELECTION_LIFETIME_SECONDS`` is how long a learner has to answer an
    exercise before it expires. ``TTS_URL`` is where the speech service is.
    """

    model_config = SettingsConfigDict(frozen=True, env_file=".env", extra="ignore")

    curriculum_directory: Path = DEFAULT_CURRICULUM_DIRECTORY
    selection_lifetime_seconds: int = Field(
        default=DEFAULT_SELECTION_LIFETIME_SECONDS, gt=0
    )
    tts_url: str = DEFAULT_TTS_URL
    tts_timeout_seconds: float = Field(default=DEFAULT_TTS_TIMEOUT_SECONDS, gt=0)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    @property
    def selection_lifetime(self) -> timedelta:
        return timedelta(seconds=self.selection_lifetime_seconds)
