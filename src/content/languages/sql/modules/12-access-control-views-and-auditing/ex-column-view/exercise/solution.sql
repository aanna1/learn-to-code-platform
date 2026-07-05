-- The view names only the safe columns, so salary is simply not part of it.
-- Grant SELECT on employee_public (and revoke it on employee) and a user can
-- read names and branches but can never reach salary through this window.
CREATE VIEW employee_public AS
SELECT employee_id, first_name, last_name, branch_id
FROM employee;

SELECT * FROM employee_public;
