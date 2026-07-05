-- Just the two columns that make up the composite primary key. Look down
-- either column alone: employee_id 101 appears twice, project_id 1 appears
-- twice — neither is unique on its own. Only the PAIR is. That's why removing
-- either parent would leave an assignment row with no identity: identifying.
SELECT employee_id, project_id FROM assignment;
