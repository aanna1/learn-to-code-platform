-- TODO: this SHOULD list the non-managers, but it returns ZERO rows. The reason:
-- branch.mgr_id contains a NULL (Buffalo), and comparing anything to NULL is
-- UNKNOWN, so NOT IN is never true for anyone. Fix it by keeping NULLs out of the
-- subquery: add WHERE mgr_id IS NOT NULL inside the parentheses.
SELECT first_name
FROM employee
WHERE employee_id NOT IN (SELECT mgr_id FROM branch)
ORDER BY employee_id;
