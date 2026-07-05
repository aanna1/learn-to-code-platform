# Module 09 — Subqueries

> Tags: `[27200]`

Here's a question you can't yet answer in one shot: "who earns more than the company average?" You
know how to get the average — `SELECT AVG(salary) FROM employee` — and you know how to filter with
`WHERE salary > ...`. The trouble is the `...`. You'd have to run the first query, read off `65625`
with your own eyes, then paste it into a second query by hand. That works exactly once; the moment
someone's salary changes, your pasted number is wrong.

A **subquery** closes that gap. It's a query written *inside* another query, so the database runs the
inner one first and feeds its result straight into the outer one — no copying numbers by hand. That's
the whole idea, and everything in this module is a variation on it: the inner query can return a
single value, a whole column of values, or just a yes/no "did anything match?" You'll learn each
shape, plus the one subtlety that trips up nearly everyone (a `NULL` hiding inside a `NOT IN`).

Same two tables as Module 08:

```
employee                                                      branch
+-------------+------------+-----------+-----------+--------+   +-----------+-------------+--------+
| employee_id | first_name | last_name | branch_id | salary |   | branch_id | branch_name | mgr_id |
+-------------+------------+-----------+-----------+--------+   +-----------+-------------+--------+
| 100         | Jan        | Levinson  | 1         | 110000 |   | 1         | Corporate   | 100    |
| 101         | Michael    | Scott     | 2         | 90000  |   | 2         | Scranton    | 101    |
| 102         | Dwight     | Schrute   | 2         | 62000  |   | 3         | Stamford    | 105    |
| 103         | Jim        | Halpert   | 2         | 60000  |   | 4         | Buffalo     | NULL   |
| 104         | Pam        | Beesly    | 2         | 42000  |   +-----------+-------------+--------+
| 105         | Andy       | Bernard   | 3         | 55000  |
| 106         | Stanley    | Hudson    | 2         | 58000  |
| 107         | Ryan       | Howard    | NULL      | 48000  |
+-------------+------------+-----------+-----------+--------+
```

Ryan (no branch) and Buffalo (no employees) are still the odd rows out — subqueries interact with those
`NULL`s in ways worth watching.

## Prerequisites

Modules 06 (`SELECT`, `WHERE`, `IN`), 07 (`AVG` and the other aggregates), and 08 (joins — because the
last section compares subqueries to joins, and `EXISTS` is really a join in disguise).

## What you'll learn

- **Scalar subqueries** — an inner query that returns one value, usable anywhere a value is allowed
- The **single-value rule**, and how SQLite and Oracle disagree about breaking it
- **`IN` subqueries** — an inner query that returns a whole column to test membership against
- **`NOT IN` and the `NULL` trap** — the single most common subquery bug, and its two fixes
- **Correlated subqueries** — an inner query that references the outer row and re-runs for each one
- **`EXISTS` / `NOT EXISTS`** — testing whether a match exists at all, and why it's the safe anti-join
- When a **subquery** is clearer than a **join**, and when it's the other way around
- (security lens) how the `NOT IN` `NULL` bug becomes a *filter* bug, and why subqueries are an injection payload

## Scalar subqueries: one query returns one value

The simplest subquery returns exactly one value — a single row, single column. That's called a
**scalar subquery**, and you can drop it anywhere SQL expects a value. Our "above average" question
becomes one clean statement:

```sql
SELECT first_name, salary
FROM employee
WHERE salary > (SELECT AVG(salary) FROM employee);
```

```
+------------+--------+
| first_name | salary |
+------------+--------+
| Jan        | 110000 |
| Michael    | 90000  |
+------------+--------+
```

The database runs the inside first: `SELECT AVG(salary) FROM employee` produces `65625`. Then the outer
query behaves as if you'd typed `WHERE salary > 65625`, and only Jan and Michael clear that bar. The
parentheses are what mark the subquery; everything inside them is evaluated before the outer `WHERE`
sees it.

A scalar subquery isn't limited to the `WHERE` clause — it can sit in the `SELECT` list too, computing a
value for each row. Here's each person's distance from the company average:

