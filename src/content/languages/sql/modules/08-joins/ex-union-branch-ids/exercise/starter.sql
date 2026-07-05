-- TODO: this keeps every duplicate (branch_id 2 appears 5 times from
-- employee alone). Switch to the set operator that removes duplicates.
SELECT branch_id FROM employee
UNION ALL
SELECT branch_id FROM branch
ORDER BY branch_id;
