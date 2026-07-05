-- This grabs every column, including assigned_date and hours you don't need
-- right now. Pulling more than you need is a habit worth breaking early.
-- TODO: return ONLY the two columns that together form the identifying
-- composite key: employee_id and project_id, in that order.
SELECT * FROM assignment;
