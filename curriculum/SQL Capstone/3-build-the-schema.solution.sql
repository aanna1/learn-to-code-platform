-- Every constraint is a design decision from Stages 1-2 made mandatory:
-- primary keys give identity, foreign keys make the relationships real,
-- NOT NULL marks what can't be missing, UNIQUE stops duplicate emails,
-- CHECK refuses nonsense like a negative price.
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
