-- Add the three constraints so this table only ever holds valid rows.
--
-- TODO: student_id should be the PRIMARY KEY.
-- TODO: name must be NOT NULL.
-- TODO: major should DEFAULT to 'undecided'.

CREATE TABLE student (
  student_id INTEGER,
  name       TEXT,
  major      TEXT
);
