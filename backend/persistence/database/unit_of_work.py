from sqlalchemy.orm import Session

from persistence.database.repositories import (
    ChallengeRepository,
    CredentialRepository,
    EventRepository,
    LearnerRepository,
    LoginSessionRepository,
    SelectionRepository,
    UserRepository,
)


class UnitOfWork:
    """The repositories for one transaction, which only ``commit`` makes permanent.

    The session belongs to the caller, who closes it. Anything not committed is
    rolled back when it is closed.
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self.users = UserRepository(session)
        self.credentials = CredentialRepository(session)
        self.login_sessions = LoginSessionRepository(session)
        self.challenges = ChallengeRepository(session)
        self.learners = LearnerRepository(session)
        self.selections = SelectionRepository(session)
        self.events = EventRepository(session)

    def commit(self) -> None:
        self._session.commit()
