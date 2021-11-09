from flask import Flask, jsonify, request

from utilities import *

app = Flask(__name__)


@app.route('/meeting/types')
def meeting_types():
    results = db_execute('SELECT meeting_type FROM meeting_types')
    meeting_types = [meeting_type for (meeting_type,) in results]

    return jsonify(meeting_types)


@app.route('/meeting/validate')
def validate_meeting():
    meeting = request.get_json()
    id = request.args.get('id')

    with db_connection() as conn:
        # Check if meeting already exists
        with conn.cursor() as cur:
            if id is None:
                cur.execute(
                    'SELECT COUNT(*) '
                    'FROM meetings '
                    'WHERE meeting_type = %s '
                    'AND meeting_date = %s',
                    (meeting['meeting_type'], meeting['meeting_date'])
                )
            else:
                cur.execute(
                    'SELECT COUNT(*) '
                    'FROM meetings '
                    'WHERE meeting_type = %s '
                    'AND meeting_date = %s '
                    'AND meeting_id != %s',
                    (meeting['meeting_type'], meeting['meeting_date'], id)
                )
            (identical_meetings,) = cur.fetchone()

        # Check for unrecognized uniqnames
        new_uniqnames = list()
        for uniqname in meeting['attendees']:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT COUNT(*) '
                    'FROM members '
                    'WHERE uniqname = %s',
                    (uniqname,)
                )
                (attendee_exists,) = cur.fetchone()
            
            if attendee_exists == 0:
                new_uniqnames.append(uniqname)

    return {
        'already_exists': identical_meetings > 0,
        'new_uniqnames': new_uniqnames
    }


@app.route('/meeting', methods=['POST'])
def post_meeting():
    return 'Hello, World!'


@app.route('/meeting/id/<int:id>', methods=['PUT'])
def put_meeting(id):
    return 'Hello, World!'


@app.route('/meeting/id/<int:id>', methods=['DELETE'])
def delete_meeting(id):
    return 'Hello, World!'


@app.route('/meeting')
def get_all_meetings():
    return 'Hello, World!'


@app.route('/meeting/id/<int:id>')
def get_meeting_by_id(id):
    return 'Hello, World!'


@app.route('/meeting/uniqname/<string:uniqname>')
def get_meetings_by_uniqname(id):
    return 'Hello, World!'


@app.route('/active')
def get_active_members():
    return 'Hello, World!'
