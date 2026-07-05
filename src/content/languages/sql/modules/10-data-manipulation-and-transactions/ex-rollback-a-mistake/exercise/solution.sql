-- A transaction is already open and a no-WHERE UPDATE has zeroed every salary.
-- Nothing is committed yet, so throw the whole thing away with ROLLBACK.
BEGIN;
UPDATE employee SET salary = 0;
ROLLBACK;
