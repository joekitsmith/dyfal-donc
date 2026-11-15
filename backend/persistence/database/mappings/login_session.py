from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import LoginSessionRecord


def to_login_session_record(row: models.LoginSession) -> LoginSessionRecord:
    return LoginSessionRecord(
        id=row.id,
        user_id=row.user_id,
        created_at=to_utc(row.created_at),
        authenticated_at=to_utc(row.authenticated_at),
        last_seen_at=to_utc(row.last_seen_at),
        expires_at=to_utc(row.expires_at),
    )
