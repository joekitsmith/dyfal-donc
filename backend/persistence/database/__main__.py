from persistence.database.schema import create_schema
from persistence.database.session import create_database_engine
from persistence.database.settings import DatabaseSettings


def main() -> None:
    engine = create_database_engine(DatabaseSettings().url)
    create_schema(engine)
    engine.dispose()
    print("Created the tables that were missing")


if __name__ == "__main__":
    main()
