-- TODO: also require salary > 55000, so only the higher earners in Scranton
-- come back. Right now Pam (42000) is still included.
SELECT first_name, salary FROM employee WHERE branch_id = 2;
