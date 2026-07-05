SELECT first_name, last_name
FROM employee
WHERE employee_id IN (SELECT mgr_id FROM branch)
ORDER BY employee_id;
