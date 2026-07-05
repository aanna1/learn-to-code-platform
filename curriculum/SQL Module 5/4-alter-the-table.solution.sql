-- Both new columns added to the existing student table, without rebuilding it or
-- disturbing the rows already there.

ALTER TABLE student ADD COLUMN gpa DECIMAL(3, 2);
ALTER TABLE student ADD COLUMN email TEXT;
