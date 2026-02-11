#!/usr/bin/env python3
"""
Database initialization script for demo-database-input.

Creates the SQLite database with schema, indexes, and triggers.
Enables WAL mode for better concurrency.
"""

import sqlite3
import sys
from pathlib import Path


def init_database(db_path: str = "data/projects.db") -> bool:
    """
    Initialize the database with schema from schema.sql.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure data directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        wal_mode = cursor.fetchone()[0]
        print(f"✓ WAL mode enabled: {wal_mode}")

        # Read and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        cursor.executescript(schema_sql)
        print("✓ Schema created successfully")

        # Verify table creation
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='work_projects'"
        )
        if cursor.fetchone():
            print("✓ Table 'work_projects' verified")
        else:
            print("✗ Error: Table 'work_projects' not found")
            return False

        # Verify indexes
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='work_projects'"
        )
        indexes = cursor.fetchall()
        print(f"✓ Created {len(indexes)} indexes")

        # Verify trigger
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='work_projects'"
        )
        triggers = cursor.fetchall()
        print(f"✓ Created {len(triggers)} trigger(s)")

        # Commit and close
        conn.commit()
        conn.close()

        print(f"\n✓ Database initialized successfully at: {db_path}")
        return True

    except Exception as e:
        print(f"\n✗ Error initializing database: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Allow custom database path via command line
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/projects.db"
    success = init_database(db_path)
    sys.exit(0 if success else 1)
