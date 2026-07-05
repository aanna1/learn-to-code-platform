-- Disaster: a no-WHERE UPDATE set every salary to 0. But it's inside an open
-- transaction and NOT committed yet. Add one line to undo it, then Submit.
BEGIN;
UPDATE employee SET salary = 0;
