import os

import flask
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS

from utilities import *

app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app)


# This function is called before all endpoints annotated with `@auth.login_required`
# If it returns False, the request is aborted with a 401
@auth.verify_password
def verify_password(username, password):
    famnm_passphrase = os.environ.get('FAMNM_PASSPHRASE')

    if famnm_passphrase is not None:
        return username.casefold() == 'famnm'.casefold() and password.casefold() == famnm_passphrase.casefold()
    else:
        # FAMNM_PASSPHRASE is not set
        return False


@app.route('/api/v2/meeting')
def get_all_meetings():
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT meeting_id '
                'FROM meetings'
            )
            meeting_ids = [meeting_id for (meeting_id,) in cur.fetchall()]

        return flask.jsonify([meeting_info(meeting_id, conn) for meeting_id in meeting_ids])


@app.route('/api/v2/meeting', methods=['POST', 'PUT'])
@auth.login_required
def create_meeting():
    meeting_type, meeting_date, attendees = extract_meeting_info()

    with db_connection(writable=True) as conn:
        insert_meeting_type(meeting_type, conn)

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

        insert_attendance(meeting_id, attendees, conn)

    return '', 201


@app.route('/api/v2/meeting/id/<int:meeting_id>')
def get_meeting_by_id(meeting_id):
    with db_connection() as conn:
        response = meeting_info(meeting_id, conn)

        if response is not None:
            return flask.jsonify(response)
        else:
            flask.abort(404, f'No meeting with id {meeting_id}')


@app.route('/api/v2/meeting/id/<int:meeting_id>', methods=['PUT'])
@auth.login_required
def update_meeting(meeting_id):
    meeting_type, meeting_date, attendees = extract_meeting_info()

    with db_connection(writable=True) as conn:
        insert_meeting_type(meeting_type, conn)

        # Update meeting
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE meetings '
                'SET meeting_type = %s, meeting_date = %s '
                'WHERE meeting_id = %s '
                'RETURNING *',
                (meeting_type, meeting_date, meeting_id)
            )

            if cur.rowcount == 0:
                flask.abort(404, f'Meeting {meeting_id} not found')

        insert_attendance(meeting_id, attendees, conn)

    return '', 204


@app.route('/api/v2/meeting/id/<int:meeting_id>', methods=['DELETE'])
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


@app.route('/api/v2/meeting/uniqname/<uniqname>')
def get_meeting_by_uniqname(uniqname):
    with db_connection() as conn:
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


@app.route('/api/v2/meeting/validate')
def validate_meeting():
    try:
        meeting_type, meeting_date, attendees = extract_meeting_info()
    except ValueError as e:
        flask.abort(400, e)

    with db_connection() as conn:
        # Check if meeting already exists
        with conn.cursor() as cur:
            cur.execute(
                'SELECT * '
                'FROM meetings '
                'WHERE meeting_type = %s '
                'AND meeting_date = %s',
                (meeting_type, meeting_date)
            )
            already_exists = cur.rowcount > 0

        # Check for unrecognized uniqnames
        new_members = [
            uniqname for uniqname in attendees if not member_in_database(uniqname, conn)]

    return {
        'already_exists': already_exists,
        'new_uniqnames': new_members
    }


@app.route('/api/v2/meeting/validate/id/<int:meeting_id>')
def validate_meeting_by_id(meeting_id):
    try:
        meeting_type, meeting_date, attendees = extract_meeting_info()
    except ValueError as e:
        flask.abort(400, e)

    with db_connection() as conn:
        # Check if meeting already exists
        with conn.cursor() as cur:
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


@app.route('/api/v2/meeting/types')
def get_meeting_types():
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT meeting_type '
                'FROM meeting_types'
            )
            meeting_types = [meeting_type for (
                meeting_type,) in cur.fetchall()]

    return flask.jsonify(meeting_types)


@app.route('/api/v2/member')
def get_all_members():
    with db_connection() as conn:
        return flask.jsonify(all_member_info(conn))


@app.route('/api/v2/member/uniqname/<uniqname>')
def get_member_by_uniqname(uniqname):
    with db_connection() as conn:
        result = member_info([uniqname], conn)

        if len(result) == 1:
            return result[0]
        else:
            flask.abort(404, f'Records not found for {uniqname}')


@app.route('/api/v2/member/uniqname/<uniqname>', methods=['POST', 'PUT'])
@auth.login_required
def create_or_update_member(uniqname):
    try:
        mentor = request.get_json()['mentor']
    except KeyError as e:
        flask.abort(400, f'{e} not in JSON body')

    with db_connection(writable=True) as conn:
        if member_in_database(uniqname, conn):
            if request.method == 'POST':
                flask.abort(
                    400, f'{uniqname} already has a record (use PUT to update existing records)')

            created_new_member = False
        else:
            created_new_member = True

        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO members(uniqname, mentor) '
                'VALUES (%s, %s) '
                'ON CONFLICT (uniqname) DO '
                'UPDATE SET mentor = EXCLUDED.mentor',
                (uniqname, mentor)
            )

    return '', (201 if created_new_member else 204)


@app.route('/api/v2/member/active')
def get_active_members():
    with db_connection() as conn:
        active_members = [member for member in all_member_info(
            conn) if member['active']]

    return flask.jsonify(active_members)
