import subprocess
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

import docker
import httpx2
import pytest
from docker.errors import DockerException
from sqlalchemy import Engine, text
from sqlalchemy.engine import make_url
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer

from persistence.database import create_database_engine, create_schema

REPOSITORY_ROOT = Path(__file__).parents[2]
TTS_DOCKERFILE = "backend/tts/Dockerfile"
TTS_IMAGE = "dyfal-tts-test"
TTS_PORT = 8001
TTS_STARTUP_SECONDS = 120


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


@pytest.fixture(scope="session")
def tts_url() -> Iterator[str]:
    """The address of the speech service, built from its Dockerfile and started.

    The image is built with the Docker CLI, because its Dockerfile needs BuildKit.
    """
    try:
        docker.from_env().ping()
    except DockerException as error:
        pytest.skip(f"Docker is not available: {error}")

    subprocess.run(
        ["docker", "build", "--file", TTS_DOCKERFILE, "--tag", TTS_IMAGE, "."],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    container = DockerContainer(TTS_IMAGE).with_exposed_ports(TTS_PORT)
    container.start()
    host, port = container.get_container_host_ip(), container.get_exposed_port(TTS_PORT)
    url = f"http://{host}:{port}"
    deadline = time.monotonic() + TTS_STARTUP_SECONDS
    while not _is_healthy(url):
        if time.monotonic() > deadline:
            container.stop()
            pytest.fail("The speech service did not become healthy")

        time.sleep(1)

    yield url
    container.stop()


def _is_healthy(url: str) -> bool:
    try:
        return httpx2.get(f"{url}/health", timeout=2).status_code == 200
    except httpx2.HTTPError:
        return False
