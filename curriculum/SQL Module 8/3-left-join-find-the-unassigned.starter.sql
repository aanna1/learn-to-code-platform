-- TODO: this drops Ryan because he has no branch_id. Switch to a join that
-- keeps every employee, matched or not.
SELECT e.first_name, b.branch_name
FROM employee e
JOIN branch b ON e.branch_id = b.branch_id
ORDER BY e.employee_id;
