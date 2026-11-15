from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODELS_DIRECTORY = Path("/models")


class TtsSettings(BaseSettings):
    """The service's settings, read from the environment.

    ``TTS_MODELS_DIRECTORY`` is where the voice model files are.
    """

    model_config = SettingsConfigDict(env_prefix="TTS_", frozen=True)

    models_directory: Path = DEFAULT_MODELS_DIRECTORY
