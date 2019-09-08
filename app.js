const express = require('express');
const db = require('./db/db.js');


const app = express();
const port = process.env.PORT || 8000;

function getRequest(getfunction, res, data) {
	var func = null;
	if (data) {
		func = getfunction(data);
	} else {
		func = getfunction();
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

app.get('/meeting_types', async (req, res) => {
	getRequest(db.get_all_meeting_types, res);
});

/*
************
* MEETINGS *
************
*/

app.get('/get_all_meetings', async (req, res) => {
	getRequest(db.get_all_meetings, res);
});

app.get('/get_meetings_on_day', async(req, res) => {
	getRequest(db.get_meetings_on_day, res, Date.parse(req.query.day));
});

app.get('/get_meetings_within_day_range', async(req, res) => {
	getRequest(db.get_meetings_within_day_range, res, [Date.parse(req.query.start), Date.parse(req.query.end)]);
});
/*
**************
* ATTENDANCE *
**************
*/

/*
***
GET
***
get_meetings_of_type
get_attendance_for_uniqname
get_attendance_for_meeting

***
POST
***
create_meeting_type
create_meeting
create_attendance_entry


***
PUT
***
update_meeting


***
DELETE
***
delete_meeting_type
delete_meeting
delete_attendance_entry

*/
app.listen(port, () => console.log(`app listening at https:\/\/localhost:${port}!`))

