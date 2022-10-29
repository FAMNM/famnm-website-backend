CREATE TABLE meeting_types (
    meeting_type TEXT PRIMARY KEY,
    CONSTRAINT no_default_meeting_type CHECK (meeting_type <> '------')
);

CREATE TABLE members (
    uniqname TEXT PRIMARY KEY,
    mentor BOOLEAN
);

CREATE TABLE meetings (
    meeting_id SERIAL PRIMARY KEY,
    meeting_type TEXT NOT NULL REFERENCES meeting_types(meeting_type) ON DELETE CASCADE,
    meeting_date DATE NOT NULL,
    UNIQUE (meeting_type, meeting_date)
);

CREATE TABLE attendance (
    uniqname TEXT NOT NULL REFERENCES members(uniqname) ON DELETE CASCADE,
    meeting_id INTEGER NOT NULL REFERENCES meetings(meeting_id) ON DELETE CASCADE,
    PRIMARY KEY (uniqname, meeting_id)
);

CREATE TABLE semesters (
    starting_date DATE PRIMARY KEY,
    semester_name TEXT NOT NULL
);
