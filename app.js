const express = require('express');
const db = require('./db/db.js');


const app = express();
app.use(express.json());

const port = process.env.PORT || 8000;

function dbRequest(fn, res, data) {
	console.log("data to send to db: " + JSON.stringify(data));
	var func = null;
	if (data) {
		func = fn(data);
	} else {
		func = fn();
	}
	func.then(rows => {
		res.send(rows);
	}).catch(e => {
		res.status(500).send({error: 'something went wrong.', object: e});
	});
}

app.get('/test', (req, res) => res.send('Hello! This is the FAMNM Backend. Pls no DDOS.'));

/*
*****************
* MEETING TYPES *
*****************
*/

app.get('/meeting_type', async (req, res) => {
	dbRequest(db.get_all_meeting_types, res);
});

app.post('/meeting_type', async(req, res) => {
	dbRequest(db.create_meeting_type, res, req.body.meetingType);
});

app.delete('/meeting_type', async(req, res) => {
	dbRequest(db.delete_meeting_type, res, req.body.meetingType);
});

/*
************
* MEETINGS *
************
*/
app.get('/meeting/:meetingId', async (req, res) => {
	dbRequest(db.get_all_meetings, res, req.params.meetingId);
});

app.get('/meeting', async (req, res) => {
	dbRequest(db.get_all_meetings, res);
});

// ANYBODY MAKING REQUESTS MUST USE Date.getTime();

app.get('/meeting/day/:meetingDay', async(req, res) => {
	dbRequest(db.get_meetings_on_day, res, new Date(req.params.meetingDay));
});

app.get('/meeting/start/:startDay/end/:endDay', async(req, res) => {
	dbRequest(db.get_meetings_within_day_range, res, [new Date(req.params.startDay), new Date(req.params.endDay)]);
});

app.get('/meeting/type/:meetingType', async(req, res) => {
	dbRequest(db.get_meetings_of_type, res, req.params.meetingType);
});

app.post('/meeting', async(req, res) => {
	dbRequest(db.create_meeting, res, [req.body.meetingType, new Date(req.body.meetingDay), req.body.startTime, req.body.endTime, req.body.description]);
});

// time is a string, in 24 hour time, e.g. 15:04. HH:MM.

app.put('/meeting', async(req, res) => {
	dbRequest(db.update_meeting, res, [req.body.meetingType, new Date(req.body.meetingDay), req.body.startTime, req.body.endTime, req.body.description, req.body.meetingId]);
});

app.delete('/meeting', async(req, res) => {
	dbRequest(db.delete_meeting, res, req.body.meetingId);
});


/*
**************
* ATTENDANCE *
**************
*/
app.get('/attendance/uniqname/:uniqname', async(req, res) => {
	dbRequest(db.get_attendance_for_uniqname, res, req.params.uniqname);
});

app.get('/attendance/meeting/:meetingId', async(req, res) => {
	dbRequest(db.get_attendance_for_meeting, res, req.params.meetingId);
});

app.post('/attendance', async(req, res) => {
	dbRequest(db.create_attendance_entry, res, [req.body.uniqname, req.body.meetingId]);
});

app.delete('/attendance', async(req, res) => {
	dbRequest(db.delete_attendance_entry, res, [req.body.uniqname, req.body.meetingId]);
});
app.listen(port, () => console.log(`app listening at https:\/\/localhost:${port}!`))

