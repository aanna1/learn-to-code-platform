SELECT first_name
FROM employee
WHERE employee_id NOT IN (SELECT mgr_id FROM branch WHERE mgr_id IS NOT NULL)
ORDER BY employee_id;
