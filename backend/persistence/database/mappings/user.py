from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import UserRecord


def to_user_record(row: models.User, *, is_guest: bool) -> UserRecord:
    return UserRecord(
        id=row.id,
        display_name=row.display_name,
        is_guest=is_guest,
        created_at=to_utc(row.created_at),
    )
