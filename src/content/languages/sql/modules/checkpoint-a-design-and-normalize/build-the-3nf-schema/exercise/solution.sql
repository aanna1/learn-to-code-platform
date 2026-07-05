-- The normalized 3NF schema: each fact stored once, in its own table, with keys
-- and foreign keys wiring the design together. This is the ERD from Part 1, built.

CREATE TABLE student (
  student_id    INTEGER PRIMARY KEY,
  student_name  TEXT NOT NULL,
  student_email TEXT
);

CREATE TABLE department (
  dept_id       INTEGER PRIMARY KEY,
  dept_name     TEXT NOT NULL,
  dept_building TEXT
);

CREATE TABLE course (
  course_id    INTEGER PRIMARY KEY,
  course_title TEXT NOT NULL,
  dept_id      INTEGER,
  FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

CREATE TABLE enrollment (
  student_id INTEGER,
  course_id  INTEGER,
  grade      TEXT,
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES student(student_id),
  FOREIGN KEY (course_id)  REFERENCES course(course_id)
);
