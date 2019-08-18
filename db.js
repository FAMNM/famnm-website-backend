const { Client } = require('pg');

const client = new Client({
	connectionString: process.env.DATABASE_URL,
	ssl: true,
});


module.exports = {
	meeting_types: () => {
		client.connect();
		return client
			.query('SELECT * FROM MEETING_TYPE;')
			.then(res => {
				client.end();
				return res.rows;
			})
			.catch(e => {
				client.end();
				throw e;
			});
	}
}
