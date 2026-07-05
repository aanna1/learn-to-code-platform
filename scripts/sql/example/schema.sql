-- Fixture: seeded before the learner's SQL on every test case (fresh DB per case).
-- A tiny products catalog — enough to make ORDER BY / LIMIT meaningful.
CREATE TABLE products (
  id       INTEGER PRIMARY KEY,
  name     TEXT NOT NULL UNIQUE,
  price    INTEGER NOT NULL,
  category TEXT
);

INSERT INTO products (id, name, price, category) VALUES
  (1, 'Lamp',  40,  'home'),
  (2, 'Chair', 95,  'home'),
  (3, 'Desk',  210, 'home'),
  (4, 'Pen',   3,   'office'),
  (5, 'Mug',   12,  'office');
