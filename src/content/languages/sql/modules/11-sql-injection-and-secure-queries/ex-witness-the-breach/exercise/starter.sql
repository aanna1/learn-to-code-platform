-- This is the query the app builds for a NORMAL login (admin / s3cr3t).
-- It returns exactly one row: the admin. Your job is to rewrite it into
-- the query the app ACCIDENTALLY builds when an attacker types
--     ' OR '1'='1' --
-- into the username box, so that it returns every account instead.
SELECT id, username, role FROM users
WHERE username = 'admin' AND password = 's3cr3t';
