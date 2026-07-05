-- Two tables are set up for you: branch, and employee. You don't need to change
-- anything up here — just edit the query at the bottom, then press Run.
-- Each employee's branch_id is a FOREIGN KEY: it stores a branch's primary key,
-- which is how an employee row points at the branch they work in.
CREATE TABLE branch (
  branch_id INTEGER PRIMARY KEY,
  name      TEXT NOT NULL
);
INSERT INTO branch (branch_id, name) VALUES
  (1, 'Corporate'),
  (2, 'Scranton'),
  (3, 'Stamford');

CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  branch_id   INTEGER,
  FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);
INSERT INTO employee (employee_id, first_name, branch_id) VALUES
  (100, 'Jan',     1),
  (101, 'Michael', 2),
  (102, 'Andy',    3);
