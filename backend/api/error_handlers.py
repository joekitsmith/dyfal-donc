from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from api.errors import (
    ExerciseNotFoundError,
    ForeignOriginError,
    InvalidPasskeyError,
    LearningSessionNotFoundError,
    LastPasskeyError,
    NotAuthenticatedError,
    PasskeyNotFoundError,
    RecentSignInRequiredError,
    RecoveryCodesUnavailableError,
    SpeechUnavailableError,
)
from persistence.database.errors import (
    ChallengeNotFoundError,
    CredentialAlreadyRegisteredError,
    RecoveryCodeNotFoundError,
    EventOutOfOrderError,
    LearnerNotFoundError,
    SelectionAlreadyAnsweredError,
    SelectionExpiredError,
    SelectionNotFoundError,
)

type ErrorHandler = Callable[[Request, Exception], Awaitable[JSONResponse]]

STATUS_FOR_ERROR: dict[type[Exception], int] = {
    ExerciseNotFoundError: status.HTTP_404_NOT_FOUND,
    LearningSessionNotFoundError: status.HTTP_404_NOT_FOUND,
    SpeechUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    LearnerNotFoundError: status.HTTP_404_NOT_FOUND,
    SelectionNotFoundError: status.HTTP_404_NOT_FOUND,
    SelectionExpiredError: status.HTTP_410_GONE,
    SelectionAlreadyAnsweredError: status.HTTP_409_CONFLICT,
    EventOutOfOrderError: status.HTTP_409_CONFLICT,
    NotAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
    ForeignOriginError: status.HTTP_403_FORBIDDEN,
    InvalidPasskeyError: status.HTTP_400_BAD_REQUEST,
    ChallengeNotFoundError: status.HTTP_400_BAD_REQUEST,
    CredentialAlreadyRegisteredError: status.HTTP_409_CONFLICT,
    PasskeyNotFoundError: status.HTTP_404_NOT_FOUND,
    LastPasskeyError: status.HTTP_409_CONFLICT,
    RecoveryCodeNotFoundError: status.HTTP_400_BAD_REQUEST,
    RecoveryCodesUnavailableError: status.HTTP_409_CONFLICT,
    RecentSignInRequiredError: status.HTTP_403_FORBIDDEN,
}


def register_error_handlers(app: FastAPI) -> None:
    """Turn the errors the controllers let through into responses."""
    for error_type, status_code in STATUS_FOR_ERROR.items():
        app.add_exception_handler(error_type, _handler_for(status_code))


def _handler_for(status_code: int) -> ErrorHandler:
    async def handle(_request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(error)})

    return handle
