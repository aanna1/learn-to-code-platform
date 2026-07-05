-- This view has no WHERE, so it exposes the WHOLE company -- every branch.
-- Add a WHERE so the view shows only the Scranton branch (branch_id = 2).
CREATE VIEW scranton_roster AS
SELECT first_name, last_name, branch_id
FROM employee;

SELECT * FROM scranton_roster;
