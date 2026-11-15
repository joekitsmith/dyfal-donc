from datetime import timedelta
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from persistence.database import DatabaseSettings

DEFAULT_CURRICULUM_DIRECTORY = Path(__file__).parents[2] / "curriculum"
DEFAULT_SELECTION_LIFETIME_SECONDS = 3600
DEFAULT_TTS_URL = "http://localhost:8001"
DEFAULT_TTS_TIMEOUT_SECONDS = 30.0
DEFAULT_RELYING_PARTY_ID = "localhost"
DEFAULT_RELYING_PARTY_NAME = "dyfal-donc"
DEFAULT_ORIGINS = ("http://localhost:8080", "http://localhost:3000")
DEFAULT_LOGIN_SESSION_LIFETIME_SECONDS = 24 * 3600
DEFAULT_GUEST_LOGIN_SESSION_LIFETIME_SECONDS = 30 * 24 * 3600


class PasskeySettings(BaseSettings):
    """Who the passkeys belong to, read from the ``WEBAUTHN_`` environment variables.

    ``rp_id`` is the domain passkeys are bound to, so changing it makes every
    existing passkey unusable. ``origins`` are the addresses the app is served
    from, as a comma-separated list. The defaults suit local development.
    """

    model_config = SettingsConfigDict(
        env_prefix="WEBAUTHN_", env_file=".env", extra="ignore", frozen=True
    )

    rp_id: str = DEFAULT_RELYING_PARTY_ID
    rp_name: str = DEFAULT_RELYING_PARTY_NAME
    origins: Annotated[tuple[str, ...], NoDecode, Field(min_length=1)] = DEFAULT_ORIGINS

    @field_validator("origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        return tuple(part.strip() for part in value.split(",") if part.strip())


class LoginSessionSettings(BaseSettings):
    """How long a sign-in lasts and how its cookie is sent, read from ``SESSION_``.

    A session lasts this long after it was last used. A guest's lasts longer,
    because a guest has no passkey to get back in with: losing the session
    loses the account. Browsers only send a ``Secure`` cookie over HTTPS (and
    to localhost), so ``cookie_secure`` is on unless it is turned off for plain
    HTTP.
    """

    model_config = SettingsConfigDict(
        env_prefix="SESSION_", env_file=".env", extra="ignore", frozen=True
    )

    cookie_secure: bool = True
    lifetime_seconds: int = Field(default=DEFAULT_LOGIN_SESSION_LIFETIME_SECONDS, gt=0)
    guest_lifetime_seconds: int = Field(
        default=DEFAULT_GUEST_LOGIN_SESSION_LIFETIME_SECONDS, gt=0
    )

    def lifetime_for(self, *, is_guest: bool) -> timedelta:
        seconds = self.guest_lifetime_seconds if is_guest else self.lifetime_seconds
        return timedelta(seconds=seconds)


class Settings(BaseSettings):
    """The API's settings, read from the environment.

    ``CURRICULUM_DIRECTORY`` is where the course release is loaded from, and
    ``SELECTION_LIFETIME_SECONDS`` is how long a learner has to answer an
    exercise before it expires. ``TTS_URL`` is where the speech service is.
    ``passkeys`` and ``login_session`` are read from ``WEBAUTHN_*`` and ``SESSION_*``.
    """

    model_config = SettingsConfigDict(frozen=True, env_file=".env", extra="ignore")

    curriculum_directory: Path = DEFAULT_CURRICULUM_DIRECTORY
    selection_lifetime_seconds: int = Field(
        default=DEFAULT_SELECTION_LIFETIME_SECONDS, gt=0
    )
    tts_url: str = DEFAULT_TTS_URL
    tts_timeout_seconds: float = Field(default=DEFAULT_TTS_TIMEOUT_SECONDS, gt=0)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    passkeys: PasskeySettings = Field(default_factory=PasskeySettings)
    login_session: LoginSessionSettings = Field(default_factory=LoginSessionSettings)

    @property
    def selection_lifetime(self) -> timedelta:
        return timedelta(seconds=self.selection_lifetime_seconds)
