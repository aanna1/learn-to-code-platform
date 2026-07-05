-- This query returns just name and major — so the two Jacks come back as two
-- identical rows you can't tell apart.
-- TODO: also return the primary key column (student_id) so each row is
-- uniquely identifiable. Return student_id, name, and major.
SELECT name, major FROM students;
