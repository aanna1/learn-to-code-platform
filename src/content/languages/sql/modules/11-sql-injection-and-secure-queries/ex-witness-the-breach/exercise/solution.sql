-- After the attacker's  ' OR '1'='1' --  is glued into the template, the
-- leading quote closes the empty username, OR '1'='1' is always true, and
-- --  comments out the entire password check. What the database runs is:
SELECT id, username, role FROM users
WHERE username = '' OR '1'='1';
