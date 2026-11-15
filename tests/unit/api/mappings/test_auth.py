import uuid
from datetime import UTC, datetime

from api.mappings import to_passkey_response, to_user_response
from persistence.database import CredentialRecord, UserRecord

MOMENT = datetime(2026, 1, 1, tzinfo=UTC)


class TestToUserResponse:
    def test_maps_the_fields_the_client_needs(self) -> None:
        record = UserRecord(
            id=uuid.uuid4(), display_name="Sam", is_guest=True, created_at=MOMENT
        )

        response = to_user_response(record)

        assert (response.id, response.is_guest, response.created_at) == (
            record.id,
            True,
            MOMENT,
        )
        assert set(response.model_dump()) == {"id", "is_guest", "created_at"}


class TestToPasskeyResponse:
    def test_maps_the_fields_without_the_key_material(self) -> None:
        record = CredentialRecord(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            credential_id=b"secret-ish",
            public_key=b"key",
            sign_count=4,
            transports=("internal",),
            label="Phone",
            created_at=MOMENT,
            last_used_at=None,
        )

        response = to_passkey_response(record)

        assert response.model_dump() == {
            "id": record.id,
            "label": "Phone",
            "created_at": MOMENT,
            "last_used_at": None,
        }
