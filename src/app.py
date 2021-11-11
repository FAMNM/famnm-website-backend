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
    results = db_execute('SELECT meeting_type FROM meeting_types')
    meeting_types = [meeting_type for (meeting_type,) in results]

    return flask.jsonify(meeting_types)


@app.route('/meeting/validate')
def validate_meeting():
    meeting = request.get_json()
    id = request.args.get('id')

    with db_connection() as conn:
        # Check if meeting already exists
        with conn.cursor() as cur:
            if id is None:
                cur.execute(
                    'SELECT * '
                    'FROM meetings '
                    'WHERE meeting_type = %s '
                    'AND meeting_date = %s',
                    (meeting['meeting_type'], meeting['meeting_date'])
                )
            else:
                cur.execute(
                    'SELECT * '
                    'FROM meetings '
                    'WHERE meeting_type = %s '
                    'AND meeting_date = %s '
                    'AND meeting_id != %s',
                    (meeting['meeting_type'], meeting['meeting_date'], id)
                )
            already_exists = cur.rowcount > 0

        # Check for unrecognized uniqnames
        new_members = [uniqname for uniqname in meeting['attendees']
                       if not member_in_database(uniqname, conn)]

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
            return 'id and uniqname cannot be specified in the same request', 400
        elif meeting_id is not None:
            # Get meeting by ID
            response = get_meeting_info(meeting_id, conn)

            if response is not None:
                return flask.jsonify(response)
            else:
                return f'No meeting with id {meeting_id}', 404
        elif uniqname is not None:
            # Get meetings attended by uniqname
            if not member_in_database(uniqname, conn):
                return f'Records not found for {uniqname}', 404

            with conn.cursor() as cur:
                cur.execute(
                    'SELECT meeting_id '
                    'FROM attendance '
                    'WHERE uniqname = %s',
                    (uniqname,)
                )
                meeting_ids = [meeting_id for (meeting_id,) in cur.fetchall()]

            return flask.jsonify([get_meeting_info(meeting_id, conn) for meeting_id in meeting_ids])
        else:
            # Get all meetings
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT meeting_id '
                    'FROM meetings'
                )
                meeting_ids = [meeting_id for (meeting_id,) in cur.fetchall()]

            return flask.jsonify([get_meeting_info(meeting_id, conn) for meeting_id in meeting_ids])


@app.route('/meeting', methods=['POST'])
@auth.login_required
def post_meeting():
    return 'Hello, World!'


@app.route('/meeting/id/<int:id>', methods=['PUT'])
@auth.login_required
def put_meeting(id):
    return 'Hello, World!'


@app.route('/meeting/id/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_meeting(id):
    return 'Hello, World!'


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
                return f'Records not found for {uniqname}', 404
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
        return f'{e} not in JSON body', 400

    with db_connection(writable=True) as conn:
        if member_in_database(uniqname, conn):
            if request.method == 'POST':
                return f'{uniqname} already has a record (use PUT to update existing records)', 400
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
                    'INSERT INTO members '
                    'VALUES (%s, %s)',
                    (uniqname, mentor)
                )

            return '', 201
