const { Client } = require('pg');

const client = new Client({
	connectionString: process.env.DATABASE_URL,
	ssl: true,
});


module.exports = {
	meeting_types: () => {
		client.connect();
		client.query('SELECT * FROM MEETING_TYPE;', (err, res) => {
			client.end();
			if (err) throw err;
			return res;
		});
	}
}
