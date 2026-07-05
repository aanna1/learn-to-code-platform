-- TODO: this only shows branch_id, a number. Join to `branch` so the grid
-- shows the branch's actual name instead.
SELECT e.first_name, e.last_name, e.branch_id
FROM employee e
ORDER BY e.employee_id;
