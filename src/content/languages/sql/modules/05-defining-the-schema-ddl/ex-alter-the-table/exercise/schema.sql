-- The student table already exists. This is the schema you're altering — leave it
-- as is and add your ALTER TABLE statements below it.
CREATE TABLE student (
  student_id INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  major      TEXT DEFAULT 'undecided'
);
