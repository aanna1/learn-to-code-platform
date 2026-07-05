SELECT first_name, salary, branch_id
FROM employee e
WHERE salary > (SELECT AVG(salary)
               FROM employee x
               WHERE x.branch_id = e.branch_id)
ORDER BY employee_id;
