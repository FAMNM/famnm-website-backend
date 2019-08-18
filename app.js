const express = require('express');
const db = require('./db.js');


const app = express();
const port = process.env.PORT || 8000;

app.get('/test', (req, res) => res.send('Hello! This is the FAMNM Backend.'))
app.get('/meeting_types', (req, res) => {
	const { rows } = await db.meeting_types();
	res.send(rows);
}


app.listen(port, () => console.log(`app listening at https:\/\/localhost:${port}!`))

