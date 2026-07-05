-- The assignment table IS the resolved many-to-many: one row per pairing.
-- Michael (101) appears twice — he's on both projects — and project 1 appears
-- twice — it has two employees. That's the "many on both sides" a single
-- foreign key could never store. Notice too that assigned_date and hours live
-- here: they're facts about the PAIRING, not about the employee or project alone.
SELECT * FROM assignment;
