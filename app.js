const express = require('express');
const db = require('./db/db.js');


const app = express();
const port = process.env.PORT || 8000;

app.get('/test', (req, res) => res.send('Hello! This is the FAMNM Backend.'));
app.get('/meeting_types', async (req, res) => {
	db.get_all_meeting_types()
	.then(rows => {
		res.send(rows);
	})
	.catch(e => {
		res.status(500).send({error: 'something went wrong.', object: e});
	});
});

app.listen(port, () => console.log(`app listening at https:\/\/localhost:${port}!`))

