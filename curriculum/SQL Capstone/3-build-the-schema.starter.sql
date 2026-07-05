-- A partial, under-constrained draft. Two tables are fine; the other three are
-- missing the constraints that make the design real. Finish it:
--   * book must NOT NULL its title, CHECK (price >= 0), and REFERENCE author
--   * book_order must REFERENCE customer
--   * order_line needs a COMPOSITE primary key (order_id, book_id) and BOTH
--     foreign keys (to book_order and to book)
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
  title     TEXT,
  genre     TEXT,
  price     REAL,
  author_id INTEGER
);

CREATE TABLE book_order (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,
  order_date  TEXT
);

CREATE TABLE order_line (
  order_id INTEGER,
  book_id  INTEGER,
  quantity INTEGER,
  PRIMARY KEY (order_id)
);
