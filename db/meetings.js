module.exports = {
    create_meeting: 'INSERT INTO MEETING (TYPE, DAY, START_TIME, END_TIME, DESCRIPTION) VALUES ($1, $2, $3, $4, $5) RETURNING MEETING_ID;',
    get_meeting_with_id: 'SELECT * FROM MEETING WHERE MEETING_ID = $1;',
    get_all_meetings: 'SELECT * FROM MEETING;',
    get_meetings_on_day: 'SELECT * FROM MEETING WHERE DAY = $1;',
    get_meetings_within_day_range: 'SELECT * FROM MEETING WHERE DAY BETWEEN $1 AND $2;',
    get_meetings_of_type: 'SELECT * FROM MEETING WHERE TYPE = $1;',
    update_meeting: 'UPDATE MEETING SET TYPE = $1, DAY = $2, START_TIME = $3, END_TIME = $4, DESCRIPTION = $5 WHERE MEETING_ID = $6 RETURNING MEETING_ID;',
    delete_meeting: 'DELETE FROM MEETING WHERE MEETING_ID = $1 RETURNING MEETING_ID;',
};