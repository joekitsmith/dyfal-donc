import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from persistence.database import (
    AddChallenge,
    AddCredential,
    AddLearner,
    AddLoginSession,
    AddUser,
    ChallengeRepository,
    CredentialRepository,
    ExtendLoginSession,
    LearnerRepository,
    LoginSessionRepository,
    RecordCredentialUse,
    UserRecord,
    UserRepository,
)
from persistence.database.errors import (
    ChallengeNotFoundError,
    CredentialAlreadyRegisteredError,
)
from persistence.database.models import Base

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)
LIFETIME = timedelta(minutes=5)


def add_user(session: Session) -> UserRecord:
    return UserRepository(session).add(AddUser())


def new_credential(user_id: uuid.UUID, credential_id: bytes = b"id-1") -> AddCredential:
    return AddCredential(
        user_id=user_id,
        credential_id=credential_id,
        public_key=b"key",
        sign_count=0,
        transports=("internal", "hybrid"),
        label="Passkey",
        created_at=NOW,
    )


def new_login_session(
    user_id: uuid.UUID, token_hash: bytes = b"hash-1"
) -> AddLoginSession:
    return AddLoginSession(
        user_id=user_id,
        token_hash=token_hash,
        created_at=NOW,
        expires_at=NOW + timedelta(days=30),
    )


def new_challenge(
    challenge: bytes = b"c-1", purpose: str = "registration"
) -> AddChallenge:
    return AddChallenge(
        challenge=challenge,
        purpose=purpose,
        user_id=None,
        created_at=NOW,
        expires_at=NOW + LIFETIME,
    )


class TestUserRepository:
    def test_a_new_user_is_a_guest(self, session: Session) -> None:
        added = add_user(session)

        found = UserRepository(session).get(added.id)

        assert found == added
        assert found is not None
        assert found.is_guest

    def test_a_user_with_a_passkey_is_not_a_guest(self, session: Session) -> None:
        user = add_user(session)
        CredentialRepository(session).add(new_credential(user.id))

        found = UserRepository(session).get(user.id)

        assert found is not None
        assert not found.is_guest

    def test_an_unknown_user_is_not_found(self, session: Session) -> None:
        assert UserRepository(session).get(uuid.uuid4()) is None

    def test_deleting_a_user_reports_whether_there_was_one(
        self, session: Session
    ) -> None:
        user = add_user(session)

        assert UserRepository(session).delete(user.id)
        assert not UserRepository(session).delete(user.id)

    def test_a_user_has_one_learner(self, session: Session) -> None:
        user = add_user(session)
        LearnerRepository(session).add(AddLearner(user_id=user.id, course_release="r"))

        with pytest.raises(IntegrityError):
            LearnerRepository(session).add(
                AddLearner(user_id=user.id, course_release="r")
            )


class TestDeletingAUser:
    def test_removes_everything_that_belongs_to_them(self, session: Session) -> None:
        user = add_user(session)
        learner = LearnerRepository(session).add(
            AddLearner(user_id=user.id, course_release="r")
        )
        CredentialRepository(session).add(new_credential(user.id))
        LoginSessionRepository(session).add(new_login_session(user.id))
        ChallengeRepository(session).add(
            AddChallenge(
                challenge=b"c",
                purpose="registration",
                user_id=user.id,
                created_at=NOW,
                expires_at=NOW + LIFETIME,
            )
        )
        assert LearnerRepository(session).get(learner.id) is not None

        UserRepository(session).delete(user.id)

        counts = {
            name: session.scalar(select(func.count()).select_from(table))
            for name, table in Base.metadata.tables.items()
        }
        assert counts == dict.fromkeys(Base.metadata.tables, 0)


