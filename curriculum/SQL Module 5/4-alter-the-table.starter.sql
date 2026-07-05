-- Add the two new columns to student. The first one is done as a pattern.
--
-- TODO: add an email column of type TEXT with a second ALTER TABLE statement.

ALTER TABLE student ADD COLUMN gpa DECIMAL(3, 2);
