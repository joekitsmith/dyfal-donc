class ExerciseNotFoundError(Exception):
    pass


class SpeechUnavailableError(Exception):
    """The speech service did not give audio."""


class NotAuthenticatedError(Exception):
    """The request has no live login session."""


class ForeignOriginError(Exception):
    """A request that changes something came from an address the app is not served from."""


class PasskeyNotFoundError(Exception):
    """The user has no such passkey."""


class LastPasskeyError(Exception):
    """Removing the passkey would leave an account nobody can sign in to."""


class RecoveryCodesUnavailableError(Exception):
    """Recovery codes need a passkey first: a guest has none to recover."""


class InvalidPasskeyError(Exception):
    """The browser's passkey response is malformed or does not verify."""
