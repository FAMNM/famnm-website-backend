import psycopg2
import os
import datetime

import flask


def db_connection(writable=False):
    """Returns a connection to the database."""
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.readonly = not writable
    return conn


def extract_meeting_info():
    """
    Extract meeting info from the JSON in the request body.

    Raises ValueError if the meeting is invalid.
    Returns `meeting_id`, `meeting_type`, `meeting_date`, `attendees`.
    """
    meeting = flask.request.get_json()

    try:
        meeting_type = str(meeting['meeting_type'])
    except KeyError as e:
        flask.abort(400, f'{e} not in JSON body')

    try:
        meeting_date = datetime.date.fromisoformat(meeting['meeting_date'])
    except KeyError as e:
        flask.abort(400, f'{e} not in JSON body')
    except ValueError as e:
        flask.abort(400, str(e))

    try:
        attendees = list(meeting['attendees'])
    except KeyError as e:
        flask.abort(400, f'{e} not in JSON body')
    except TypeError as e:
        flask.abort(400, '\'attendees\' must be an array')

    return meeting_type, meeting_date, attendees


def meeting_in_database(meeting_id, conn):
    """Returns whether the member is in the database."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT * '
            'FROM meetings '
            'WHERE meeting_id = %s',
            (meeting_id,)
        )
        meeting_exists = cur.rowcount > 0

    return meeting_exists


def meeting_info(meeting_id, conn):
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
        'id': meeting_id,
        'meeting_type': meeting_type,
        'meeting_date': meeting_date.isoformat(),
        'attendees': attendees
    }


def member_in_database(uniqname, conn):
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


def member_info(uniqnames, conn):
    """Returns a dictionary of the given members' information."""
    current_semester_start, current_semester_end = current_semester(conn)
    last_semester_start, last_semester_end = last_semester(conn)

    members = list()
    for uniqname in uniqnames:
        if member_in_database(uniqname, conn):
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT * '
                    'FROM attendance '
                    'INNER JOIN meetings ON attendance.meeting_id = meetings.meeting_id '
                    'WHERE uniqname = %s '
                    'AND meetings.meeting_date BETWEEN %s AND %s',
                    (uniqname, current_semester_start, current_semester_end)
                )
                attendance_this_semester = cur.rowcount

            with conn.cursor() as cur:
                cur.execute(
                    'SELECT * '
                    'FROM attendance '
                    'INNER JOIN meetings ON attendance.meeting_id = meetings.meeting_id '
                    'WHERE uniqname = %s '
                    'AND meetings.meeting_date BETWEEN %s AND %s',
                    (uniqname, last_semester_start, last_semester_end)
                )
                attendance_last_semester = cur.rowcount

            with conn.cursor() as cur:
                cur.execute(
                    'SELECT mentor '
                    'FROM members '
                    'WHERE uniqname = %s',
                    (uniqname,)
                )
                (mentor,) = cur.fetchone()

            members.append({
                'uniqname': uniqname,
                'active': attendance_this_semester >= 4 or attendance_last_semester >= 4 or (True if mentor else False),
                'last_semester': attendance_last_semester,
                'this_semester': attendance_this_semester,
                'mentor': mentor,
            })

    return members


def all_member_info(conn):
    """Returns a dictionary of all members' information."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT uniqname '
            'FROM members'
        )
        all_uniqnames = [uniqname for (uniqname,) in cur.fetchall()]

    return member_info(all_uniqnames, conn)


def insert_meeting_type(meeting_type, conn):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO meeting_types(meeting_type) '
            'VALUES (%s) '
            'ON CONFLICT DO NOTHING',
            (meeting_type,)
        )


def insert_attendance(meeting_id, attendees, conn):
    for uniqname in attendees:
        # Add any new uniqnames to the database
        if not member_in_database(uniqname, conn):
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO members(uniqname) '
                    'VALUES (%s)',
                    (uniqname,)
                )

        # Add attendance
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO attendance(meeting_id, uniqname) '
                'VALUES (%s, %s) '
                'ON CONFLICT DO NOTHING',
                (meeting_id, uniqname)
            )


def semester(conn, ending_date):
    """Returns the starting and ending date of the semester with the given ending date."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT MAX(starting_date) '
            'FROM semesters '
            'WHERE starting_date <= %s',
            (ending_date,)
        )
        (starting_date,) = cur.fetchone()

    return starting_date, ending_date


def current_semester(conn):
    """Returns the starting and ending date of the current semester."""
    return semester(conn, datetime.date.today())


def last_semester(conn):
    """Returns the starting and ending date of last semester."""
    current_semester_start, _ = current_semester(conn)

    return semester(conn, current_semester_start - datetime.timedelta(days=1))
