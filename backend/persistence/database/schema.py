from sqlalchemy import Engine

from persistence.database.models import Base


def create_schema(engine: Engine) -> None:
    """Create any of the tables that do not exist yet.

    Tables that already exist are left alone, so this does not change the shape
    of a database that has one. That needs migrations, which are not set up yet.
    """
    Base.metadata.create_all(engine)
