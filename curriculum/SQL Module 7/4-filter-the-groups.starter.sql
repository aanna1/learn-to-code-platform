-- This lists every branch's headcount -- including branches with just one
-- person, which is a privacy problem: a one-person "average" IS that
-- person's exact salary.
-- TODO: add a HAVING clause so only branches with MORE THAN ONE employee are
-- reported.
SELECT branch_id, COUNT(*) AS headcount
FROM employee
GROUP BY branch_id;
