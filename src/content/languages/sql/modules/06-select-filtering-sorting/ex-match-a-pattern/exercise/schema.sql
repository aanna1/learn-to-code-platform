-- The Dunder Mifflin employee table is seeded for you — eight employees across
-- three branches, with one (Ryan) not yet assigned a branch. Leave this block as
-- is; write your query at the bottom and press Run to fill the results grid.
CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  branch_id   INTEGER,
  salary      INTEGER,
  hire_date   TEXT
);
INSERT INTO employee (employee_id, first_name, last_name, branch_id, salary, hire_date) VALUES
  (100, 'Jan',     'Levinson', 1,    110000, '2004-03-15'),
  (101, 'Michael', 'Scott',    2,    90000,  '2005-03-24'),
  (102, 'Dwight',  'Schrute',  2,    62000,  '2005-04-01'),
  (103, 'Jim',     'Halpert',  2,    60000,  '2006-01-10'),
  (104, 'Pam',     'Beesly',   2,    42000,  '2006-05-08'),
  (105, 'Andy',    'Bernard',  3,    55000,  '2007-09-20'),
  (106, 'Stanley', 'Hudson',   2,    58000,  '2004-11-02'),
  (107, 'Ryan',    'Howard',   NULL, 48000,  '2007-06-01');
