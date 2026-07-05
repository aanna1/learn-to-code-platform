-- Everyone in Scranton (branch 2) gets a 3000 raise.
-- salary = salary + 3000 computes the new value from each row's own old salary.
UPDATE employee
SET salary = salary + 3000
WHERE branch_id = 2;
