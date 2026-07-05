SELECT branch_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employee
GROUP BY branch_id;
