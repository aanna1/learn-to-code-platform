-- The store's product catalog -- what the search box is SUPPOSED to reach.
CREATE TABLE product (
  name  TEXT,
  price REAL
);
INSERT INTO product (name, price) VALUES
  ('Standard Paper',     4.50),
  ('Cardstock',          8.00),
  ('Glossy Photo Paper', 12.00);

-- The credentials table -- what the attacker actually wants, sitting in the
-- same database the search box can reach.
CREATE TABLE users (
  username TEXT,
  password TEXT
);
INSERT INTO users (username, password) VALUES
  ('admin',    's3cr3t'),
  ('jhalpert', 'pam4ever'),
  ('dwight',   'beets');
