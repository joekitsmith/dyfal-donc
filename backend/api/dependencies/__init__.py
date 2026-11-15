from api.dependencies.clock import ClockDependency, get_clock
from api.dependencies.course import CourseReleaseDependency, get_course_release
from api.dependencies.database import UnitOfWorkDependency, get_unit_of_work
from api.dependencies.login import (
    AuthenticatedDependency,
    LearnerIdDependency,
    SessionTokenDependency,
    get_authenticated,
    get_learner_id,
    get_session_token,
    require_known_origin,
)
from api.dependencies.settings import (
    LoginSessionSettingsDependency,
    PasskeySettingsDependency,
    SelectionLifetimeDependency,
    get_login_session_settings,
    get_passkey_settings,
    get_selection_lifetime,
)
from api.dependencies.speech import SpeechClientDependency, get_speech_client

__all__ = [
    "AuthenticatedDependency",
    "ClockDependency",
    "CourseReleaseDependency",
    "LearnerIdDependency",
    "LoginSessionSettingsDependency",
    "PasskeySettingsDependency",
    "SelectionLifetimeDependency",
    "SessionTokenDependency",
    "SpeechClientDependency",
    "UnitOfWorkDependency",
    "get_authenticated",
    "get_clock",
    "get_course_release",
    "get_learner_id",
    "get_login_session_settings",
    "get_passkey_settings",
    "get_selection_lifetime",
    "get_session_token",
    "get_speech_client",
    "get_unit_of_work",
    "require_known_origin",
]
