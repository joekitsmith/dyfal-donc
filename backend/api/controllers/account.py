import uuid

from api.errors import LastPasskeyError, PasskeyNotFoundError
from api.mappings import to_passkey_response
from api.schemas import PasskeyResponse
from persistence.database import UnitOfWork


def list_passkeys(
    unit_of_work: UnitOfWork, user_id: uuid.UUID
) -> tuple[PasskeyResponse, ...]:
    return tuple(
        to_passkey_response(credential)
        for credential in unit_of_work.credentials.for_user(user_id)
    )


def remove_passkey(
    unit_of_work: UnitOfWork, user_id: uuid.UUID, passkey_id: uuid.UUID
) -> None:
    """Remove one of the user's passkeys, unless it is their only way in."""
    passkeys = unit_of_work.credentials.for_user(user_id)
    if all(passkey.id != passkey_id for passkey in passkeys):
        raise PasskeyNotFoundError(f"Passkey {passkey_id} does not exist")

    if len(passkeys) == 1:
        raise LastPasskeyError("The last passkey cannot be removed")

    unit_of_work.credentials.delete(user_id, passkey_id)
    unit_of_work.commit()


def delete_account(unit_of_work: UnitOfWork, user_id: uuid.UUID) -> None:
    """Delete the user and everything that belongs to them."""
    unit_of_work.users.delete(user_id)
    unit_of_work.commit()
