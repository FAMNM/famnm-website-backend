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


def get_meeting_info(meeting_id, conn=db_connection()):
    """Returns a dictionary of the meeting's information."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT meeting_type, meeting_date '
            'FROM meetings '
            'WHERE meeting_id = %s',
            (meeting_id,)
        )

        if cur.rowcount == 0:
            return None
        
        (meeting_type, meeting_date) = cur.fetchone()
    
    with conn.cursor() as cur:
        cur.execute(
            'SELECT uniqname '
            'FROM attendance '
            'WHERE meeting_id = %s',
            (meeting_id,)
        )
        attendees = [uniqname for (uniqname,) in cur.fetchall()]
    
    return {
        'meeting_type': meeting_type,
        'meeting_date': meeting_date.isoformat(),
        'attendees': attendees
    }


def member_in_database(uniqname, conn=db_connection()):
    """Returns whether the member is in the database."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT * '
            'FROM members '
            'WHERE uniqname = %s',
            (uniqname,)
        )
        member_exists = cur.rowcount > 0
    
    return member_exists
