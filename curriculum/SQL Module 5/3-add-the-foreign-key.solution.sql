-- employee.branch_id is now a foreign key into branch. The database will refuse
-- any employee whose branch_id isn't a real branch_id already in the branch
-- table — referential integrity, enforced.

CREATE TABLE branch (
  branch_id   INTEGER PRIMARY KEY,
  branch_name TEXT NOT NULL
);

CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  branch_id   INTEGER,
  FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);
