-- Remove just Ryan (employee 107). The WHERE is what keeps this from
-- emptying the entire table.
DELETE FROM employee
WHERE employee_id = 107;
