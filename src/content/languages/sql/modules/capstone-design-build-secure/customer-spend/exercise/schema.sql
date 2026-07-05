CREATE TABLE author (
  author_id  INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name  TEXT NOT NULL
);

CREATE TABLE customer (
  customer_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  email       TEXT NOT NULL UNIQUE,
  city        TEXT
);

CREATE TABLE book (
  book_id   INTEGER PRIMARY KEY,
  title     TEXT NOT NULL,
  genre     TEXT,
  price     REAL NOT NULL CHECK (price >= 0),
  author_id INTEGER NOT NULL REFERENCES author(author_id)
);

CREATE TABLE book_order (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customer(customer_id),
  order_date  TEXT NOT NULL
);

CREATE TABLE order_line (
  order_id INTEGER NOT NULL REFERENCES book_order(order_id),
  book_id  INTEGER NOT NULL REFERENCES book(book_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  PRIMARY KEY (order_id, book_id)
);

INSERT INTO author VALUES
 (1,'Ursula','Le Guin'), (2,'George','Orwell'),
 (3,'Toni','Morrison'), (4,'Frank','Herbert'), (5,'Octavia','Butler');

INSERT INTO customer VALUES
 (1,'Maya','Chen','maya@example.com','Portland'),
 (2,'Devon','Park','devon@example.com','Seattle'),
 (3,'Sara','Okafor','sara@example.com','Portland'),
 (4,'Leo','Martin','leo@example.com','Boise');

INSERT INTO book VALUES
 (1,'A Wizard of Earthsea','Fantasy',12.00,1),
 (2,'The Left Hand of Darkness','SciFi',14.00,1),
 (3,'1984','Dystopia',10.00,2),
 (4,'Animal Farm','Satire',9.00,2),
 (5,'Beloved','Literary',13.00,3),
 (6,'Dune','SciFi',18.00,4),
 (7,'Kindred','SciFi',15.00,5);

INSERT INTO book_order VALUES
 (1,1,'2026-06-01'), (2,2,'2026-06-02'),
 (3,1,'2026-06-05'), (4,3,'2026-06-07');

INSERT INTO order_line VALUES
 (1,1,1),(1,3,2), (2,6,1), (3,2,1),(3,5,1), (4,3,1),(4,4,1),(4,6,2);
