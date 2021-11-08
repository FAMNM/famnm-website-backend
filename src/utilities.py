import psycopg2
import os


def db_connection():
    """Returns a connection to the database."""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))


def db_execute(query, params=None):
    """
    Execute a command on the database.
    Each call to this function is its own transaction.
    Use `db_connection()` instead if you need to execute multiple commands as a single transaction.
    """
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