```sql
SELECT first_name, salary,
       salary - (SELECT AVG(salary) FROM employee) AS diff_from_avg
FROM employee;
```

```
+------------+--------+---------------+
| first_name | salary | diff_from_avg |
+------------+--------+---------------+
| Jan        | 110000 | 44375.0       |
| Michael    | 90000  | 24375.0       |
| Dwight     | 62000  | -3625.0       |
| Jim        | 60000  | -5625.0       |
| Pam        | 42000  | -23625.0      |
| Andy       | 55000  | -10625.0      |
| Stanley    | 58000  | -7625.0       |
| Ryan       | 48000  | -17625.0      |
+------------+--------+---------------+
```

The subquery runs once, its `65625` gets subtracted from every row's salary, and the negatives are the
below-average folks. (The `.0` is there because `AVG` returns a decimal, so the difference is a decimal
too — round it with `ROUND(..., 0)` if you want it tidy, exactly as in Module 07.)

The word *scalar* is a promise: the subquery must return **one value**. Ask for `WHERE salary = (SELECT
salary FROM employee)` — a subquery that returns eight salaries — and you've broken that promise.

> **Dialect note:** engines disagree on how loudly they complain. **Oracle** (the exam's engine) raises
> a hard error — `ORA-01427: single-row subquery returns more than one row` — the instant a scalar
> subquery returns more than one. **SQLite** (this course's browser engine) is quietly permissive: it
> just uses the *first* row it happens to get and runs on, which can hand you a silently wrong answer.
> Don't rely on that. If the subquery can return more than one value, either constrain it to one or
> switch from `=` to `IN`, which is built for many values.

## IN subqueries: testing against a whole column

When the inner query legitimately returns *many* values, `IN` is the tool — the same `IN` from
Module 06, except the list comes from a subquery instead of being typed out. "Which employees are branch
managers?" The manager IDs live in `branch.mgr_id`; the names live in `employee`:

```sql
SELECT first_name, last_name
FROM employee
WHERE employee_id IN (SELECT mgr_id FROM branch);
```

```
+------------+-----------+
| first_name | last_name |
+------------+-----------+
| Jan        | Levinson  |
| Michael    | Scott     |
| Andy       | Bernard   |
+------------+-----------+
```

The subquery returns the manager IDs `100, 101, 105, NULL`, and the outer query keeps any employee whose
`employee_id` is in that set — Jan, Michael, and Andy. The `NULL` in the list (Buffalo has no manager)
does no harm here: nobody's `employee_id` equals it, so it's simply ignored. That harmlessness is about
to reverse completely.

## NOT IN and the NULL trap

Flip the question to "which employees are **not** managers?" The natural move is to negate:

```sql
SELECT first_name
FROM employee
WHERE employee_id NOT IN (SELECT mgr_id FROM branch);
```

```
+------------+
| first_name |
+------------+
+------------+
```

**Zero rows.** Not Dwight, not Jim, not Pam — nobody. That is almost certainly not what you wanted, and
it is one of the most notorious bugs in all of SQL. Here's why it happens. The subquery returns `100,
101, 105, NULL`, so for Dwight (id 102) the engine checks:

```
102 <> 100  AND  102 <> 101  AND  102 <> 105  AND  102 <> NULL
```

The first three are true — but `102 <> NULL` is not true and not false, it's **`UNKNOWN`** (from
Module 06: any comparison to `NULL` is unknown, because `NULL` means "could be anything, maybe even
102"). And `true AND true AND true AND UNKNOWN` collapses to `UNKNOWN`, which `WHERE` treats as "don't
include this row." Every single employee hits that same wall, so every row is excluded. One stray `NULL`
in the subquery silently emptied your result.

The fix is to make sure the subquery can't hand back a `NULL`:

```sql
SELECT first_name
FROM employee
WHERE employee_id NOT IN (SELECT mgr_id FROM branch WHERE mgr_id IS NOT NULL);
```

```
+------------+
| first_name |
+------------+
| Dwight     |
| Jim        |
| Pam        |
| Stanley    |
| Ryan       |
+------------+
```

Now it's right: the five non-managers. The rule to burn in: **`IN` shrugs off `NULL`s, but `NOT IN`
breaks on them.** Any time you write `NOT IN (subquery)`, either guarantee the subquery is `NULL`-free
with a `WHERE ... IS NOT NULL`, or — better — use `NOT EXISTS`, which you'll meet in a moment and which
doesn't have this failure mode at all.

## Correlated subqueries: the inner query looks at the outer row

Every subquery so far ran *once*, on its own, before the outer query started. A **correlated subquery**
is different: it refers to a column from the outer query, so it can't be computed in advance — it re-runs
for *each outer row*, using that row's values. The classic use is a per-group comparison. "Who earns more
than the average salary *of their own branch*?" — not the company average, each person measured against
their own branch:

```sql
SELECT first_name, salary, branch_id
FROM employee e
WHERE salary > (SELECT AVG(salary)
                FROM employee x
                WHERE x.branch_id = e.branch_id);
```

```
+------------+--------+-----------+
| first_name | salary | branch_id |
+------------+--------+-----------+
| Michael    | 90000  | 2         |
+------------+--------+-----------+
```

The inner query mentions `e.branch_id` — a column from the *outer* row's table alias `e`. So for each
employee, the engine computes the average salary of *that employee's* branch, then checks whether the
employee beats it. Walk it through: for Michael (branch 2) the inner query averages Scranton's five
salaries to `62400`, and `90000 > 62400`, so he's in. Dwight (also branch 2) is measured against the same
`62400`, and `62000` doesn't clear it. Jan is her branch's only member, so she's compared to her own
salary and can't exceed it; same for Andy. Ryan's `branch_id` is `NULL`, so the inner query finds no
matching rows, `AVG` of nothing is `NULL`, and `48000 > NULL` is unknown — he drops out. Only Michael
survives.

The tell for a correlated subquery is that alias reference across the boundary (`e.branch_id` inside a
query that's otherwise about `x`). It's more work for the database — conceptually one inner run per outer
row — but it expresses "compare each row to a group it belongs to" in a way a plain subquery can't.

## EXISTS and NOT EXISTS: does a match exist at all?

Sometimes you don't care *what* the subquery returns, only *whether it returns anything*. `EXISTS` takes
a subquery and is true the moment that subquery produces even one row. "Which branches have at least one
employee?"

```sql
SELECT branch_name
FROM branch b
WHERE EXISTS (SELECT 1 FROM employee e WHERE e.branch_id = b.branch_id);
```

```
+-------------+
| branch_name |
+-------------+
| Corporate   |
| Scranton    |
| Stamford    |
+-------------+
```

For each branch, the correlated inner query looks for an employee in it. Corporate, Scranton, and Stamford
each have someone, so `EXISTS` is true; Buffalo has nobody, so its subquery returns no rows and it's left
out. The `SELECT 1` is a convention — since `EXISTS` only checks for the *presence* of rows, it doesn't
matter what you select, so people write `1` (or `*`) to signal "the values are irrelevant, I only care
that something's here."

`NOT EXISTS` is the negation, and it's how you should write "find the rows with no match" — the anti-join
that `NOT IN` botched:

```sql
SELECT branch_name
FROM branch b
WHERE NOT EXISTS (SELECT 1 FROM employee e WHERE e.branch_id = b.branch_id);
```

```
+-------------+
| branch_name |
+-------------+
| Buffalo     |
+-------------+
```

Buffalo, correctly and with no `NULL` drama. This is the payoff of the earlier warning: `NOT EXISTS`
checks presence row by row, so a `NULL` in the data can't poison the whole result the way it does with
`NOT IN`. When you need "everything that *doesn't* match," reach for `NOT EXISTS` first.

## A subquery can also stand in for a table

One more place a subquery can go: the `FROM` clause, where it acts as a temporary table (often called a
**derived table**). This is handy when you want to aggregate an aggregate — say, the average branch
headcount:

```sql
SELECT ROUND(AVG(headcount), 2) AS avg_headcount
FROM (SELECT branch_id, COUNT(*) AS headcount
      FROM employee
      GROUP BY branch_id);
-- avg_headcount: 2.0
```

The inner query builds a little table of per-branch counts (`1, 5, 1, 1` across the four branch groups),
and the outer query averages that column. A derived table always needs to produce a result the outer
query can treat like any table — columns with names it can reference.

## Subquery or join? Choosing between them

Some questions can be written either way. "Employees who are branch managers" worked as an `IN` subquery
above; it's also a plain inner join of `employee` to `branch` on `employee_id = mgr_id`. Neither is
"correct" — but there are useful rules of thumb:

- Reach for a **join** when you want columns *from both tables* in the result. A subquery in `WHERE` can
  only filter the outer table; it can't add the branch's name to the output. If you need the manager's
  name *and* their branch, that's a join.
- Reach for a **subquery** when you only need to *filter* one table by a condition computed from another,
  and you don't want the other table's columns cluttering the result — or when the logic is naturally
  "compare each row to an aggregate" (a correlated subquery), which is awkward to express as a join.
- For "rows with no match," prefer **`NOT EXISTS`** over both a `NOT IN` subquery (the `NULL` trap) and a
  `LEFT JOIN ... WHERE ... IS NULL` (correct, but easy to get subtly wrong).

Don't agonize over it. As the source course puts it, a nested query is just one query informing another;
break the problem into "what does the inner question ask?" and "what does the outer question do with the
answer?" and the shape usually picks itself.

> **Security lens:** the `NOT IN` `NULL` bug isn't only a nuisance — it's a *filter* failure, and filters
> are often security controls. Picture an access check written as `WHERE user_id NOT IN (SELECT user_id
> FROM banned_users)`. The day one banned row has a `NULL` `user_id`, that `WHERE` evaluates to unknown
> for *everyone* and returns **zero rows** — which, depending on how the surrounding code reads an empty
> result, can silently let the wrong people through or lock everyone out. A control that quietly stops
> working is worse than one that fails loudly. Write anti-joins as `NOT EXISTS`, and never let a
> `NULL`-able column drive a `NOT IN`. Separately, remember that a subquery is executable code: in a
> boolean-based SQL injection, an attacker smuggles a whole `SELECT` into a `WHERE` — `... AND (SELECT
> ...) = 'x'` — to probe your database one true/false answer at a time. Same defense as always,
> parameterized queries, which you'll build in Module 11.

## Try it: predict the grid

This is the source course's own puzzle, adapted to our schema: "list the names of everyone in the branch
that Michael (employee 101) manages." It's a scalar subquery driving an outer filter.

```sql
SELECT first_name
FROM employee
WHERE branch_id = (SELECT branch_id FROM branch WHERE mgr_id = 101);
```

What names come back, and why does the `=` work here where it would have been dangerous a few sections
ago?

<details>
<summary>Reason it out, then click to check</summary>

**Five rows** — everyone in Scranton:

```
+------------+
| first_name |
+------------+
| Michael    |
| Dwight     |
| Jim        |
| Pam        |
| Stanley    |
+------------+
```

Inner query first: `SELECT branch_id FROM branch WHERE mgr_id = 101` finds the branch Michael manages —
Scranton, `branch_id = 2` — and returns that single value. The outer query then becomes `WHERE branch_id
= 2`, which matches all five Scranton employees (Michael included; he works there *and* manages it).

The `=` is safe here for one specific reason: `mgr_id = 101` matches exactly one branch, so the subquery
returns exactly one value — the single-value rule is satisfied. If Michael somehow managed two branches,
this subquery would return two rows, and `=` would break (a hard error in Oracle, a silently-wrong
first-row pick in SQLite). The robust habit when a subquery *might* return more than one value is to
switch `=` to `IN` — `WHERE branch_id IN (SELECT ...)` — which handles one value or many without
complaint.

</details>

## Recap

A subquery is a query nested inside another; the database runs the inner one and feeds its result to the
outer one. A **scalar subquery** returns a single value and can appear anywhere a value is legal (`WHERE`,
`SELECT`, `FROM`) — but it *must* stay single-valued, and while Oracle errors when it doesn't, SQLite
silently uses the first row. An **`IN` subquery** tests membership against a whole column the inner query
returns, and it tolerates `NULL`s in that column — whereas **`NOT IN` breaks on a single `NULL`**,
returning no rows, which you fix with `IS NOT NULL` in the subquery or (better) by rewriting as `NOT
EXISTS`. A **correlated subquery** references the outer row and conceptually re-runs per row, which is how
you compare each row to a group it belongs to, like each employee against their own branch's average.
**`EXISTS`/`NOT EXISTS`** test only whether a match is present and are the safe way to write "has a match"
/ "has no match." Choose a **join** when you need columns from both tables, a **subquery** when you're only
filtering one — and reach for `NOT EXISTS` for anti-joins, because a filter that silently fails on `NULL`
is a genuine security risk when that filter is an access control.

## Quiz seeds

- Q: `SELECT first_name FROM employee WHERE salary > (SELECT AVG(salary) FROM employee)` returns Jan and
  Michael. In what order does the database evaluate this?
  - ✅ The inner subquery runs first, producing the average (`65625`); the outer query then filters as if
    you'd written `WHERE salary > 65625`
  - ❌ The outer query runs first and the subquery re-checks each row — that describes a *correlated*
    subquery; this plain scalar subquery is computed once, up front
  - ❌ Both run at the same time and the results are merged — SQL evaluates the inner query first and
    substitutes its single value into the outer one

- Q: `WHERE employee_id NOT IN (SELECT mgr_id FROM branch)` returns zero rows even though most employees
  aren't managers. Why?
  - ✅ `branch.mgr_id` includes a `NULL` (Buffalo has no manager); comparing anything to `NULL` is
    `UNKNOWN`, so `NOT IN` is never true for any row and everything is excluded
  - ❌ `NOT IN` is not valid SQL with a subquery — it's valid; the problem is the `NULL` inside the
    subquery's result, not the syntax
  - ❌ Every employee actually is a manager — only three are; the empty result is the `NULL` trap, not a
    reflection of the data

- Q: What's the safest way to rewrite "branches with no employees," and why?
  - ✅ `WHERE NOT EXISTS (SELECT 1 FROM employee e WHERE e.branch_id = b.branch_id)` — `NOT EXISTS` checks
    presence row by row and can't be poisoned by a `NULL` the way `NOT IN` can
  - ❌ `WHERE branch_id NOT IN (SELECT branch_id FROM employee)` — this is exactly the fragile form; the
    employee list contains a `NULL` (Ryan), so it hits the `NOT IN` trap
  - ❌ There's no way to express "no match" in SQL — `NOT EXISTS` (and a `LEFT JOIN ... IS NULL`) both do
    it; `NOT EXISTS` is the most robust

- Q: What makes a subquery *correlated*, and what's the consequence?
  - ✅ It references a column from the outer query (like `e.branch_id`), so it can't be computed once up
    front — it conceptually re-runs for each outer row
  - ❌ It's correlated whenever it appears in the `WHERE` clause — location doesn't make it correlated;
    referencing an outer-row column does
  - ❌ Correlated means it returns multiple columns — the number of columns is unrelated; correlation is
    about the reference back to the outer row

- Q: You need each employee's name *and* their branch's city in one result. Is a `WHERE` subquery enough?
  - ✅ No — a `WHERE` subquery can only *filter* the employee rows; to put the branch's city in the output
    you need a join, which can pull columns from both tables
  - ❌ Yes, just add the branch city to the subquery's `SELECT` — a subquery in `WHERE` returns values for
    the comparison only; its columns don't appear in the outer result
  - ❌ No, and it's impossible in SQL — it's very possible, with a join (Module 08); the subquery just
    isn't the right tool for adding columns

## Up next

You've spent four modules *reading* data — filtering, grouping, joining, nesting. **Module 10 — Data
Manipulation & Transactions** is about *changing* it: `INSERT` to add rows, `UPDATE` to modify them,
`DELETE` to remove them, and then the safety net that makes those operations trustworthy — `COMMIT` and
`ROLLBACK`, the transaction controls that let you undo a mistake before it becomes permanent and answer
the nervous question "did my `DELETE` actually do what I meant?"
