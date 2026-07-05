-- This view exposes EVERYTHING, salary included -- SELECT * copies every column,
-- so it's no boundary at all. Redefine it to select only the safe columns
-- (employee_id, first_name, last_name, branch_id) so salary is unreachable.
CREATE VIEW employee_public AS
SELECT * FROM employee;

SELECT * FROM employee_public;
