# Capstone — Design, Build & Secure a Small Database

> Tags: `[27200]` `[SEC]` — the whole course in one project. Everything you've been taught
> separately, done together, in the order a real database gets built.

Twelve modules ago a database was "a collection of related information." Now you can model one,
normalize it, define it with constraints, load it, ask it almost any question, and lock it
down. This capstone makes you do all of that *end to end* on a single scenario — the same arc
the real CNIT 27200 labs follow ("design a database for X"), and the same arc a working
developer follows on day one of a new system. There's nothing new to learn here. The skill
being tested is whether you can *sequence* what you already know: model before you define,
define before you load, load before you query, and — the habit this course never lets you drop
— think about the attacker before you ship.

Work it top to bottom. Each stage produces something the next stage needs, exactly like a real
build. Predict each result before you reveal it; on the handwritten exam there's no Run button,
so practicing "I know what this returns" is the point.

## Prerequisites

All twelve modules. Specifically: 03 (ER modeling), 04 (normalization), 05 (DDL and
constraints), 06–09 (querying — filtering, aggregates, joins, subqueries), 10 (DML and
transactions), and 11–12 (the security pass). If any stage feels shaky, that's the module to
revisit before the exam — the capstone is also a self-diagnostic.

## What you'll produce

- An **ER model** of the scenario: entities, relationships, cardinality, and the one
  many-to-many that needs an associative entity
- A **normalized (3NF) schema** — no repeating groups, no partial or transitive dependencies
- The **`CREATE TABLE` statements** that make the database *enforce* that design with keys and
  constraints
- **Seed data** loaded with `INSERT`
- A set of **queries** — joins, aggregates, and a subquery — that answer real business questions
- A deliberate **security review**: find the injectable query, cap the blast radius with least
  privilege, and expose only what's safe with a view

## The scenario

**Inkwell Books** is a small independent bookstore that wants to move its order tracking off a
shared spreadsheet. Here's the whole business, in plain English — this is the kind of
paragraph a real client hands you, and turning it into a schema is the job:

> Inkwell sells **books**, each written by an **author** and priced individually. **Customers**
> place **orders**; a single order can contain several different books, and each book on an
> order has a quantity. The shop wants to know things like "how much has each customer spent,"
> "which books have never sold," and "what's our revenue by author" — and, because customer
> emails and staff logins live in the same database, it wants to be sure a search box can't be
> turned into a data leak.

Read that once more and underline the nouns: *books, authors, customers, orders*. Those are
your entities. The verbs — *written by, place, contain* — are your relationships. Everything
below follows from reading the paragraph that way.

## Stage 1 — Model it (ER)

Four entities, and the relationships between them:

- An **author** writes many **books**; each book has one author → **1:N** (author → book).
- A **customer** places many **orders**; each order belongs to one customer → **1:N**
  (customer → order).
- An **order** contains many **books**, and a **book** appears on many **orders** → **N:M**
  (order ↔ book).

That last one is the interesting one, and it's exactly the situation Module 03 said you can't
model with a plain foreign key. A many-to-many needs an **associative entity** to resolve it —
here, an `order_line` (one row per "this book, on this order, this quantity"). The `quantity`
attribute is the tell: it belongs to neither the order alone nor the book alone, but to the
*pairing*, which is precisely what an associative entity is for.

```
author 1───∞ book ∞───< order_line >───∞ book_order ∞───1 customer
                         (order_id, book_id, quantity)
```

> **Watch out:** a beginner reflex is to give `book_order` columns like `book1_id, book2_id,
> book3_id` for "up to three books per order." That's the repeating group Module 04 warned
> about — it caps the order size, wastes space, and makes "which orders include *Dune*"
> miserable to query. The associative entity has no such limit: one `order_line` row per book,
> as many as you like.

## Stage 2 — Normalize it (3NF)

Imagine Inkwell's current spreadsheet — one fat row per line item:

```
order_id | order_date | customer_name | customer_email    | book_title | author_name    | price | qty
---------+------------+---------------+-------------------+------------+----------------+-------+----
1        | 2026-06-01 | Maya Chen     | maya@example.com  | Earthsea   | Ursula Le Guin | 12.00 | 1
1        | 2026-06-01 | Maya Chen     | maya@example.com  | 1984       | George Orwell  | 10.00 | 2
```

