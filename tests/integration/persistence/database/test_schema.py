from sqlalchemy import Engine, inspect

from persistence.database import create_schema

TABLES = {"learners", "issued_selections", "review_events"}


class TestCreateSchema:
    def test_creates_the_tables(self, empty_engine: Engine) -> None:
        create_schema(empty_engine)

        assert TABLES <= set(inspect(empty_engine).get_table_names())

    def test_can_be_run_again(self, engine: Engine) -> None:
        create_schema(engine)

        assert TABLES <= set(inspect(engine).get_table_names())
