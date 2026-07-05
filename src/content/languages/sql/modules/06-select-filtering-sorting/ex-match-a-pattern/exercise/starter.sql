-- TODO: add the % wildcard so this matches last names that START WITH S,
-- not last names that are exactly the letter S.
SELECT first_name, last_name FROM employee WHERE last_name LIKE 'S';
