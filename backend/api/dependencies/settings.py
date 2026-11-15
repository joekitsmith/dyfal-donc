from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request


def get_selection_lifetime(request: Request) -> timedelta:
    lifetime: timedelta = request.app.state.selection_lifetime
    return lifetime


SelectionLifetimeDependency = Annotated[timedelta, Depends(get_selection_lifetime)]
