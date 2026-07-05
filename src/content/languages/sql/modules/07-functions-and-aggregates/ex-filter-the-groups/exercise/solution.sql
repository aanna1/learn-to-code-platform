SELECT branch_id, COUNT(*) AS headcount
FROM employee
GROUP BY branch_id
HAVING COUNT(*) > 1;
