export const create_meeting_type = "INSERT INTO MEETING TYPE (TYPE) VALUES $1";
export const get_all_meeting_types = "SELECT TYPE FROM MEETING_TYPE";
export const delete_meeting_type = "DELETE FROM MEETING TYPE WHERE TYPE = $1";