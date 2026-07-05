-- The full employee table -- salary and all. HR may see salary; a team lead
-- browsing the directory must not. Same table, different windows onto it.
CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT,
  last_name   TEXT,
  branch_id   INTEGER,
  salary      INTEGER
);

INSERT INTO employee (employee_id, first_name, last_name, branch_id, salary) VALUES
  (100, 'Jan',     'Levinson', 1,    110000),
  (101, 'Michael', 'Scott',    2,    90000),
  (102, 'Dwight',  'Schrute',  2,    62000),
  (103, 'Jim',     'Halpert',  2,    60000),
  (104, 'Pam',     'Beesly',   2,    42000),
  (105, 'Andy',    'Bernard',  3,    55000),
  (106, 'Stanley', 'Hudson',   2,    58000),
  (107, 'Ryan',    'Howard',   NULL, 48000);
