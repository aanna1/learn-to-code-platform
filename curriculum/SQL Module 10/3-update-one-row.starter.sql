-- This sets branch_id = 3 for EVERY employee, because it has no WHERE.
-- Add a WHERE so only Ryan (employee 107) is changed, then Submit.
UPDATE employee
SET branch_id = 3;
