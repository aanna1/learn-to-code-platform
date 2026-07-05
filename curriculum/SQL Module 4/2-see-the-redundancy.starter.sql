-- This shows the products, but hides the problem. The redundancy the lecture
-- warned about is in the emp_name and branch_city columns — you can't see it
-- until you put them on the grid.
-- TODO: return product, emp_name, and branch_city (in that order) so the
-- duplication is visible line by line.
SELECT product FROM orders;
