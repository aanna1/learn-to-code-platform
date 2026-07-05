-- TODO: this lists everyone. Keep only the employees who are branch managers.
-- The manager IDs live in branch.mgr_id — test membership with
-- WHERE employee_id IN (SELECT mgr_id FROM branch).
SELECT first_name, last_name
FROM employee
ORDER BY employee_id;
