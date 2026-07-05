-- TODO: 65625 is the current company average, typed in by hand. The moment
-- someone's salary changes, this number is wrong. Replace the hardcoded 60000
-- with a scalar subquery that computes the average: (SELECT AVG(salary) FROM employee).
SELECT first_name, salary
FROM employee
WHERE salary > 60000
ORDER BY salary DESC;
