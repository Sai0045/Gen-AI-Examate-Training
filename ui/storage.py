import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Project and database paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "teekatimer_ui.db"


def get_connection():
    """Create a connection to the SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """Create the required database tables."""

    with get_connection() as connection:

        # Store user feedback on assistant answers.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
                mode TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Store completed vaccine doses for each baby's DOB.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS completed_doses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_of_birth TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                dose_number INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                UNIQUE(date_of_birth, record_id, dose_number)
            )
        """)


def save_feedback(question, answer, rating, mode):
    """Save a thumbs-up or thumbs-down rating."""

    if rating not in (-1, 1):
        raise ValueError("Rating must be 1 or -1.")

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO feedback
            (question, answer, rating, mode, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (question, answer, rating, mode, created_at)
        )

        return cursor.lastrowid


def save_dose_status(date_of_birth, record_id, dose_number, is_done):
    """Mark a vaccine dose as Done or remove its Done status."""

    with get_connection() as connection:

        if is_done:
            completed_at = datetime.now(timezone.utc).isoformat()

            connection.execute(
                """
                INSERT INTO completed_doses
                (date_of_birth, record_id, dose_number, completed_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(date_of_birth, record_id, dose_number)
                DO UPDATE SET completed_at = excluded.completed_at
                """,
                (
                    date_of_birth,
                    record_id,
                    dose_number,
                    completed_at
                )
            )

        else:
            connection.execute(
                """
                DELETE FROM completed_doses
                WHERE date_of_birth = ?
                AND record_id = ?
                AND dose_number = ?
                """,
                (date_of_birth, record_id, dose_number)
            )


def get_completed_doses(date_of_birth):
    """Return the completed vaccine doses for a baby's DOB."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT record_id, dose_number
            FROM completed_doses
            WHERE date_of_birth = ?
            """,
            (date_of_birth,)
        ).fetchall()

    return {
        (row["record_id"], row["dose_number"])
        for row in rows
    }
