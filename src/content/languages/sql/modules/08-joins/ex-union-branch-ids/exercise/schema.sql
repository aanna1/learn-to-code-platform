CREATE TABLE branch (
  branch_id   INTEGER PRIMARY KEY,
  branch_name TEXT NOT NULL,
  mgr_id      INTEGER
);

CREATE TABLE employee (
  employee_id   INTEGER PRIMARY KEY,
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  branch_id     INTEGER,
  salary        INTEGER,
  hire_date     TEXT,
  supervisor_id INTEGER
);

INSERT INTO branch (branch_id, branch_name, mgr_id) VALUES
  (1, 'Corporate', 100),
  (2, 'Scranton', 101),
  (3, 'Stamford', 105),
  (4, 'Buffalo', NULL);

INSERT INTO employee (employee_id, first_name, last_name, branch_id, salary, hire_date, supervisor_id) VALUES
  (100, 'Jan', 'Levinson', 1, 110000, '2004-03-15', NULL),
  (101, 'Michael', 'Scott', 2, 90000, '2005-03-24', 100),
  (102, 'Dwight', 'Schrute', 2, 62000, '2005-04-01', 101),
  (103, 'Jim', 'Halpert', 2, 60000, '2006-01-10', 101),
  (104, 'Pam', 'Beesly', 2, 42000, '2006-05-08', 101),
  (105, 'Andy', 'Bernard', 3, 55000, '2007-09-20', 100),
  (106, 'Stanley', 'Hudson', 2, 58000, '2004-11-02', 101),
  (107, 'Ryan', 'Howard', NULL, 48000, '2007-06-01', 101);
