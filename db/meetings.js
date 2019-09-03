export const create_meeting = 'INSERT INTO MEETING (TYPE, DAY, START_TIME, END_TIME, DESCRIPTION) VALUES ($1, $2, $3, $4, $5);';
export const get_all_meetings = 'SELECT * FROM MEETING;';
export const get_meetings_on_day = 'SELECT * FROM MEETING WHERE DAY = $1';
export const get_meetings_within_day_range = 'SELECT * FROM MEETING WHERE DAY GE $1 AND DAY LE $2;';
export const get_meetings_of_type = 'SELECT * FROM MEETING WHERE TYPE = $1;';
export const update_meeting = 'UPDATE MEETING SET TYPE = $1, DAY = $2, START_TIME = $3, END_TIME = $4, DESCRIPTION = $5 WHERE MEETING_ID = $6';
export const delete_meeting = 'DELETE FROM MEETING WHERE MEETING_ID = $1;';