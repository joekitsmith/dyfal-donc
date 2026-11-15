from api.controllers.account import delete_account, list_passkeys, remove_passkey
from api.controllers.audio import speak_exercise
from api.controllers.auth import (
    Authenticated,
    RegisteredPasskey,
    SignIn,
    authenticate,
    begin_passkey_authentication,
    begin_passkey_registration,
    finish_passkey_authentication,
    finish_passkey_registration,
    sign_out,
    start_guest,
)
from api.controllers.course import describe_course
from api.controllers.learners import (
    describe_progress,
    offer_exercise,
    record_outcome,
)

__all__ = [
    "Authenticated",
    "RegisteredPasskey",
    "SignIn",
    "authenticate",
    "begin_passkey_authentication",
    "begin_passkey_registration",
    "delete_account",
    "describe_course",
    "describe_progress",
    "finish_passkey_authentication",
    "finish_passkey_registration",
    "list_passkeys",
    "offer_exercise",
    "record_outcome",
    "remove_passkey",
    "sign_out",
    "speak_exercise",
    "start_guest",
]
