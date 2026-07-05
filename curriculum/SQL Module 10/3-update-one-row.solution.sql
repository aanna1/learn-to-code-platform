-- Ryan (employee 107) is finally assigned to Stamford (branch 3).
-- The WHERE picks exactly one row — that is the whole point.
UPDATE employee
SET branch_id = 3
WHERE employee_id = 107;
