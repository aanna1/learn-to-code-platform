SELECT COUNT(*) AS headcount,
       SUM(salary) AS total_payroll,
       AVG(salary) AS avg_salary,
       MIN(salary) AS lowest,
       MAX(salary) AS highest
FROM employee;
