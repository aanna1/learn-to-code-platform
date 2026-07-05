-- This raises EVERY employee's salary, not just Scranton's, because it has no WHERE.
-- Restrict it to branch 2, then Submit.
UPDATE employee
SET salary = salary + 3000;