class TestCredentialRepository:
    def test_a_passkey_is_stored_and_found_by_its_credential_id(
        self, session: Session
    ) -> None:
        user = add_user(session)
        repository = CredentialRepository(session)

        added = repository.add(new_credential(user.id))

        found = repository.by_credential_id(b"id-1")
        assert found == added
        assert found is not None
        assert found.transports == ("internal", "hybrid")
        assert found.last_used_at is None

    def test_the_same_credential_cannot_be_added_twice(self, session: Session) -> None:
        first, second = add_user(session), add_user(session)
        repository = CredentialRepository(session)
        repository.add(new_credential(first.id))

        with pytest.raises(CredentialAlreadyRegisteredError):
            repository.add(new_credential(second.id))

    def test_a_users_passkeys_are_listed_oldest_first(self, session: Session) -> None:
        user = add_user(session)
        repository = CredentialRepository(session)
        later = new_credential(user.id, b"later")
        repository.add(replace(later, created_at=NOW + LIFETIME))
        repository.add(new_credential(user.id, b"earlier"))

        listed = repository.for_user(user.id)

        assert [credential.credential_id for credential in listed] == [
            b"earlier",
            b"later",
        ]

    def test_using_a_passkey_records_the_count_and_time(self, session: Session) -> None:
        user = add_user(session)
        repository = CredentialRepository(session)
        repository.add(new_credential(user.id))

        repository.record_use(
            RecordCredentialUse(credential_id=b"id-1", sign_count=7, used_at=NOW)
        )

        found = repository.by_credential_id(b"id-1")
        assert found is not None
        assert (found.sign_count, found.last_used_at) == (7, NOW)

    def test_a_user_can_only_delete_their_own_passkey(self, session: Session) -> None:
        owner, other = add_user(session), add_user(session)
        repository = CredentialRepository(session)
        passkey = repository.add(new_credential(owner.id))

        assert not repository.delete(other.id, passkey.id)
        assert repository.delete(owner.id, passkey.id)
        assert repository.for_user(owner.id) == ()


class TestLoginSessionRepository:
    def test_a_session_is_found_by_its_token_hash(self, session: Session) -> None:
        user = add_user(session)
        repository = LoginSessionRepository(session)

        added = repository.add(new_login_session(user.id))

        assert repository.by_token_hash(b"hash-1") == added
        assert repository.by_token_hash(b"other") is None

    def test_extending_a_session_moves_its_expiry(self, session: Session) -> None:
        user = add_user(session)
        repository = LoginSessionRepository(session)
        added = repository.add(new_login_session(user.id))
        later = NOW + timedelta(days=1)

        repository.extend(
            ExtendLoginSession(
                login_session_id=added.id,
                seen_at=later,
                expires_at=later + timedelta(days=30),
            )
        )

        found = repository.by_token_hash(b"hash-1")
        assert found is not None
        assert found.last_seen_at == later
        assert found.expires_at == later + timedelta(days=30)

    def test_deleting_a_session_signs_that_browser_out(self, session: Session) -> None:
        user = add_user(session)
        repository = LoginSessionRepository(session)
        added = repository.add(new_login_session(user.id))

        repository.delete(added.id)

        assert repository.by_token_hash(b"hash-1") is None

    def test_expired_sessions_are_deleted_and_counted(self, session: Session) -> None:
        user = add_user(session)
        repository = LoginSessionRepository(session)
        repository.add(new_login_session(user.id, b"old"))
        repository.add(
            AddLoginSession(
                user_id=user.id,
                token_hash=b"new",
                created_at=NOW,
                expires_at=NOW + timedelta(days=90),
            )
        )

        deleted = repository.delete_expired(NOW + timedelta(days=31))

        assert deleted == 1
        assert repository.by_token_hash(b"old") is None
        assert repository.by_token_hash(b"new") is not None


class TestChallengeRepository:
    def test_a_challenge_can_be_used_once(self, session: Session) -> None:
        repository = ChallengeRepository(session)
        repository.add(new_challenge())

        used = repository.consume(b"c-1", "registration", NOW)

        assert used.challenge == b"c-1"
        with pytest.raises(ChallengeNotFoundError):
            repository.consume(b"c-1", "registration", NOW)

    def test_a_challenge_cannot_be_used_for_another_purpose(
        self, session: Session
    ) -> None:
        repository = ChallengeRepository(session)
        repository.add(new_challenge())

        with pytest.raises(ChallengeNotFoundError):
            repository.consume(b"c-1", "authentication", NOW)

    def test_an_expired_challenge_cannot_be_used(self, session: Session) -> None:
        repository = ChallengeRepository(session)
        repository.add(new_challenge())

        with pytest.raises(ChallengeNotFoundError):
            repository.consume(b"c-1", "registration", NOW + LIFETIME)

    def test_an_unknown_challenge_cannot_be_used(self, session: Session) -> None:
        with pytest.raises(ChallengeNotFoundError):
            ChallengeRepository(session).consume(b"nope", "registration", NOW)

    def test_expired_challenges_are_deleted_and_counted(self, session: Session) -> None:
        repository = ChallengeRepository(session)
        repository.add(new_challenge(b"old"))

        assert repository.delete_expired(NOW + LIFETIME) == 1
        assert repository.delete_expired(NOW + LIFETIME) == 0
