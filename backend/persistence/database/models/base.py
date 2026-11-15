from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base of the tables. Timestamps are stored in UTC."""
