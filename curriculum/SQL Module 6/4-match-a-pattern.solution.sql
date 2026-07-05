-- 'S%' is a prefix match: an S followed by any run of characters. That catches
-- Scott and Schrute.
SELECT first_name, last_name FROM employee WHERE last_name LIKE 'S%';
