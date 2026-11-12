"""Rebuild the database: create tables, load the CSV, transform. Safe to re-run."""
import subprocess
import sys
from pathlib import Path

from database.connection import get_connection

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def run_sql_file(path: Path) -> None:
    # Drop full-line comments, then split into statements.
    # This assumes the file has no stored procedures or DELIMITER lines.
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if not line.strip().startswith("--")]
    statements = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(statement)
        connection.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
    print(f"Ran {path.name} ({len(statements)} statements)")


def main() -> None:
    run_sql_file(SQL_DIR / "02_create_tables.sql")
    subprocess.run([sys.executable, "-m", "scripts.load_staging"], check=True)
    run_sql_file(SQL_DIR / "03_transform.sql")


if __name__ == "__main__":
    main()