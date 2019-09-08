module.exports = {
    create_attendance_entry: "INSERT INTO ATTENDANCE (UNIQNAME, MEETING_ID) VALUES ($1, $2);",
    get_attendance_for_uniqname: "SELECT MEETING_ID FROM ATTENDANCE WHERE UNIQNAME = $1;",
    get_attendance_for_meeting: "SELECT UNIQNAME FROM ATTENDANCE WHERE MEETING_ID = $1;",
    delete_attendance_entry: "DELETE FROM ATTENDANCE WHERE UNIQNAME = $1 AND MEETING_ID = $2;"
};