-- The student table with all three constraints in place: a primary key that
-- identifies each row, a name that can never be empty, and a major that falls
-- back to 'undecided' when none is given.

CREATE TABLE student (
  student_id INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  major      TEXT DEFAULT 'undecided'
);
