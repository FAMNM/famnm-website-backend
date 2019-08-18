const { Client } = require('pg');

const client = new Client({
	connectionString: process.env.DATABASE_URL,
	ssl: true,
});


module.exports = {
	meeting_types: () => {
		client.connect();
		var result;
		client.query('SELECT * FROM MEETING_TYPE;', (err, res) => {
			if (err !== null) {
				throw err;
			}
			result = res.rows;
		});
		client.end();
		return result;
	}
}
