CREATE TABLE branch (
  branch_id   INTEGER PRIMARY KEY,
  branch_name TEXT NOT NULL,
  mgr_id      INTEGER
);

CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  branch_id   INTEGER,
  salary      INTEGER
);

INSERT INTO branch (branch_id, branch_name, mgr_id) VALUES
  (1, 'Corporate', 100),
  (2, 'Scranton', 101),
  (3, 'Stamford', 105),
  (4, 'Buffalo', NULL);

INSERT INTO employee (employee_id, first_name, last_name, branch_id, salary) VALUES
  (100, 'Jan', 'Levinson', 1, 110000),
  (101, 'Michael', 'Scott', 2, 90000),
  (102, 'Dwight', 'Schrute', 2, 62000),
  (103, 'Jim', 'Halpert', 2, 60000),
  (104, 'Pam', 'Beesly', 2, 42000),
  (105, 'Andy', 'Bernard', 3, 55000),
  (106, 'Stanley', 'Hudson', 2, 58000),
  (107, 'Ryan', 'Howard', NULL, 48000);
