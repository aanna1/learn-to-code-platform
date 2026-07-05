-- This returns the company-wide average salary -- one number, for everybody.
-- TODO: group by branch_id so you get one row PER branch, with that branch's
-- headcount and average salary. Select branch_id, COUNT(*) AS headcount, and
-- AVG(salary) AS avg_salary.
SELECT AVG(salary) AS avg_salary FROM employee;
