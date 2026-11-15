class DatabaseError(Exception):
    """Base class for the errors the repositories raise."""


class LearnerNotFoundError(DatabaseError):
    pass


class SelectionNotFoundError(DatabaseError):
    """The selection does not exist, or was not issued to this learner."""


class SelectionExpiredError(DatabaseError):
    pass


class SelectionAlreadyAnsweredError(DatabaseError):
    pass


class EventOutOfOrderError(DatabaseError):
    """The event is earlier than one already recorded for the learner."""


class CredentialAlreadyRegisteredError(DatabaseError):
    """The authenticator's credential id is already stored."""


class ChallengeNotFoundError(DatabaseError):
    """The challenge was never issued, was already used, or has expired."""


class RecoveryCodeNotFoundError(DatabaseError):
    """The recovery code was never issued or has been used."""


class ProblemReportNotFoundError(DatabaseError):
    pass
