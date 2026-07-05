-- The students table is already set up for you. You don't need to change
-- anything up here — just edit the query at the bottom, then press Run to see
-- the results grid fill in. Notice rows 1 and 4: two different students who
-- happen to share a name AND a major.
CREATE TABLE students (
  student_id INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  major      TEXT NOT NULL
);
INSERT INTO students (student_id, name, major) VALUES
  (1, 'Jack',   'Biology'),
  (2, 'Kate',   'Sociology'),
  (3, 'Claire', 'English'),
  (4, 'Jack',   'Biology');
