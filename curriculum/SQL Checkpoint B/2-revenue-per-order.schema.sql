CREATE TABLE customer (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT
);

CREATE TABLE product (
  product_id INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  price      REAL NOT NULL
);

CREATE TABLE sales_order (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,
  order_date  TEXT,
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE order_item (
  order_id   INTEGER,
  product_id INTEGER,
  quantity   INTEGER NOT NULL,
  FOREIGN KEY (order_id) REFERENCES sales_order(order_id),
  FOREIGN KEY (product_id) REFERENCES product(product_id)
);

INSERT INTO customer (customer_id, name, city) VALUES
  (1, 'Alice', 'Scranton'),
  (2, 'Bob', 'Scranton'),
  (3, 'Carol', 'Stamford'),
  (4, 'Dave', 'Buffalo');

INSERT INTO product (product_id, name, price) VALUES
  (10, 'Widget', 5.00),
  (11, 'Gadget', 12.50),
  (12, 'Gizmo', 8.00),
  (13, 'Doohickey', 20.00);

INSERT INTO sales_order (order_id, customer_id, order_date) VALUES
  (100, 1, '2024-01-05'),
  (101, 1, '2024-02-10'),
  (102, 2, '2024-01-20'),
  (103, 3, '2024-03-01');

INSERT INTO order_item (order_id, product_id, quantity) VALUES
  (100, 10, 2),
  (100, 11, 1),
  (101, 12, 3),
  (102, 10, 5),
  (103, 11, 2),
  (103, 12, 1);
