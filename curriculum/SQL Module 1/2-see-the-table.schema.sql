-- The students table is already set up for you. You don't need to change
-- anything up here — just edit the query at the bottom, then press Run to see
-- the results grid fill in.
CREATE TABLE students (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL,
  major TEXT NOT NULL
);
INSERT INTO students (id, name, major) VALUES
  (1, 'Ada',       'Computer Science'),
  (2, 'Grace',     'Mathematics'),
  (3, 'Alan',      'Computer Science'),
  (4, 'Katherine', 'Physics'),
  (5, 'Dorothy',   'Chemistry');
