-- Now the redundancy is impossible to miss: "Michael" is copied onto three
-- rows and "Scranton" onto all four. Change how Scranton's city is spelled and
-- you must fix every one of those rows — miss one and the database disagrees
-- with itself. That's the update anomaly. Normalization's job is to store each
-- of those facts exactly once, in its own table.
SELECT product, emp_name, branch_city FROM orders;
