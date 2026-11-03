import sqlite3

DB_PATH = "hermes_state.db"


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS email_processing (
            message_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return connection


def get_email_status(message_id):
    with _connect() as connection:
        row = connection.execute(
            "SELECT status FROM email_processing WHERE message_id = ?",
            (message_id,),
        ).fetchone()
    return row[0] if row else None


def set_email_status(message_id, status):
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO email_processing (message_id, status, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(message_id) DO UPDATE SET
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (message_id, status),
        )
