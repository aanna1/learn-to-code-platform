SELECT e.first_name, b.branch_name
FROM employee e
LEFT JOIN branch b ON e.branch_id = b.branch_id
ORDER BY e.employee_id;