Every anomaly from Module 04 is sitting right there. Maya's email is copied onto every line of
every order she places (update anomaly — change it once, miss a row, and now she has two
emails). A book nobody has ordered yet can't be recorded at all (insertion anomaly). Delete the
last order for a customer and you lose the customer (deletion anomaly). Normalizing splits this
one table into the entities from Stage 1, each fact stored exactly once:

- **1NF** — already atomic (no comma-lists in a cell), but the repeating groups across rows are
  the redundancy we remove by splitting.
- **2NF** — `book_title`, `author_name`, and `price` depend only on the *book*, not on the
  whole `(order_id, book_id)` line — a partial dependency. They move to a `book` table.
- **3NF** — `author_name` depends on the author, not the book (a transitive dependency: order →
  book → author). It moves to its own `author` table, and `book` keeps just `author_id`.

The result is the five tables Stage 1 predicted: `author`, `book`, `customer`, `book_order`,
`order_line`. Each column now lives with the key it actually depends on — which is the whole
definition of 3NF.

## Stage 3 — Define it (DDL)

Now the design becomes SQL the database *enforces*. Note every constraint is a design decision
from Stages 1–2 made mandatory: primary keys give each row identity, foreign keys make the
relationships real, `NOT NULL` marks what can't be missing, `UNIQUE` stops duplicate emails,
and `CHECK` refuses nonsense like a negative price.

```sql
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
```

The `order_line` table shows the associative entity in DDL form: its primary key is the
**composite** `(order_id, book_id)`, which does double duty — it uniquely identifies each line
*and* enforces "the same book can't appear twice on one order" for free. Both columns are also
foreign keys, so a line can never point at an order or a book that doesn't exist.

> **Dialect note:** this is SQLite (the browser engine), so it runs as-is. On the exam's Oracle
> database you'd write `VARCHAR2(n)` instead of `TEXT`, `NUMBER(6,2)` instead of `REAL`, and
> you'd typically attach a `SEQUENCE` for surrogate keys rather than relying on an
> auto-incrementing integer primary key. The *relational logic* — same keys, same constraints,
> same foreign keys — is identical, and that logic is what a hand-graded exam rewards.

## Stage 4 — Load it (DML)

A schema with no rows can't answer anything. Seed each table parent-first, because a foreign
key can't reference a row that isn't there yet — authors before books, customers and books
before orders and lines:

```sql
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
```

Leo (customer 4) placed no orders, and *Kindred* (book 7) has never sold — deliberately, so the
queries below have interesting edge cases to handle. This is also a quiet nod to Module 10: in a
real load you'd wrap these inserts in a **transaction** and `COMMIT` only if every one
succeeds, so a failure halfway through doesn't leave you with books whose author never got
inserted.

## Stage 5 — Query it

Now the payoff — the questions the shop actually asked. First, **how much has each customer
spent?** Revenue lives in three tables at once (who ordered, what was on the order, what it
cost), so this is a three-join chain feeding an aggregate:

```sql
SELECT c.first_name || ' ' || c.last_name AS customer,
       ROUND(SUM(b.price * ol.quantity), 2) AS total_spent
FROM customer c
JOIN book_order bo ON bo.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = bo.order_id
JOIN book b        ON b.book_id = ol.book_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;
```

> **Dialect note:** every non-aggregated column in the `SELECT` — here `first_name` and
> `last_name` — must appear in `GROUP BY`, exactly the rule Module 07 set. SQLite lets you get
> away with `GROUP BY c.customer_id` alone, but Oracle rejects it with `ORA-00979: not a GROUP BY
> expression`. Grouping by `customer_id` *and* the two name columns satisfies both: the id keeps
> two same-named customers apart, and the names clear the exam's rule. Write it the strict way and
> it runs everywhere.

<details>
<summary>Predict the grid, then check</summary>

```
customer    | total_spent
------------+------------
Maya Chen   | 59.0
Sara Okafor | 55.0
Devon Park  | 18.0
```

Maya's two orders total 59 (order 1: 1×12 + 2×10 = 32; order 3: 14 + 13 = 27). Note **Leo is
absent** — an inner `JOIN` drops customers with no matching orders, which is correct here
("spent" implies at least one purchase). If the shop wanted *every* customer including the
zeros, that's a `LEFT JOIN` from `customer` with `COALESCE(SUM(...), 0)` — the exact
inner-vs-outer decision Module 08 drilled.

</details>

