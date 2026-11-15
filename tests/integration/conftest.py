import uuid
from collections.abc import Iterator

import pytest
from docker.errors import DockerException
from sqlalchemy import Engine, text
from sqlalchemy.engine import make_url
from testcontainers.community.postgres import PostgresContainer

from persistence.database import create_database_engine, create_schema


@pytest.fixture(scope="session")
def postgres() -> Iterator[PostgresContainer]:
    try:
        container = PostgresContainer("postgres:17", driver="psycopg")
        container.start()
    except DockerException as error:
        pytest.skip(f"Docker is not available: {error}")

    yield container
    container.stop()


@pytest.fixture
def empty_engine(postgres: PostgresContainer) -> Iterator[Engine]:
    """An engine for a new, empty database, so tests cannot affect each other."""
    name = f"test_{uuid.uuid4().hex}"
    url = make_url(postgres.get_connection_url())
    admin = create_database_engine(url.render_as_string(hide_password=False))
    with admin.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text(f'CREATE DATABASE "{name}"'))

    engine = create_database_engine(
        url.set(database=name).render_as_string(hide_password=False)
    )
    yield engine
    engine.dispose()
    admin.dispose()


@pytest.fixture
def engine(empty_engine: Engine) -> Engine:
    """An engine for a database with the tables created."""
    create_schema(empty_engine)
    return empty_engine
