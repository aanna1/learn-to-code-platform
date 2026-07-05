-- A classic credentials table -- the target every attacker wants.
CREATE TABLE users (
  id       INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  role     TEXT NOT NULL
);

INSERT INTO users (id, username, password, role) VALUES
  (1, 'admin',    's3cr3t',   'admin'),
  (2, 'jhalpert', 'pam4ever', 'user'),
  (3, 'dwight',   'beets',    'user');
