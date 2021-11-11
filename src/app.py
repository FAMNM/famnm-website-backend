import os

import flask
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth

from utilities import *

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    famnm_passphrase = os.environ.get('FAMNM_PASSPHRASE')

    if famnm_passphrase is not None:
        return username.casefold() == 'famnm'.casefold() and password.casefold() == famnm_passphrase.casefold()
    else:
        # FAMNM_PASSPHRASE is not set
        return False


@app.route('/meeting/types')
def meeting_types():
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT meeting_type '
                'FROM meeting_types'
            )
        meeting_types = [meeting_type for (meeting_type,) in cur.fetchall()]

    return flask.jsonify(meeting_types)


@app.route('/meeting/validate')
def validate_meeting():
    try:
        meeting_id, meeting_type, meeting_date, attendees = extract_meeting_info(
            request.get_json())
    except ValueError as e:
        flask.abort(400, e)

    with db_connection() as conn:
        # Check if meeting already exists
        with conn.cursor() as cur:
            if meeting_id is None:
                cur.execute(
                    'SELECT * '
                    'FROM meetings '
                    'WHERE meeting_type = %s '
                    'AND meeting_date = %s',
                    (meeting_type, meeting_date)
                )
            else:
                cur.execute(
                    'SELECT * '
                    'FROM meetings '
                    'WHERE meeting_type = %s '
                    'AND meeting_date = %s '
                    'AND meeting_id != %s',
                    (meeting_type, meeting_date, meeting_id)
                )
            already_exists = cur.rowcount > 0

        # Check for unrecognized uniqnames
        new_members = [
            uniqname for uniqname in attendees if not member_in_database(uniqname, conn)]

    return {
        'already_exists': already_exists,
        'new_uniqnames': new_members
    }


@app.route('/meeting')
def get_meeting():
    meeting_id = request.args.get('id')
    uniqname = request.args.get('uniqname')

    with db_connection() as conn:
        if meeting_id is not None and uniqname is not None:
            flask.abort(
                400, '\'id\' and \'uniqname\' cannot be specified in the same request')
        elif meeting_id is not None:
            # Get meeting by ID
            response = meeting_info(meeting_id, conn)

            if response is not None:
                return flask.jsonify(response)
            else:
                flask.abort(404, f'No meeting with id {meeting_id}')
        elif uniqname is not None:
            # Get meetings attended by uniqname
            if not member_in_database(uniqname, conn):
                flask.abort(404, f'Records not found for {uniqname}')

            with conn.cursor() as cur:
                cur.execute(
                    'SELECT meeting_id '
                    'FROM attendance '
                    'WHERE uniqname = %s',
                    (uniqname,)
                )
                meeting_ids = [meeting_id for (meeting_id,) in cur.fetchall()]

            return flask.jsonify([meeting_info(meeting_id, conn) for meeting_id in meeting_ids])
        else:
            # Get all meetings
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT meeting_id '
                    'FROM meetings'
                )
                meeting_ids = [meeting_id for (meeting_id,) in cur.fetchall()]

            return flask.jsonify([meeting_info(meeting_id, conn) for meeting_id in meeting_ids])


@app.route('/meeting', methods=['POST', 'PUT'])
@auth.login_required
def post_meeting():
    try:
        meeting_id, meeting_type, meeting_date, attendees = extract_meeting_info(
            request.get_json())
    except ValueError as e:
        flask.abort(400, e)

    with db_connection(writable=True) as conn:
        # Add meeting type if it doesn't exist
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO meeting_types '
                'VALUES (%s) '
                'ON CONFLICT DO NOTHING',
                (meeting_type,)
            )

        if meeting_id is not None:
            if request.method == 'POST':
                flask.abort(400, 'Use PUT to update existing meetings')

            if not meeting_in_database(meeting_id, conn):
                flask.abort(404, f'Meeting {meeting_id} not found')

            # Update meeting
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE meetings '
                    'SET meeting_type = %s, meeting_date = %s '
                    'WHERE meeting_id = %s',
                    (meeting_type, meeting_date, meeting_id)
                )

            created_new = False
        else:
            # Create meeting
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        'INSERT INTO meetings(meeting_type, meeting_date) '
                        'VALUES (%s, %s) '
                        'RETURNING meeting_id',
                        (meeting_type, meeting_date)
                    )
                except psycopg2.errors.UniqueViolation:
                    flask.abort(
                        400, f'{meeting_type} meeting on {meeting_date} already exists')

                (meeting_id,) = cur.fetchone()

            created_new = True

        for uniqname in attendees:
            # Add any new uniqnames
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

    return '', (201 if created_new else 204)


@app.route('/meeting/id/<int:meeting_id>', methods=['DELETE'])
@auth.login_required
def delete_meeting(meeting_id):
    with db_connection(writable=True) as conn:
        if not meeting_in_database(meeting_id, conn):
            flask.abort(404, f'Meeting {meeting_id} not found')

        with conn.cursor() as cur:
            cur.execute(
                'DELETE FROM meetings '
                'WHERE meeting_id = %s',
                (meeting_id,)
            )

    return '', 204


@app.route('/member')
def get_member():
    uniqname = request.args.get('uniqname')

    with db_connection() as conn:
        if uniqname is not None:
            # Get member by uniqname
            result = member_info([uniqname], conn)

            if len(result) == 1:
                return result[0]
            else:
                flask.abort(404, f'Records not found for {uniqname}')
        else:
            # Get all members
            return flask.jsonify(all_member_info(conn))


@app.route('/member/active')
def get_active_members():
    with db_connection() as conn:
        active_members = [member for member in all_member_info(
            conn) if member['active']]

    return flask.jsonify(active_members)


@app.route('/member', methods=['POST', 'PUT'])
@auth.login_required
def post_member():
    member = request.get_json()

    try:
        uniqname = member['uniqname']
        mentor = member['mentor']
    except KeyError as e:
        flask.abort(400, f'{e} not in JSON body')

    with db_connection(writable=True) as conn:
        if member_in_database(uniqname, conn):
            if request.method == 'POST':
                flask.abort(
                    400, f'{uniqname} already has a record (use PUT to update existing records)')
            else:
                with conn.cursor() as cur:
                    cur.execute(
                        'UPDATE members '
                        'SET mentor = %s '
                        'WHERE uniqname = %s',
                        (mentor, uniqname)
                    )

                return '', 204
        else:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO members(uniqname, mentor) '
                    'VALUES (%s, %s)',
                    (uniqname, mentor)
                )

            return '', 201
