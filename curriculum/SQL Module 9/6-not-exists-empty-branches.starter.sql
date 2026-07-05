-- TODO: "branches with no employees." Written as NOT IN, this returns ZERO rows,
-- because employee.branch_id contains a NULL (Ryan) and NOT IN breaks on NULLs.
-- Rewrite it as NOT EXISTS with a correlated subquery, which checks presence row
-- by row and can't be poisoned by a NULL.
SELECT branch_name
FROM branch
WHERE branch_id NOT IN (SELECT branch_id FROM employee)
ORDER BY branch_id;
