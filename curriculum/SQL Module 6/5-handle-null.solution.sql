-- IS NULL is the only way to test for a missing value. This finds Ryan, whose
-- branch hasn't been assigned yet.
SELECT first_name FROM employee WHERE branch_id IS NULL;
