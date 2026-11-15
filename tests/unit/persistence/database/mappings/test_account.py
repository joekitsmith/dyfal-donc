import uuid

from persistence.database import models
from persistence.database.mappings import (
    to_challenge_record,
    to_credential_record,
    to_login_session_record,
    to_user_record,
)
from tests.unit.persistence.database.mappings.conftest import MOMENT, TOKYO

USER_ID = uuid.uuid4()


class TestToUserRecord:
    def test_maps_every_field(self) -> None:
        row = models.User(id=USER_ID, display_name="Sam", created_at=MOMENT)

        record = to_user_record(row, is_guest=False)

        assert (record.id, record.display_name, record.is_guest) == (
            USER_ID,
            "Sam",
            False,
        )
        assert record.created_at == MOMENT


class TestToCredentialRecord:
    def test_maps_every_field_in_utc(self) -> None:
        row = models.WebauthnCredential(
            id=uuid.uuid4(),
            user_id=USER_ID,
            credential_id=b"id",
            public_key=b"key",
            sign_count=3,
            transports=["internal"],
            label="Phone",
            created_at=MOMENT.astimezone(TOKYO),
            last_used_at=None,
        )

        record = to_credential_record(row)

        assert record.transports == ("internal",)
        assert record.created_at == MOMENT
        assert record.created_at.utcoffset() == MOMENT.utcoffset()
        assert record.last_used_at is None
        assert (record.credential_id, record.public_key, record.sign_count) == (
            b"id",
            b"key",
            3,
        )


class TestToLoginSessionRecord:
    def test_maps_every_field(self) -> None:
        row = models.LoginSession(
            id=uuid.uuid4(),
            user_id=USER_ID,
            token_hash=b"hash",
            created_at=MOMENT,
            authenticated_at=MOMENT.astimezone(TOKYO),
            last_seen_at=MOMENT,
            expires_at=MOMENT.astimezone(TOKYO),
        )

        record = to_login_session_record(row)

        assert record.user_id == USER_ID
        assert record.authenticated_at == MOMENT
        assert record.authenticated_at.utcoffset() == MOMENT.utcoffset()
        assert record.expires_at == MOMENT
        assert record.expires_at.utcoffset() == MOMENT.utcoffset()


class TestToChallengeRecord:
    def test_maps_every_field(self) -> None:
        row = models.WebauthnChallenge(
            challenge=b"c", purpose="registration", user_id=USER_ID
        )

        record = to_challenge_record(row)

        assert (record.challenge, record.purpose, record.user_id) == (
            b"c",
            "registration",
            USER_ID,
        )
