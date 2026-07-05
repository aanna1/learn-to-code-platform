SELECT branch_id FROM employee
UNION
SELECT branch_id FROM branch
ORDER BY branch_id;
