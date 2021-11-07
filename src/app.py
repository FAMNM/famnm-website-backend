from flask import Flask

app = Flask(__name__)


@app.route('/meeting/types')
def meeting_types():
    return 'Hello, World!'


@app.route('/meeting/validate')
def validate_meeting():
    return 'Hello, World!'


@app.route('/meeting/validate/id/<int:id>')
def validate_meeting_by_id(id):
    return 'Hello, World!'


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
