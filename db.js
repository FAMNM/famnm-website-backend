const { Pool } = require('pg');

const pool = new Pool({
	connectionString: process.env.DATABASE_URL,
	ssl: true,
});


module.exports = {
	meeting_types: () => {
		return pool
			.query('SELECT * FROM MEETING_TYPE;')
			.then(res => res.rows)
			.catch(e => {
				throw e;
			});
	}
}
