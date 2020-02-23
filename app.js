const express = require('express');
const cors = require('cors');
const db = require('./db/db.js');
const stringify = require('csv-stringify');

var corsOptions = {
	origin: 'https://famnm.club',
	optionsSuccessStatus: 200 // some legacy browsers (IE11, various SmartTVs) choke on 204
}


const app = express();
app.use(express.json());

if (process.env.CORS_ENABLED == "TEST")
{
	app.use(cors());
} else if (process.env.CORS_ENABLED == "TRUE") {
	app.use(cors(corsOptions));
}

const port = process.env.PORT || 8000;

function dbRequest(fn, res, data) {
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

function parseDate(dateString) {
	return new Date(parseInt(dateString));
}

app.get('/', (req, res) => res.send('Hello World! This is the FAMNM Backend.'));

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
	dbRequest(db.get_meeting_with_id, res, req.params.meetingId);
});

app.get('/meeting', async (req, res) => {
	dbRequest(db.get_all_meetings, res);
});

// ANYBODY MAKING REQUESTS MUST USE Date.getTime();

app.get('/meeting/day/:meetingDay', async(req, res) => {
	dbRequest(db.get_meetings_on_day, res, parseDate(req.params.meetingDay));
});

app.get('/meeting/start/:startDay/end/:endDay', async(req, res) => {
	dbRequest(db.get_meetings_within_day_range, res, [parseDate(req.params.startDay),
													  parseDate(req.params.endDay)]);
});

app.get('/meeting/type/:meetingType', async(req, res) => {
	dbRequest(db.get_meetings_of_type, res, req.params.meetingType);
});

app.post('/meeting', async(req, res) => {
	dbRequest(db.create_meeting, res, [req.body.meetingType, 
									   parseDate(req.body.meetingDay),
									   req.body.startTime,
									   req.body.endTime,
									   req.body.description]);
});

// time is a string, in 24 hour time, e.g. 15:04. HH:MM.

app.put('/meeting', async(req, res) => {
	dbRequest(db.update_meeting, res, [req.body.meetingType,
									   parseDate(req.body.meetingDay),
									   req.body.startTime,
									   req.body.endTime,
									   req.body.description,
									   req.body.meetingId]);
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

app.get('/attendance/active', async (req, res) => {
	dbRequest(db.get_active_member_uniqnames, res);
});

app.post('/attendance', async(req, res) => {
	dbRequest(db.create_attendance_entry, res, [req.body.uniqname, req.body.meetingId]);
});

app.delete('/attendance', async(req, res) => {
	dbRequest(db.delete_attendance_entry, res, [req.body.uniqname, req.body.meetingId]);
});

/*
**************
* CSV EXPORT *
**************
*/
app.get('/export', async(req, res) => {
	db.get_csv_export_data()
	.then(rows => {
		for (let i = 0; i < rows.length; ++i)
			rows[i].date = new Date(rows[i].date).toDateString();
		return rows;
	})
	.then(rows => {
		res.setHeader('Content-Type', 'text/csv');
		res.setHeader('Content-Disposition', 'attachment; filename=\"' + 'famnm-attendance-' + Date.now() + '.csv\"');
		res.setHeader('Cache-Control', 'no-cache');
		res.setHeader('Pragma', 'no-cache');

		stringify(rows, { header: true })
		.pipe(res);
	})
	.catch(console.log);
})

app.listen(port, () => console.log(`app listening at http:\/\/localhost:${port}!`))