Next, **which books have never sold?** That's an absence, and absence is what a subquery with
`NOT IN` expresses cleanly (Module 09):

```sql
SELECT title FROM book
WHERE book_id NOT IN (SELECT book_id FROM order_line)
ORDER BY title;
```

<details>
<summary>Predict, then check</summary>

```
title
-------
Kindred
```

The subquery collects every `book_id` that appears on any order line; the outer query keeps the
books *not* in that set. Only *Kindred* qualifies. (Real-world caution from Module 09: `NOT IN`
misbehaves if the subquery can return `NULL` — here `order_line.book_id` is `NOT NULL`, so it's
safe. When nullability is in doubt, `NOT EXISTS` is the sturdier choice.)

</details>

Finally, **revenue by author**, including authors who've sold nothing — the shop wants the
zeros this time, so it's an outer join all the way down:

```sql
SELECT a.first_name || ' ' || a.last_name AS author,
       COALESCE(SUM(b.price * ol.quantity), 0) AS revenue
FROM author a
LEFT JOIN book b        ON b.author_id = a.author_id
LEFT JOIN order_line ol ON ol.book_id = b.book_id
GROUP BY a.author_id, a.first_name, a.last_name
ORDER BY revenue DESC, author;
```

<details>
<summary>Predict, then check</summary>

```
author         | revenue
---------------+--------
Frank Herbert  | 54.0
George Orwell  | 39.0
Ursula Le Guin | 26.0
Toni Morrison  | 13.0
Octavia Butler | 0
```

Herbert's *Dune* sold 3 copies at 18 (order 2: 1, order 4: 2) = 54. Butler shows **0** rather
than vanishing — that's the `LEFT JOIN` keeping her row and `COALESCE` turning the resulting
`NULL` sum into a real zero. Swap both `LEFT JOIN`s for inner joins and Butler disappears; that
one-word change is the difference between "our authors' sales" and "authors who have sales."

</details>

## Stage 6 — Secure it

The schema works. Now put on the attacker's hat from Modules 11–12, because "it works" and
"it's safe" are different claims. Three questions close the course.

**Where's the injectable query?** The shop's website has a title search. A junior dev built it
the fast way:

```python
# the search box behind Inkwell's website — VULNERABLE
query = "SELECT title, price FROM book WHERE title LIKE '%" + search + "%'"
```

An attacker types `x%' UNION SELECT username, password FROM staff_user --` into the search box,
and — exactly as in Module 11 — the `UNION` staples every staff credential onto what should
have been a book list. The fix is not to filter the input; it's to **parameterize** so the
input can never be code:

```python
# SAFE
query = "SELECT title, price FROM book WHERE title LIKE ?"
db.execute(query, ['%' + search + '%'])
```

Now `x%' UNION SELECT ... --` is searched for as a *literal title*, matches no book, and the
attack returns nothing.

**Cap the blast radius with least privilege (Module 12).** Even parameterized, the website's
database account should be able to do only what the storefront needs — read the catalog, write
orders — and nothing else. So you `GRANT` narrowly instead of handing over `ALL`:

```sql
GRANT SELECT ON book, author TO web_app;   -- browse the catalog
GRANT SELECT, INSERT ON book_order, order_line TO web_app;  -- place orders
-- pointedly NOT granted: any access to staff_user, or DELETE/DROP on anything
```

If an injection ever *does* slip through on that account, the attacker inherits its tiny
privileges: no reach into `staff_user` at all, no ability to delete orders or drop tables. The
break-in still finds most doors locked.

**Expose only what's safe with a view (Module 12).** The public catalog page needs titles,
authors, and prices — never the customer or staff tables. A view makes that boundary the
database's job, not the application's:

```sql
CREATE VIEW catalog_public AS
SELECT b.title, a.first_name || ' ' || a.last_name AS author, b.price
FROM book b
JOIN author a ON a.author_id = b.author_id;
```

<details>
<summary>What does <code>SELECT * FROM catalog_public ORDER BY title;</code> return — and what can't it reach?</summary>

```
title                     | author         | price
--------------------------+----------------+------
1984                      | George Orwell  | 10.0
A Wizard of Earthsea      | Ursula Le Guin | 12.0
Animal Farm               | George Orwell  | 9.0
Beloved                   | Toni Morrison  | 13.0
Dune                      | Frank Herbert  | 18.0
Kindred                   | Octavia Butler | 15.0
The Left Hand of Darkness | Ursula Le Guin | 14.0
```

