const express = require('express');
const db = require('./db.js');


const app = express();
const port = process.env.PORT || 8000;

app.get('/test', (req, res) => res.send('Hello! This is the FAMNM Backend.'));
app.get('/meeting_types', async (req, res) => {
	try {
		const { rows } = await db.meeting_types();
		res.send(rows);
	} catch (e) {
		res.status(500).send({error: 'something went wrong.'});
	}
});


app.listen(port, () => console.log(`app listening at https:\/\/localhost:${port}!`))

