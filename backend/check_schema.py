from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


def check_build_professions_table():
    # Create an engine that connects to the SQLite database
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create a Session
    db = SessionLocal()

    # Create an inspector
    inspector = inspect(engine)

    try:
        # Get table information
        tables = inspector.get_table_names()
        print("\n=== Tables in the database ===")
        for table in tables:
            print(f"\nTable: {table}")
            print("Columns:")
            for column in inspector.get_columns(table):
                print(
                    f"  {column['name']} ({column['type']}) - PK: {column.get('primary_key', False)}"
                )

            print("\nPrimary Key:")
            pk_constraint = inspector.get_pk_constraint(table)
            print(f"  {pk_constraint}")

            print("\nForeign Keys:")
            fks = inspector.get_foreign_keys(table)
            for fk in fks:
                print(f"  {fk}")

    finally:
        db.close()


if __name__ == "__main__":
    check_build_professions_table()
