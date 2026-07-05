SELECT branch_name
FROM branch b
WHERE NOT EXISTS (SELECT 1 FROM employee e WHERE e.branch_id = b.branch_id)
ORDER BY branch_id;
