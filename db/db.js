const { Pool } = require('pg');
const meetings = require('./meetings.js');
const meeting_types = require('./meeting_types.js');

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
	get_all_meeting_types: () => {
		return this.query({text: meeting_types.get_all_meeting_types});
	},
	create_meeting: (new_meeting) => {
		return this.query({text: meetings.create_meeting, values: new_meeting});
	},
	get_all_meetings: () => {
		return this.query({text: meetings.get_all_meetings});
	},
	get_meetings_on_day: (day) => {
		return this.query({text: meetings.get_meetings_on_day, values: [day]});
	},
	get_meetings_within_day_range: (days) => {
		return this.query({text: meetings.get_meetings_within_day_range, values: days});
	},
	get_meetings_of_type: (type) => {
		return this.query({text: meetings.get_meetings_of_type, values: [type]});
	},
	update_meeting: (new_info) => {
		return this.query({text: meetings.update_meeting, values: new_info});
	},
	delete_meeting: (id) => {
		return this.query({text: meetings.delete_meeting, values: [id]});
	},
}
