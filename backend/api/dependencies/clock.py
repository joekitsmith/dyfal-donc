from typing import Annotated

from fastapi import Depends, Request

from api.clock import Clock


def get_clock(request: Request) -> Clock:
    clock: Clock = request.app.state.clock
    return clock


ClockDependency = Annotated[Clock, Depends(get_clock)]
