-- One denormalized table is set up for you: orders. You don't need to change
-- anything up here — just edit the query at the bottom, then press Run.
-- This is the "one table that does too much" from the lecture: each row is a
-- single product on an order, but the employee's name and the branch's city are
-- copied onto every line instead of living once in their own tables.
CREATE TABLE orders (
  order_id    INTEGER,
  product     TEXT NOT NULL,
  qty         INTEGER NOT NULL,
  emp_name    TEXT NOT NULL,
  branch_city TEXT NOT NULL,
  PRIMARY KEY (order_id, product)
);
INSERT INTO orders (order_id, product, qty, emp_name, branch_city) VALUES
  (1001, 'Paper',   10, 'Michael', 'Scranton'),
  (1001, 'Toner',    2, 'Michael', 'Scranton'),
  (1002, 'Stapler',  1, 'Michael', 'Scranton'),
  (1003, 'Paper',    5, 'Angela',  'Scranton');
