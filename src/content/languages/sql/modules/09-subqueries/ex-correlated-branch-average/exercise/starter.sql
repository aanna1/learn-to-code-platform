-- TODO: this compares each person to the COMPANY-wide average, so it returns Jan
-- and Michael. You want each person compared to the average of THEIR OWN branch.
-- Make the subquery correlated: filter it to the outer row's branch with
-- WHERE x.branch_id = e.branch_id.
SELECT first_name, salary, branch_id
FROM employee e
WHERE salary > (SELECT AVG(salary) FROM employee x)
ORDER BY employee_id;
