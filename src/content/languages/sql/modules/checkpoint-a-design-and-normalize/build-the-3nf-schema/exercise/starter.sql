-- Build the normalized 3NF schema for the registrar's data. Two tables are done
-- for you as a pattern; finish the other two.
--
-- TODO: course must have a FOREIGN KEY on dept_id referencing department.
-- TODO: enrollment must have the COMPOSITE primary key (student_id, course_id)
--       and FOREIGN KEYs to both student and course.

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
  dept_id      INTEGER
  -- missing: FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

CREATE TABLE enrollment (
  student_id INTEGER PRIMARY KEY,   -- wrong: this should be a COMPOSITE key
  course_id  INTEGER,
  grade      TEXT
  -- missing: the composite PRIMARY KEY and both FOREIGN KEYs
);
