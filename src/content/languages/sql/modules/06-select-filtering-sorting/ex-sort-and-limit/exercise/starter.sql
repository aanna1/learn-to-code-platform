-- The sort is right, but this returns all eight employees.
-- TODO: keep only the top 3 by adding LIMIT 3 at the end.
SELECT first_name, salary FROM employee ORDER BY salary DESC;
