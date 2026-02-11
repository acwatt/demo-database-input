"""
Database utilities for demo-database-input.

Provides async connection management and query execution utilities
for use with FastAPI and aiosqlite.
"""

import aiosqlite
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = "data/projects.db"


async def get_connection(db_path: str = DEFAULT_DB_PATH) -> aiosqlite.Connection:
    """
    Get an async database connection with WAL mode enabled.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        Async SQLite connection
    """
    conn = await aiosqlite.connect(db_path)
    # Enable WAL mode for better concurrency
    await conn.execute("PRAGMA journal_mode=WAL")
    # Return rows as dictionaries
    conn.row_factory = aiosqlite.Row
    return conn


async def execute_query(
    query: str,
    params: Optional[Tuple] = None,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Execute a query that modifies data (INSERT, UPDATE, DELETE).

    Args:
        query: SQL query with ? placeholders
        params: Query parameters
        db_path: Path to database file

    Returns:
        Last row ID (for INSERT) or row count (for UPDATE/DELETE)
    """
    try:
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("PRAGMA journal_mode=WAL")
            cursor = await conn.execute(query, params or ())
            await conn.commit()
            return cursor.lastrowid if query.strip().upper().startswith("INSERT") else cursor.rowcount
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


async def fetch_one(
    query: str,
    params: Optional[Tuple] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single row from the database.

    Args:
        query: SQL query with ? placeholders
        params: Query parameters
        db_path: Path to database file

    Returns:
        Row as dictionary or None if not found
    """
    try:
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("PRAGMA journal_mode=WAL")
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params or ())
            row = await cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching row: {e}")
        raise


async def fetch_all(
    query: str,
    params: Optional[Tuple] = None,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """
    Fetch all rows from the database.

    Args:
        query: SQL query with ? placeholders
        params: Query parameters
        db_path: Path to database file

    Returns:
        List of rows as dictionaries
    """
    try:
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("PRAGMA journal_mode=WAL")
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params or ())
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching rows: {e}")
        raise


async def ensure_database_exists(db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Check if database exists and is accessible.

    Args:
        db_path: Path to database file

    Returns:
        True if database exists and is accessible
    """
    try:
        db_file = Path(db_path)
        if not db_file.exists():
            logger.error(f"Database not found at {db_path}")
            return False

        # Try to connect and query
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='work_projects'"
            )
            result = await cursor.fetchone()
            if result:
                logger.info("Database verified successfully")
                return True
            else:
                logger.error("Database exists but 'work_projects' table not found")
                return False
    except Exception as e:
        logger.error(f"Error verifying database: {e}")
        return False
