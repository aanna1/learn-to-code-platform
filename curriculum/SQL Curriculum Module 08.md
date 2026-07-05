# Module 08 — Joins

> Tags: `[27200]`

Every query you've written so far has lived inside a single table. But you didn't *design* your
database as one table — back in Module 02 you split it into `employee` and `branch` and wired them
together with a foreign key, precisely so each fact lives in exactly one place. The cost of that
tidiness is that the interesting questions now span *two* tables at once: "who manages the Scranton
branch?" needs a name from `employee` and a branch from `branch`. **Joins** are how you put the
pieces back together — combining rows from two or more tables, matched on a related column, into one
result grid.

This is the single most heavily tested topic on the real exam — there's a whole lecture devoted to
outer joins alone — so it gets the most room here. By the end you'll be able to write inner joins,
all three outer joins, self-joins, and `UNION`, and know exactly which rows each one keeps or drops.

Two tables drive every example. First the `employee` table you already know from Modules 06–07:

```
employee
+-------------+------------+-----------+-----------+--------+------------+
| employee_id | first_name | last_name | branch_id | salary | hire_date  |
+-------------+------------+-----------+-----------+--------+------------+
| 100         | Jan        | Levinson  | 1         | 110000 | 2004-03-15 |
| 101         | Michael    | Scott     | 2         | 90000  | 2005-03-24 |
| 102         | Dwight     | Schrute   | 2         | 62000  | 2005-04-01 |
| 103         | Jim        | Halpert   | 2         | 60000  | 2006-01-10 |
| 104         | Pam        | Beesly    | 2         | 42000  | 2006-05-08 |
| 105         | Andy       | Bernard   | 3         | 55000  | 2007-09-20 |
| 106         | Stanley    | Hudson    | 2         | 58000  | 2004-11-02 |
| 107         | Ryan       | Howard    | NULL      | 48000  | 2007-06-01 |
+-------------+------------+-----------+-----------+--------+------------+
```

And now a `branch` table to join it against:

```
branch
+-----------+-------------+--------+
| branch_id | branch_name | mgr_id |
+-----------+-------------+--------+
| 1         | Corporate   | 100    |
| 2         | Scranton    | 101    |
| 3         | Stamford    | 105    |
| 4         | Buffalo     | NULL   |
+-----------+-------------+--------+
```

Notice two deliberately lopsided rows. **Ryan** (employee 107) has a `NULL` `branch_id` — he's not
assigned anywhere yet. And **Buffalo** (branch 4) has no manager and, as it happens, no employees
assigned to it at all. Those two mismatches are invisible in an inner join and become the whole
point of the outer joins later. Keep them in the corner of your eye.

## Prerequisites

