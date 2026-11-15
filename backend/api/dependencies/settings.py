from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request

from api.settings import LoginSessionSettings, PasskeySettings


def get_selection_lifetime(request: Request) -> timedelta:
    lifetime: timedelta = request.app.state.selection_lifetime
    return lifetime


SelectionLifetimeDependency = Annotated[timedelta, Depends(get_selection_lifetime)]


def get_passkey_settings(request: Request) -> PasskeySettings:
    settings: PasskeySettings = request.app.state.passkey_settings
    return settings


def get_login_session_settings(request: Request) -> LoginSessionSettings:
    settings: LoginSessionSettings = request.app.state.login_session_settings
    return settings


PasskeySettingsDependency = Annotated[PasskeySettings, Depends(get_passkey_settings)]
LoginSessionSettingsDependency = Annotated[
    LoginSessionSettings, Depends(get_login_session_settings)
]
