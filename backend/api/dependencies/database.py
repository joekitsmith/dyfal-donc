from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request

from persistence.database import UnitOfWork


def get_unit_of_work(request: Request) -> Iterator[UnitOfWork]:
    """A unit of work for one request. Whatever is not committed is rolled back."""
    with request.app.state.session_factory() as session:
        yield UnitOfWork(session)


UnitOfWorkDependency = Annotated[UnitOfWork, Depends(get_unit_of_work)]
