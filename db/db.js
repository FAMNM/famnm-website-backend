const { Pool } = require('pg');
const meetings = require('./meetings.js');
const meeting_types = require('./meeting_types.js');
const attendance = require('./attendance.js');

const pool = new Pool({
	connectionString: process.env.DATABASE_URL,
	ssl: true,
});


module.exports = {
	query: (query) => {
		return pool
			.query(query)
			.then(res => res.rows)
			.catch(e => {
				throw e;
			})
	},
	/*
	*****************
	* MEETING TYPES *
	*****************
	*/
	get_all_meeting_types: () => {
		return module.exports.query({text: meeting_types.get_all_meeting_types});
	},
	create_meeting_type: (type) => {
		return module.exports.query({text: meeting_types.create_meeting_type, values: [type]});
	},
	delete_meeting_type: (type) => {
		return module.exports.query({text: meeting_types.create_meeting_type, values: [type]});
	},
	/*
	************
	* MEETINGS *
	************
	*/
	get_meeting_with_id: (id) => {
		return module.exports.query({text: meetings.get_meeting_with_id, values: [id]});
	},
	get_all_meetings: () => {
		return module.exports.query({text: meetings.get_all_meetings});
	},
	get_meetings_on_day: (day) => {
		return module.exports.query({text: meetings.get_meetings_on_day, values: [day]});
	},
	get_meetings_within_day_range: (days) => {
		return module.exports.query({text: meetings.get_meetings_within_day_range, values: days});
	},
	get_meetings_of_type: (type) => {
		return module.exports.query({text: meetings.get_meetings_of_type, values: [type]});
	},
	create_meeting: (new_meeting) => {
		return module.exports.query({text: meetings.create_meeting, values: new_meeting});
	},
	update_meeting: (new_info) => {
		return module.exports.query({text: meetings.update_meeting, values: new_info});
	},
	delete_meeting: (id) => {
		return module.exports.query({text: meetings.delete_meeting, values: [id]});
	},
	/*
	**************
	* ATTENDANCE *
	**************
	*/
	get_attendance_for_uniqname: (uniqname) => {
		return module.exports.query({text: attendance.get_attendance_for_uniqname, values: [uniqname]});
	},
	get_attendance_for_meeting: (meeting_id) => {
		return module.exports.query({text: attendance.get_attendance_for_meeting, values: [meeting_id]});
	},
	create_attendance_entry: (entry) => {
		return module.exports.query({text: attendance.create_attendance_entry, values: entry});
	},
	delete_attendance_entry: (entry) => {
		return module.exports.query({text: attendance.delete_attendance_entry, values: entry});
	}
}
