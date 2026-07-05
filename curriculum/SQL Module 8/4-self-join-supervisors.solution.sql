SELECT e.first_name AS employee, s.first_name AS supervisor
FROM employee e
JOIN employee s ON e.supervisor_id = s.employee_id
ORDER BY e.employee_id;