Modules 02 (primary/foreign keys — a join follows the FK relationship you designed there), 06
(`SELECT`, `WHERE`), and 07 (`GROUP BY`, and especially the `COUNT(*)` vs. `COUNT(column)` `NULL`
rule, which comes back in this module's "Try it").

## What you'll learn

- **`INNER JOIN`** — combine rows that match on a related column, and why unmatched rows vanish
- Writing **qualified column names** (`employee.first_name`) and shortening them with **table aliases**
- The join *condition* is just a boolean: **equijoins** (`=`) vs. **non-equijoins** (`BETWEEN`, `<`, `>`)
- **`NATURAL JOIN`**, and why the convenience is a trap
- The three **outer joins** — `LEFT`, `RIGHT`, `FULL OUTER` — and exactly which unmatched rows each keeps
- **Self-joins**: joining a table to itself to follow a relationship inside one table
- **`UNION`** / **`UNION ALL`** — stacking result sets vertically, and the rules that govern it
- (woven throughout) how joins cross data-sensitivity boundaries, and why `UNION` is the engine behind a whole class of injection attacks

## Your first join: INNER JOIN

Module 07 promised this exact query: list each employee alongside the *name* of the branch they work
in. The name lives in `branch`, the person lives in `employee`, and the two tables share a column —
`employee.branch_id` points at `branch.branch_id`. That shared column is the hinge the join swings on:

```sql
SELECT employee.first_name, employee.last_name, branch.branch_name
FROM employee
JOIN branch ON employee.branch_id = branch.branch_id;
```

```
+------------+-----------+-------------+
| first_name | last_name | branch_name |
+------------+-----------+-------------+
| Jan        | Levinson  | Corporate   |
| Michael    | Scott     | Scranton    |
| Dwight     | Schrute   | Scranton    |
| Jim        | Halpert   | Scranton    |
| Pam        | Beesly    | Scranton    |
| Andy       | Bernard   | Stamford    |
| Stanley    | Hudson    | Scranton    |
+------------+-----------+-------------+
```

Two new things are happening. First, because more than one table is in play, you write
**qualified column names** — `employee.first_name`, `branch.branch_name` — so SQL knows which table
each column comes from. (When a column name is unambiguous you can drop the prefix, but qualifying
everything is a good habit and it's required when both tables have a same-named column, like
`branch_id` here.) Second, the `ON` clause is the matching rule: pair an `employee` row with a
`branch` row *only when* their `branch_id`s are equal.

Now count the rows. Eight employees went in; **seven** came out. Ryan is missing — his `branch_id` is
`NULL`, so it matched no branch, and an inner join keeps only rows that find a partner. Buffalo is
missing too — no employee has `branch_id = 4`, so it partnered with no one. That's the defining
behavior of `INNER JOIN`: **a row appears only if it finds a match on the other side.** Unmatched
rows on *either* side are dropped. (`JOIN` and `INNER JOIN` mean exactly the same thing; the `INNER`
is optional and just makes the intent explicit.)

## Table aliases: less typing, clearer queries

Spelling out `employee.` and `branch.` on every column gets old fast, especially with longer table
names. You can give each table a short **alias** right after naming it in `FROM`, then use the alias
everywhere else:

```sql
SELECT e.first_name, e.last_name, b.branch_name
FROM employee e
JOIN branch b ON e.branch_id = b.branch_id;
```

Same seven rows, far less noise. `employee e` means "call it `e` for the rest of this query." Aliases
are cosmetic here, but for self-joins later they stop being optional — you'll *need* two different
names for the same table.

## The join condition is just a boolean: equijoins vs. non-equijoins

Nothing says the `ON` condition has to compare `branch_id` to `branch_id`, or even use `=`. It's an
ordinary boolean expression, exactly like a `WHERE` clause. When it uses equality, the join has a
name you'll see on exams: an **equijoin**. Our branch join is one. So is this one, which follows a
*different* shared column — the branch's `mgr_id`, which stores an `employee_id`:

```sql
SELECT b.branch_name, e.first_name, e.last_name
FROM branch b
JOIN employee e ON b.mgr_id = e.employee_id;
```

```
+-------------+------------+-----------+
| branch_name | first_name | last_name |
+-------------+------------+-----------+
| Corporate   | Jan        | Levinson  |
| Scranton    | Michael    | Scott     |
| Stamford    | Andy       | Bernard   |
+-------------+------------+-----------+
```

Three rows — one per branch that actually *has* a manager. Buffalo's `mgr_id` is `NULL`, so it drops
out of the inner join, and the columns being matched (`mgr_id` and `employee_id`) don't even share a
name. That's fine; the join cares about the *values*, not the column labels.

When the condition uses something *other* than equality — a range, a `<`, a `>` — it's a
**non-equijoin**. The classic example matches each employee to a salary grade band. Picture a small
lookup table:

```
salary_grade
+-------+---------+----------+
| grade | low_end | high_end |
+-------+---------+----------+
| A     | 100000  | 999999   |
| B     | 60000   | 99999    |
| C     | 40000   | 59999    |
+-------+---------+----------+
```

There's no shared key between `employee` and `salary_grade` — you match on *where the salary falls*:

```sql
SELECT e.first_name, e.salary, g.grade
FROM employee e
JOIN salary_grade g ON e.salary BETWEEN g.low_end AND g.high_end;
```

```
+------------+--------+-------+
| first_name | salary | grade |
+------------+--------+-------+
| Jan        | 110000 | A     |
| Michael    | 90000  | B     |
| Dwight     | 62000  | B     |
| Jim        | 60000  | B     |
| Pam        | 42000  | C     |
| Andy       | 55000  | C     |
| Stanley    | 58000  | C     |
| Ryan       | 48000  | C     |
+------------+--------+-------+
```

Each employee lands in exactly one band because the ranges don't overlap. Same `JOIN ... ON`
machinery — only the condition changed from `=` to `BETWEEN`.

> **Dialect note:** the equijoin/non-equijoin vocabulary is Oracle-flavored (the exam's world), where
> you'll also see the older comma syntax `FROM employee, branch WHERE employee.branch_id =
> branch.branch_id`. That produces the same result as an inner join, but the modern `JOIN ... ON`
> form is clearer and much harder to break — forget the `WHERE` in the comma style and you get a
> **cross join** (every row paired with every row), which is almost never what you want. Prefer
> `JOIN ... ON`.

## NATURAL JOIN: convenient, and a trap

Since our two tables share a column *name* — `branch_id` — SQL offers a shortcut that joins on it
automatically, no `ON` clause needed:

```sql
SELECT first_name, last_name, branch_name
FROM employee
NATURAL JOIN branch;
```

This returns the same seven rows as the first inner join. `NATURAL JOIN` finds every column the two
tables have *in common by name* and quietly joins on all of them. Convenient — and exactly why it's
risky. The join key is invisible in the query, so it depends entirely on what the columns happen to
be named. Add a column later that both tables share by accident (imagine both grew a `created_date`),
and your `NATURAL JOIN` silently starts matching on that too, and your results change with no edit to
the query. Most professionals avoid it for that reason and write the `ON` condition out in full so
the join key is explicit and stable. Know it for the exam; reach for explicit `JOIN ... ON` in real
work.

## When you need the unmatched rows: OUTER JOINs

Inner joins throw away rows that don't match. Often that's wrong. "How many employees does each
branch have?" should still list Buffalo (with zero), and "which employees are unassigned?" is a
question *about* the row that didn't match. **Outer joins** keep the unmatched rows and fill the
missing side with `NULL`.

### LEFT JOIN — keep every row from the left table

A `LEFT JOIN` keeps *all* rows from the left table (the one in `FROM`), matched or not, and pads the
right side with `NULL` where there's no match:

```sql
SELECT e.first_name, b.branch_name
FROM employee e
LEFT JOIN branch b ON e.branch_id = b.branch_id;
```

```
+------------+-------------+
| first_name | branch_name |
+------------+-------------+
| Jan        | Corporate   |
| Michael    | Scranton    |
| Dwight     | Scranton    |
| Jim        | Scranton    |
| Pam        | Scranton    |
| Andy       | Stamford    |
| Stanley    | Scranton    |
| Ryan       | NULL        |
+------------+-------------+
```

Eight rows now, not seven. Ryan is back — the left table is `employee`, so *every* employee survives,
and since his `branch_id` matched nothing, his `branch_name` comes back `NULL`. That `NULL` isn't
noise; it's the answer to "who has no branch?" `LEFT JOIN` is the one you'll use most, because "keep
everything on my main table, attach related info where it exists" is such a common need.

### RIGHT JOIN — keep every row from the right table

A `RIGHT JOIN` is the mirror image: keep all rows from the *right* table, pad the left with `NULL`.
Swap which side is preserved and Buffalo — the branch with no employees — reappears:

```sql
SELECT e.first_name, b.branch_name
FROM employee e
RIGHT JOIN branch b ON e.branch_id = b.branch_id;
```

```
+------------+-------------+
| first_name | branch_name |
+------------+-------------+
| Jan        | Corporate   |
| Michael    | Scranton    |
| Dwight     | Scranton    |
| Jim        | Scranton    |
| Pam        | Scranton    |
| Stanley    | Scranton    |
| Andy       | Stamford    |
| NULL       | Buffalo     |
+------------+-------------+
```

Every branch is present; Buffalo has no employee, so its `first_name` is `NULL`. Notice Ryan is gone
again — he's on the *left*, and a right join doesn't protect the left side.

Here's a useful truth: **you never actually need `RIGHT JOIN`.** Any right join is a left join with
the tables written in the other order. `employee RIGHT JOIN branch` is the same as `branch LEFT JOIN
employee`. Many people write every outer join as a `LEFT JOIN` for consistency and just reorder the
tables. That habit also sidesteps a portability problem:

> **Dialect note:** `RIGHT JOIN` and `FULL OUTER JOIN` are newer to SQLite — support arrived in
> version 3.39 (2022). If the browser IDE is running an older build, `RIGHT JOIN` will error; rewrite
> it as a `LEFT JOIN` with the tables swapped and it'll run anywhere. MySQL and Oracle (the exam's
> engine) both support `RIGHT JOIN` fine. The safe move on a handwritten exam is to know it, but
> reach for `LEFT JOIN` when you have the choice.

### FULL OUTER JOIN — keep everything from both sides

A `FULL OUTER JOIN` keeps every row from *both* tables — matched rows join up, and unmatched rows from
either side come through with `NULL` on the missing half. It's a `LEFT` and a `RIGHT` at once, so both
Ryan *and* Buffalo appear:

```sql
SELECT e.first_name, b.branch_name
FROM employee e
FULL OUTER JOIN branch b ON e.branch_id = b.branch_id;
```

```
+------------+-------------+
| first_name | branch_name |
+------------+-------------+
| Jan        | Corporate   |
| Michael    | Scranton    |
| Dwight     | Scranton    |
| Jim        | Scranton    |
| Pam        | Scranton    |
| Stanley    | Scranton    |
| Andy       | Stamford    |
| Ryan       | NULL        |
| NULL       | Buffalo     |
+------------+-------------+
```

Nine rows: the seven matches, plus Ryan (employee with no branch), plus Buffalo (branch with no
employee). This is the join you want when you're reconciling two lists and need to see *both* kinds of
leftover — every unassigned person and every empty branch in one grid.

> **Dialect note:** MySQL has no `FULL OUTER JOIN` at all — you emulate it by `UNION`-ing a `LEFT
> JOIN` with a `RIGHT JOIN` (you'll meet `UNION` in a moment). Oracle supports it directly, and recent
> SQLite (3.39+) does too. It's the least portable of the joins, so on the exam expect Oracle syntax.

## Joining a table to itself: the self-join

Sometimes the relationship you want to follow lives *inside a single table*. Suppose each employee has
a supervisor who is also an employee — the table points at itself. For this example, picture the
`employee` table with one extra column, `supervisor_id`, holding the `employee_id` of that person's boss:

```
employee (with supervisor_id)
+-------------+------------+---------------+
| employee_id | first_name | supervisor_id |
+-------------+------------+---------------+
| 100         | Jan        | NULL          |
| 101         | Michael    | 100           |
| 102         | Dwight     | 101           |
| 103         | Jim        | 101           |
| 104         | Pam        | 101           |
| 105         | Andy       | 100           |
| 106         | Stanley    | 101           |
| 107         | Ryan       | 101           |
+-------------+------------+---------------+
```

Jan reports to no one (`supervisor_id` is `NULL`); Michael and Andy report to Jan; everyone else reports to
Michael. To show each person next to their supervisor's *name*, you need the table in two roles at
once: one copy playing "the employee," another playing "the supervisor." Aliases make that possible —
same table, two names:

```sql
SELECT e.first_name AS employee, s.first_name AS supervisor
FROM employee e
JOIN employee s ON e.supervisor_id = s.employee_id;
```

```
+----------+------------+
| employee | supervisor |
+----------+------------+
| Michael  | Jan        |
| Dwight   | Michael    |
| Jim      | Michael    |
| Pam      | Michael    |
| Andy     | Jan        |
| Stanley  | Michael    |
| Ryan     | Michael    |
+----------+------------+
```

Read the `ON` clause as "match each employee `e` to the row `s` whose `employee_id` equals `e`'s
`supervisor_id`" — that's the supervisor. It's an ordinary inner join; the only twist is that both sides
are the same table, which is exactly why the aliases are mandatory. Seven rows, not eight — it's an
*inner* join, so Jan is missing: her `supervisor_id` is `NULL` (she's at the top and reports to no one).
Swap in `LEFT JOIN employee s` and Jan comes back with a `NULL` supervisor, the same outer-join
behavior you just saw.

## Stacking results: UNION

Joins glue tables together *side by side* — more columns per row. `UNION` does the opposite: it stacks
the results of two `SELECT`s *on top of each other* — more rows, same columns. Say you want a single
list of every name in the database, people and branches alike:

```sql
SELECT first_name AS name FROM employee
UNION
SELECT branch_name FROM branch;
```

That returns one `name` column with all twelve values — the eight employees and four branches — in one
list. Two rules govern it: each `SELECT` must produce the **same number of columns**, and matching
columns must have **compatible types** (you can't stack a name onto a date). The column names come from
the *first* `SELECT`, which is why the alias `AS name` is on the top query.

By default `UNION` also **removes duplicates**, like `SELECT DISTINCT`. Stack the `branch_id`s from
both tables and the repeats collapse:

```sql
SELECT branch_id FROM employee
UNION
SELECT branch_id FROM branch;
-- returns 5 rows: NULL, 1, 2, 3, 4
```

Even though `employee` alone lists `branch_id = 2` five times, `UNION` folds them into one. If you
want every row kept — duplicates and all — use **`UNION ALL`**, which is also faster because it skips
the de-duplication work:

```sql
SELECT branch_id FROM employee
UNION ALL
SELECT branch_id FROM branch;
-- returns 12 rows: all 8 from employee + all 4 from branch, no folding
```

One more thing to know cold: `UNION` does **not** guarantee any particular row order. If order matters,
put a single `ORDER BY` at the very end, after the last `SELECT`.

> **Security lens:** `UNION` is not just a reporting convenience — it's the mechanism behind an entire
> family of attacks called **UNION-based SQL injection**. If an application builds a query by pasting
> user input into a `SELECT`, an attacker can inject their own `UNION SELECT username, password FROM
> users` onto the end, and the database will happily *stack the secret table onto the result the app
> expected* and hand it all back. The two rules you just learned are exactly what the attacker satisfies
> to make it work: match the column count, match the types. You'll take this apart properly — and learn
> the parameterized-query fix — in Module 11. For now, just register that the same feature that stacks
> employees and branches can stack a password table onto a public query.

> **Security lens (joins):** joins are also where data-sensitivity boundaries get crossed. A join can
> pull a public column and a restricted one into the same result — imagine joining a public `employee`
> directory to a private `compensation` table. The join itself is neutral; the risk is *who's allowed to
> run it*. This is why a real database restricts join-able tables per user and often exposes only a
> **view** that pre-joins the safe columns. That's the least-privilege story of Module 12 — hold the
> thought.

## Try it: predict the grid

This one braids together everything — an outer join, a `GROUP BY` from Module 07, and the
`COUNT(column)` `NULL` rule you learned there. "How many employees does each branch have?"

```sql
SELECT b.branch_name, COUNT(e.employee_id) AS headcount
FROM branch b
LEFT JOIN employee e ON e.branch_id = b.branch_id
GROUP BY b.branch_name;
```

Four branches, but one of them is Buffalo — which has no employees. What does its `headcount` come
out to, and why?

<details>
<summary>Think it through, then click to check</summary>

**Four rows:**

```
+-------------+-----------+
| branch_name | headcount |
+-------------+-----------+
| Corporate   | 1         |
| Scranton    | 5         |
| Stamford    | 1         |
| Buffalo     | 0         |
+-------------+-----------+
```

The `LEFT JOIN` from `branch` keeps Buffalo even though no employee matches — its row comes through with
a `NULL` `employee_id`. Then `COUNT(e.employee_id)` counts only **non-`NULL`** values (the exact rule
from Module 07), so Buffalo's lone `NULL` counts as **0**. That's the number you want.

The trap: had you written `COUNT(*)` instead, Buffalo would show **1** — because the `LEFT JOIN` still
produced one physical row for it, and `COUNT(*)` counts rows regardless of `NULL`. So on an outer join,
`COUNT(a_real_column)` and `COUNT(*)` disagree by exactly the number of unmatched rows. Counting a column
from the *joined* side is how you get true zeros.

(Ryan doesn't appear at all here — his `branch_id` is `NULL`, and this join is anchored on `branch`, so
an unassigned *employee* has nowhere to land. Flip the join to `FROM employee LEFT JOIN branch` and it'd
be the reverse.)

</details>

## Recap

A join combines rows from two or more tables, matched by an `ON` condition. `INNER JOIN` (a.k.a. plain
`JOIN`) keeps only rows that find a match on both sides — which is why Ryan (no branch) and Buffalo (no
employee) both dropped out. Because multiple tables are in play you write qualified column names like
`e.first_name`, and **table aliases** keep that readable. The `ON` condition is any boolean: an
**equijoin** uses `=` (on a shared key or any two comparable columns), a **non-equijoin** uses ranges or
inequalities like `BETWEEN`. `NATURAL JOIN` auto-matches same-named columns and is best avoided because
the join key is invisible and unstable. The three **outer joins** keep unmatched rows and fill the gaps
with `NULL`: `LEFT` keeps everything on the left (Ryan reappears), `RIGHT` keeps everything on the right
(Buffalo reappears) and is really just a reordered `LEFT`, and `FULL OUTER` keeps both — mind that
`RIGHT`/`FULL` need SQLite 3.39+ and that MySQL lacks `FULL OUTER` entirely. A **self-join** aliases one
table into two roles to follow a relationship inside it, like employee→supervisor. And `UNION` stacks two
result sets vertically (same column count, compatible types, first query names the columns), removing
duplicates unless you use `UNION ALL` — the very feature that, misused through injected input, powers
UNION-based SQL injection.

## Quiz seeds

- Q: An inner join of `employee` and `branch` on `branch_id` returns 7 rows, but `employee` has 8 rows
  and `branch` has 4. Why 7?
  - ✅ Inner joins keep only matched rows: Ryan's `branch_id` is `NULL` so he matches no branch, and
    Buffalo (branch 4) has no employees — both unmatched rows are dropped, leaving the 7 that pair up
  - ❌ A join always returns the row count of the smaller table — false; a join returns matched rows,
    which can be more *or* fewer than either table depending on the matches
  - ❌ One of Scranton's employees was a duplicate and got removed — inner joins don't de-duplicate;
    all five Scranton employees are present in the 7 rows

- Q: You want a list of every branch *including* ones with no employees, each with its employee count.
  Which join, and why not an inner join?
  - ✅ A `LEFT JOIN` from `branch` (or `RIGHT JOIN` to it) — an inner join would silently drop Buffalo,
    the empty branch, which is exactly the row you need to show a 0
  - ❌ An inner join is fine; empty branches will show up with a count of 0 — no, an inner join omits
    unmatched branch rows entirely, so Buffalo wouldn't appear at all
  - ❌ A `UNION` of the two tables — `UNION` stacks rows vertically; it can't attach each branch to its
    employees side by side, which is what a per-branch count needs

- Q: On that outer join, why does `COUNT(employee_id)` give Buffalo a headcount of 0 while `COUNT(*)`
  gives 1?
  - ✅ The outer join emits one row for Buffalo with a `NULL` `employee_id`; `COUNT(column)` skips
    `NULL`s so it's 0, while `COUNT(*)` counts the row itself so it's 1
  - ❌ `COUNT(*)` is simply wrong on joins and should never be used — it's not wrong, it just counts rows
    rather than non-null values; which you want depends on the question
  - ❌ Buffalo actually has one employee whose name is `NULL` — no; Buffalo has no employees, and the
    `NULL` is produced by the outer join padding the unmatched side

- Q: Why do many developers write every outer join as a `LEFT JOIN` rather than using `RIGHT JOIN`?
  - ✅ Any `RIGHT JOIN` is equivalent to a `LEFT JOIN` with the tables in the other order, and `LEFT
    JOIN` is more widely supported (older SQLite lacks `RIGHT`/`FULL`), so it's more portable and
    consistent
  - ❌ `RIGHT JOIN` produces incorrect results — it's correct; it just preserves the right table instead
    of the left, and can always be rewritten as a `LEFT` join
  - ❌ `RIGHT JOIN` is slower on every database — the choice is about portability and readability, not a
    universal performance rule

- Q: What's the difference between `UNION` and `UNION ALL`, and why does it matter for security?
  - ✅ `UNION` removes duplicate rows (like `DISTINCT`); `UNION ALL` keeps them all and is faster — and
    `UNION`'s ability to append a second `SELECT` onto a query is the basis of UNION-based SQL injection
  - ❌ `UNION` stacks rows and `UNION ALL` joins columns side by side — both stack rows; the only
    difference is duplicate handling
  - ❌ They're identical; `ALL` is just an optional keyword with no effect — `ALL` specifically disables
    duplicate removal, which changes both the result and the performance

## Up next

You've now got the full querying toolkit — filtering, aggregates, and joins across several tables — so
it's time to prove it. **Checkpoint B — Multi-Table Report** hands you a seeded multi-table schema (a
small store or library) and asks you to write a series of join-based queries that answer realistic
business questions, reinforcing everything from Modules 05–08. After that, **Module 09 — Subqueries**
goes the other
direction: nesting one query *inside* another, so the result of one `SELECT` feeds the `WHERE`, the
`FROM`, or even a single column of another. You'll write scalar subqueries, `IN`/`NOT IN` subqueries,
correlated subqueries, and `EXISTS` — and see where a subquery is clearer than a join and where a join
is clearer than a subquery.
