-- This runs without error but returns NOTHING: = NULL is never true for any row.
-- TODO: change = NULL to IS NULL.
SELECT first_name FROM employee WHERE branch_id = NULL;
