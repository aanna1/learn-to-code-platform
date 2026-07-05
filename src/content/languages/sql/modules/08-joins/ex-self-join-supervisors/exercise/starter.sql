-- TODO: this joins each employee to THEMSELVES (same id on both sides), so
-- "supervisor" always comes out equal to "employee". Match on supervisor_id
-- instead so s is the actual supervisor.
SELECT e.first_name AS employee, s.first_name AS supervisor
FROM employee e
JOIN employee s ON e.employee_id = s.employee_id
ORDER BY e.employee_id;
