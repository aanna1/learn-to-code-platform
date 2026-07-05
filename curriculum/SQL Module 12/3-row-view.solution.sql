-- The WHERE inside the view filters rows the same way it filters columns above.
-- Grant SELECT on this view and a user sees the Scranton team and nothing else --
-- they can't even tell the other branches exist.
CREATE VIEW scranton_roster AS
SELECT first_name, last_name, branch_id
FROM employee
WHERE branch_id = 2;

SELECT * FROM scranton_roster;