Seven books with their authors and prices — and **nothing else reachable**. There is no
customer email, no order history, no staff login anywhere in this view, because it never
selected those tables. `GRANT SELECT ON catalog_public TO web_public` and `REVOKE` direct
access to the base tables, and the storefront can show the catalog while being structurally
incapable of leaking a customer's address. That's confidentiality enforced by the database, not
promised by the app — the note Module 12 closed on.

</details>

> **Dialect note:** the `CREATE VIEW` and the parameterized-query *reasoning* are real, but
> `GRANT`/`REVOKE` don't run in the browser's SQLite (no user accounts — Module 12). On the
> Oracle exam they're expected cold, so write them out by hand as practice even though the IDE
> can't execute them.

## Recap

A database gets built in an order, and this capstone is that order. You **modeled** Inkwell's
business into four entities plus one associative entity (`order_line`) to resolve the
order-to-book many-to-many; **normalized** the fat spreadsheet to 3NF so every fact lives with
the key it depends on and the update/insert/delete anomalies vanish; **defined** the design as
`CREATE TABLE`s whose primary keys, foreign keys, `NOT NULL`, `UNIQUE`, and `CHECK` constraints
make the database enforce the model instead of trusting the application to; **loaded** it
parent-first (ideally inside a transaction); **queried** it with the full toolkit — a
three-table join into an aggregate for customer spend, a `NOT IN` subquery for never-sold
books, and `LEFT JOIN` + `COALESCE` for revenue-by-author including the zeros; and **secured**
it by parameterizing the injectable search, granting the web account least privilege so a breach
finds little to steal, and fronting the catalog with a view that exposes only what's safe. That
last stage is the whole point of this course's security lens: a schema isn't finished when it
answers questions correctly — it's finished when it also refuses the questions it shouldn't
answer.

## Quiz seeds

- Q: Inkwell needs "one order can contain many books, and one book can be on many orders." How
  do you model that relationship correctly?
  - ✅ Add an associative entity (`order_line`) with a composite key `(order_id, book_id)` plus
    the line's own `quantity`, resolving the N:M into two 1:N relationships
  - ❌ Put `book_id` as a foreign key column on `book_order` — that only allows one book per
    order; it can't represent an order with several books
  - ❌ Put `order1_id, order2_id, order3_id` columns on `book` — that's a repeating group (a 1NF
    violation) and caps how many orders a book can appear on
- Q: The revenue-by-author query uses `LEFT JOIN` and `COALESCE(SUM(...), 0)` instead of an
  inner join. Why does that matter for Octavia Butler, who has sold nothing?
  - ✅ A `LEFT JOIN` keeps her author row even with no matching sales, and `COALESCE` turns the
    resulting `NULL` sum into 0; an inner join would drop her from the results entirely
  - ❌ It's just a style choice — the two produce the same rows — an inner join would omit every
    author with zero sales, so the result set would be different
  - ❌ `COALESCE` is what makes the join keep her row — the `LEFT JOIN` keeps the row; `COALESCE`
    only cleans up the `NULL` into a 0
- Q: Inkwell's website account is granted `SELECT` on the catalog and `SELECT, INSERT` on orders
  — and nothing on `staff_user`. Why is that a security control and not just tidiness?
  - ✅ It's least privilege: if an injection or credential theft hits that account, the attacker
    inherits only those few rights and can't read staff logins, delete orders, or drop tables
  - ❌ It makes the queries run faster — privileges are about permission, not performance; the
    point is capping what a compromised account can do
  - ❌ It prevents SQL injection from happening — least privilege limits the *damage* of an
    injection; parameterized queries are what prevent the injection itself

## Up next

There is no next module — this was the finish line. You can now take a business description,
turn it into a normalized relational design, define and populate it in SQL, answer real
questions with joins, aggregates, and subqueries, change it safely, and review it like an
attacker would. That's the full span of CNIT 27200 plus the security throughline the exam
doesn't test but every real database job does. Two things left: run back through the cheat sheet
until the joins diagram and the normal-form checklist are automatic, and — because the test-out
exam is handwritten with no Run button — practice drafting a few of these queries and `CREATE
TABLE`s on paper first, then checking them in the IDE. When "I already know what this returns"
stops being a guess, you're ready to sit the exam.
