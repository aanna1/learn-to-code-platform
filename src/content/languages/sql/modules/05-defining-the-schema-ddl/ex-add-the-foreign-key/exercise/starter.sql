-- branch is finished. Give employee its foreign key so branch_id can only hold a
-- branch that actually exists.
--
-- TODO: add FOREIGN KEY (branch_id) REFERENCES branch(branch_id) to employee.

CREATE TABLE branch (
  branch_id   INTEGER PRIMARY KEY,
  branch_name TEXT NOT NULL
);

CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  branch_id   INTEGER
  -- missing: FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);
