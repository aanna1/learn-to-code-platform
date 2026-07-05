-- Three tables are set up for you: employee, project, and the associative
-- entity assignment. You don't need to change anything up here — just edit the
-- query at the bottom, then press Run.
-- An employee can work on many projects, and a project can have many employees.
-- That many-to-many can't live as a single foreign key, so it's resolved into
-- the `assignment` table: each row is ONE employee paired with ONE project.
CREATE TABLE employee (
  employee_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL
);
INSERT INTO employee (employee_id, first_name) VALUES
  (101, 'Michael'),
  (103, 'Angela'),
  (105, 'Kevin');

CREATE TABLE project (
  project_id INTEGER PRIMARY KEY,
  name       TEXT NOT NULL
);
INSERT INTO project (project_id, name) VALUES
  (1, 'Scranton Website'),
  (2, 'Client Audit');

CREATE TABLE assignment (
  employee_id   INTEGER,
  project_id    INTEGER,
  assigned_date TEXT NOT NULL,
  hours         INTEGER NOT NULL,
  PRIMARY KEY (employee_id, project_id),
  FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
  FOREIGN KEY (project_id)  REFERENCES project(project_id)
);
INSERT INTO assignment (employee_id, project_id, assigned_date, hours) VALUES
  (101, 1, '2024-03-03', 40),
  (101, 2, '2024-04-10', 12),
  (103, 1, '2024-03-05', 20),
  (105, 2, '2024-04-11', 8);
