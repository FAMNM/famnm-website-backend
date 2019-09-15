module.exports = {
    create_meeting_type: "INSERT INTO MEETING_TYPE (TYPE) VALUES $1 RETURNING TYPE;",
    get_all_meeting_types: "SELECT TYPE FROM MEETING_TYPE;",
    delete_meeting_type: "DELETE FROM MEETING_TYPE WHERE TYPE = $1 RETURNING TYPE;"
};