from persistence.database.session import create_database_engine, create_session_factory


class TestSession:
    def test_creating_an_engine_does_not_connect(self) -> None:
        engine = create_database_engine("postgresql+psycopg://nobody@unreachable/db")

        assert engine.url.host == "unreachable"

    def test_sessions_keep_their_objects_after_commit(self) -> None:
        engine = create_database_engine("postgresql+psycopg://nobody@unreachable/db")

        factory = create_session_factory(engine)

        assert factory.kw["expire_on_commit"] is False
