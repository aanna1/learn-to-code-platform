-- Two tables are set up for you: the normalized branch table, and an orders
-- table that points at it. You don't need to change anything up here — just
-- edit the query at the bottom, then press Run.
-- This is the AFTER picture: each branch's city is stored exactly once, in the
-- branch table. The orders table only stores a branch_id pointing at it, so no
-- order ever repeats a city. Compare this to the redundant table in the
-- previous exercise.
CREATE TABLE branch (
  branch_id INTEGER PRIMARY KEY,
  city      TEXT NOT NULL
);
INSERT INTO branch (branch_id, city) VALUES
  (1, 'Corporate'),
  (2, 'Scranton'),
  (3, 'Stamford');

CREATE TABLE orders (
  order_id  INTEGER PRIMARY KEY,
  product   TEXT NOT NULL,
  branch_id INTEGER,
  FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);
INSERT INTO orders (order_id, product, branch_id) VALUES
  (1001, 'Paper',   2),
  (1002, 'Stapler', 2),
  (1003, 'Toner',   3);
