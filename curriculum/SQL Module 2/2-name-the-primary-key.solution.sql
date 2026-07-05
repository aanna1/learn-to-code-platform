-- student_id is the primary key: guaranteed unique for every row. Adding it
-- makes the two Jacks distinguishable — 1 vs 4 — even though every other
-- column matches.
SELECT student_id, name, major FROM students;
