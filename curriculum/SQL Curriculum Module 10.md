# Module 10 — Data Manipulation & Transactions

> Tags: `[27200]`

Nine modules in, you've become fluent at *reading* a database — filtering, sorting, grouping, joining,
nesting. But you never put any of that data there, and you never changed a word of it. This module is
where you pick up the other half of SQL: the three statements that *write* to the database — `INSERT`
to add rows, `UPDATE` to change them, `DELETE` to remove them — collectively called **DML**, Data
Manipulation Language.

Writing is riskier than reading. A `SELECT` with a mistake gives you a wrong answer you can just run
again; an `UPDATE` with a mistake *changes your data*, and a single missing word can overwrite every row
in a table. So the second half of this module is the safety net that makes writing trustworthy:
**transactions** — `COMMIT` to make your changes permanent and `ROLLBACK` to undo them, so a mistake is
recoverable instead of catastrophic. This is a heavily emphasized exam topic and, honestly, the most
important habit you'll build in the whole course.

Same two tables — but for the first time, watch them *change* as statements run:

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

## Prerequisites

Modules 05 (`CREATE TABLE`, constraints, and foreign keys — those constraints decide which writes the
database *accepts*, and the FK you defined controls what happens when you delete a referenced row) and
06 (`WHERE` — because in an `UPDATE` or `DELETE`, the `WHERE` clause is what decides which rows get
changed, and getting it wrong is the whole danger of this module).

## What you'll learn

- **`INSERT`** — adding new rows, in both the full and column-list forms
- **`UPDATE`** — changing existing rows, one column or several at once
- The single most dangerous mistake in SQL: an **`UPDATE` or `DELETE` with no `WHERE`**
- **`DELETE`** — removing rows
- **Transactions** — `COMMIT` to finalize, `ROLLBACK` to undo, and why *atomicity* matters
- **Autocommit** vs. explicit transactions, and how Oracle and SQLite differ sharply here
- What happens when you **delete a row another table points at** (the FK behavior from Module 05)
- (security lens) why writes need auditing, least privilege, and why an injected `UPDATE` is a nightmare

## INSERT: adding rows

`INSERT` puts a new row into a table. The most explicit form names the table and lists a value for
every column, in table order:

```sql
INSERT INTO branch VALUES (5, 'Utica', NULL);
```

That adds a fifth branch — Utica, no manager yet. It works, but it's brittle: you have to know the exact
column order and supply *every* column, so if the table changes later, the statement silently means
something different. The safer, clearer form names the columns explicitly:

```sql
INSERT INTO employee (employee_id, first_name, last_name, branch_id, salary, hire_date)
VALUES (108, 'Kelly', 'Kapoor', 2, 45000, '2007-08-01');
```

```
employee (new row added)
+-------------+------------+-----------+-----------+--------+
| employee_id | first_name | last_name | branch_id | salary |
+-------------+------------+-----------+-----------+--------+
| ...         | ...        | ...       | ...       | ...    |
| 107         | Ryan       | Howard    | NULL      | 48000  |
| 108         | Kelly      | Kapoor    | 2         | 45000  |
+-------------+------------+-----------+-----------+--------+
```

Now the order of your values just has to match the order of *your own column list*, and any column you
leave out gets its default (or `NULL`, or an auto-generated key — exactly the constraints you set in
Module 05). This is the form to prefer in real work.

And the constraints from Module 05 are live guards here. Try to insert an employee whose `employee_id`
is `100` — already taken — and the primary key rejects it:

```sql
INSERT INTO employee (employee_id, first_name) VALUES (100, 'Clone');
-- Error: UNIQUE constraint failed: employee.employee_id
```

A `NOT NULL` column with no value, a `CHECK` that fails, a `FOREIGN KEY` pointing at a branch that
doesn't exist — each one blocks the insert the same way. Those rejections aren't the database being
difficult; they're it refusing to let you create data that breaks the rules you designed.

## UPDATE: changing existing rows

`UPDATE` modifies rows that already exist. The shape is `UPDATE table SET column = value WHERE
condition`. Say Ryan finally gets assigned to Stamford (branch 3):

```sql
UPDATE employee
SET branch_id = 3
WHERE employee_id = 107;
```

The database reports `1 row affected` — it found the one row matching `employee_id = 107` and changed
its `branch_id` from `NULL` to `3`. That `WHERE` is doing the critical work: it picks *which* rows get
the change. You can change several columns at once by separating them with commas:

```sql
UPDATE employee
SET salary = 50000, branch_id = 3
WHERE employee_id = 107;
```

One statement, two columns updated, still only for Ryan. And the condition can be as rich as any `WHERE`
you've written — ranges, `OR`, `IN`, anything from Module 06. A company-wide raise for everyone in
Scranton:

```sql
UPDATE employee
SET salary = salary + 3000
WHERE branch_id = 2;
```

Note `salary = salary + 3000` — the new value is computed from the old one, per row, so each Scranton
employee's own salary goes up by 3000. That reports `5 rows affected`.

## The most dangerous mistake in SQL: forgetting WHERE

Here is the one to burn into memory. The `WHERE` clause in an `UPDATE` is **optional** — and if you
leave it off, the update applies to *every row in the table*:

```sql
UPDATE employee
SET salary = 0;          -- NO WHERE
```

```
8 rows affected. Every salary in the company is now 0.
```

There's no confirmation prompt, no "are you sure?" The database does exactly what you said — set every
salary to zero — because a missing `WHERE` means "all rows," not "no rows." The same trap sits under
`DELETE`. This is the classic career-defining production incident: someone means to update or delete one
row, the `WHERE` doesn't get typed (or gets typed wrong), and the whole table is overwritten in a blink.

The habit that saves you: **write the `WHERE` as a `SELECT` first.** Before you run `UPDATE employee SET
salary = 0 WHERE employee_id = 107`, run `SELECT * FROM employee WHERE employee_id = 107` and confirm it
returns the *exact* rows you intend to change — just those, no more. Only then swap `SELECT *` for
`UPDATE ... SET ...`. It takes five seconds and it's the difference between fixing one row and
explaining to your boss why everyone's salary is zero.

## DELETE: removing rows

`DELETE` removes whole rows, and it works just like `UPDATE` — a `WHERE` picks the targets:

```sql
DELETE FROM employee
WHERE employee_id = 107;
```

`1 row affected` — Ryan is gone, seven employees remain. The condition can match a group, too:

```sql
DELETE FROM employee
WHERE branch_id = 2;      -- removes all five Scranton employees
```

And the same fatal shortcut applies: leave off the `WHERE` entirely and you empty the table.

```sql
DELETE FROM employee;     -- deletes EVERY row. The table still exists, but it's empty.
```

`DELETE FROM employee` isn't an error and it isn't undone by closing the window — it's a valid command to
remove every row, and (outside a transaction) it's immediate and permanent. Which is the perfect reason
to meet the safety net.

## Transactions: COMMIT and ROLLBACK

A **transaction** groups one or more statements into a single all-or-nothing unit. Nothing inside it is
permanent until you say so with **`COMMIT`**, and at any point before that you can throw the whole thing
away with **`ROLLBACK`**, returning the database to exactly how it looked when the transaction started.

The reason transactions exist is *atomicity* — "all or nothing." The textbook example is a bank transfer:
move $100 from account A to B, and that's really two writes — subtract 100 from A, add 100 to B. If the
system crashes *between* them, A has lost $100 that never arrived at B. A transaction says "these two
writes are one indivisible operation": either both happen or neither does, so the money can never
vanish in the gap.

You open a transaction with `BEGIN` (or `START TRANSACTION`), do your writes, then either seal them or
discard them:

```sql
BEGIN;
UPDATE account SET balance = balance - 100 WHERE id = 'A';
UPDATE account SET balance = balance + 100 WHERE id = 'B';
COMMIT;      -- both updates become permanent together
```

If anything looks wrong before the `COMMIT`, `ROLLBACK` undoes *everything* since `BEGIN`:

```sql
BEGIN;
DELETE FROM employee;              -- oops, forgot the WHERE — table looks empty now
ROLLBACK;                          -- ...and it's all back. Crisis averted.
```

That second example is the direct answer to the nervous question "did my `DELETE` actually do what I
meant?" Inside a transaction, you can run the statement, `SELECT` to check the result, and if it's wrong,
`ROLLBACK` as if it never happened. Only `COMMIT` makes it real. Transactions turn a destructive,
one-shot command into something you can inspect and reverse.

## Autocommit, and a big dialect difference

So why haven't you needed `BEGIN`/`COMMIT` until now? Because most systems run in **autocommit** mode by
default: each statement is its own automatically-committed transaction, made permanent the instant it
finishes. That's convenient for one-off queries and exactly why a bare `DELETE FROM employee` is
immediately permanent — it auto-committed. To get the safety net, you *opt in* by wrapping your work in
`BEGIN ... COMMIT`, which suspends autocommit until you close the transaction yourself.

> **Dialect note:** this is one of the sharpest splits between engines, and the exam runs on the strict
> one. **Oracle** (the exam's environment) does **not** autocommit DML — after an `INSERT`/`UPDATE`/
> `DELETE`, the change is *pending* and invisible to other users until you explicitly `COMMIT`, and a
> `ROLLBACK` (or disconnecting badly) discards it. So in Oracle, `COMMIT` isn't optional ceremony; it's
> how your changes become real, and forgetting it means your work silently disappears. (DDL like `CREATE
> TABLE` is the exception — Oracle auto-commits that.) **SQLite** (this course's browser engine) and
> **MySQL/InnoDB** autocommit each statement by default, so in the IDE an `UPDATE` takes effect
> immediately unless you wrap it in `BEGIN ... COMMIT`. On a handwritten exam, assume the Oracle model:
> if a question involves changing data and you don't write `COMMIT`, the change hasn't stuck.

## Deleting a row that another table points at

There's a special hazard in `DELETE` that ties back to the foreign keys from Module 05. Our `branch.mgr_id`
points at `employee.employee_id`. So what happens if you delete an employee who manages a branch — say
Michael (101), Scranton's manager? The branch's `mgr_id = 101` would suddenly reference an employee who
no longer exists: a *dangling* reference, exactly the broken state foreign keys are meant to prevent.

The database's response depends on the rule you attached to the foreign key when you created the table:

- **Restrict (the default):** the delete is **blocked** — `FOREIGN KEY constraint failed` — because
  removing the row would orphan a reference. You must deal with the referencing rows first. This is the
  safe default: it refuses to let you create broken data.
- **`ON DELETE SET NULL`:** the referencing column is set to `NULL` instead. Delete Scranton's branch and
  every employee who pointed at it gets `branch_id = NULL` — they survive, just unassigned. (Good when the
  reference is optional.)
- **`ON DELETE CASCADE`:** the referencing rows are **deleted too**, in a chain. Delete a branch and every
  row that depended on it goes with it. (Necessary when the child row is meaningless without its parent —
  e.g., a link row whose foreign key is *part of its own primary key*, since a primary key can't be
  `NULL`.)

You choose the behavior once, in the `CREATE TABLE`, and the database enforces it on every delete
thereafter. The point for *this* module is that a `DELETE` isn't always a local act — it can be blocked,
or it can ripple into other tables, depending on how the schema was designed.

> **Dialect note:** SQLite has a surprising default — **foreign key enforcement is OFF** unless you run
> `PRAGMA foreign_keys = ON` first. So in the browser IDE, a delete that *should* be blocked by an FK may
> quietly succeed and leave a dangling reference, which won't happen on Oracle or MySQL/InnoDB where
> enforcement is on by default. If you're testing FK behavior in the IDE and it seems not to care, that
> pragma is why.

> **Security lens:** everything in this module is a *write*, and writes are where an attacker does real
> damage — reading your data is bad, but silently rewriting it is worse. The accidental "forgot the
> `WHERE`" disaster is the exact same shape as a malicious one: an injected `UPDATE employee SET salary
> = ... ` or `DELETE FROM employee` can wipe or alter a whole table through a vulnerable input box
> (Module 11). Three defenses follow directly from this module. First, **transactions plus backups make
> writes recoverable** — a change you can `ROLLBACK`, or restore from a backup, is a change an attacker
> (or a slip of the keyboard) can't make permanent. Second, **least privilege**: the account your
> application connects with usually has no business running `DELETE` or `UPDATE` on sensitive tables, so
> don't grant it — you'll set exactly these permissions with `GRANT`/`REVOKE` in Module 12. Third,
> **audit logging**: because DML changes state, integrity depends on being able to answer "who changed
> this row, and when?" — which is why regulated databases log every write. Reads leak data; writes
> destroy trust in it, so they earn the heavier controls.

## Try it: predict the state

Transactions trip people up because the "undo" is total. Predict what the final `SELECT` returns:

```sql
BEGIN;
UPDATE employee SET salary = salary + 5000;          -- everyone gets +5000
UPDATE employee SET salary = 0 WHERE employee_id = 101;   -- Michael zeroed out
ROLLBACK;
SELECT first_name, salary FROM employee WHERE employee_id IN (100, 101);
```

Two updates ran, *then* a rollback. What are Jan's and Michael's salaries at the end?

<details>
<summary>Decide before peeking</summary>

**Their original salaries — nothing changed:**

```
+------------+--------+
| first_name | salary |
+------------+--------+
| Jan        | 110000 |
| Michael    | 90000  |
+------------+--------+
```

The trap is thinking one of the updates "already happened" so *some* new value sticks — that Jan keeps
her +5000, or Michael stays at 0. Neither does. `ROLLBACK` discards **everything** since `BEGIN`, as a
single unit: both `UPDATE`s vanish together and the table is exactly as it was before the transaction
opened. That's the whole promise of atomicity — the changes inside a transaction are all-or-nothing, and
`ROLLBACK` chooses "nothing." Had the last line been `COMMIT` instead, *both* updates would have stuck
(Jan at 115000, Michael at 0), again together.

</details>

## Recap

DML is the write half of SQL. `INSERT` adds rows — prefer the column-list form `INSERT INTO t (cols...)
VALUES (...)` over the positional one, and remember the Module 05 constraints (`PRIMARY KEY`, `NOT NULL`,
`CHECK`, `FOREIGN KEY`) will reject any row that breaks them. `UPDATE t SET col = val WHERE ...` changes
existing rows and can set several columns at once, and `DELETE FROM t WHERE ...` removes rows — in both,
the `WHERE` decides which rows are affected, and **omitting it hits every row in the table**, which is
the most dangerous mistake in SQL (defend against it by running the `WHERE` as a `SELECT` first). A
**transaction** (`BEGIN ... COMMIT`/`ROLLBACK`) makes writes safe: changes are pending until `COMMIT`
makes them permanent, and `ROLLBACK` undoes the entire transaction as one atomic all-or-nothing unit.
Most engines **autocommit** each statement by default and you opt into transactions explicitly — but
**Oracle** (the exam) leaves DML pending until you `COMMIT`, so on the exam an uncommitted change hasn't
stuck. Finally, deleting a row another table references is governed by the foreign key's rule from
Module 05 — blocked by default, or `SET NULL`, or `CASCADE` — and note SQLite doesn't even enforce
foreign keys unless you switch the pragma on.

## Quiz seeds

- Q: Which form of `INSERT` is safer for real work, and why?
  - ✅ `INSERT INTO employee (employee_id, first_name, ...) VALUES (...)` — naming the columns means the
    statement doesn't silently break if the table's column order changes and lets you omit columns that
    have defaults
  - ❌ `INSERT INTO employee VALUES (...)` — it's shorter, so it's safer — shorter, but brittle: it
    depends on exact column order and requires a value for every column
  - ❌ They're identical in every way — the column-list form is more robust to schema changes and allows
    partial inserts; the positional form does neither

- Q: You run `UPDATE employee SET salary = 0;` with no `WHERE`. What happens?
  - ✅ Every row in the table is updated — all eight salaries become 0 — because a missing `WHERE` means
    "all rows," and there's no confirmation prompt
  - ❌ Nothing — an `UPDATE` without `WHERE` is a syntax error — it's valid SQL; the missing `WHERE` is
    exactly what makes it apply to the whole table
  - ❌ Only the first row is updated — `UPDATE` with no `WHERE` affects every row, not just one

- Q: Inside `BEGIN; DELETE FROM employee; ROLLBACK;`, what's the state of the table afterward?
  - ✅ Unchanged — all rows are still there; `ROLLBACK` undoes every change since `BEGIN`, so the delete
    is discarded as if it never ran
  - ❌ Empty — the `DELETE` already removed the rows before the rollback — `ROLLBACK` reverses the
    delete; nothing inside the transaction is permanent until `COMMIT`
  - ❌ Only some rows remain, at random — a rollback restores the full pre-transaction state, not a
    partial one

- Q: On the Oracle database the exam uses, you `UPDATE` a row and then close your session without a
  `COMMIT`. What happened to your change?
  - ✅ It was discarded — Oracle keeps DML pending until an explicit `COMMIT`, so an uncommitted change is
    rolled back and never becomes permanent
  - ❌ It was saved automatically — Oracle autocommits every statement — that describes SQLite/MySQL
    defaults, not Oracle; Oracle requires an explicit `COMMIT` for DML
  - ❌ It's still pending and will apply next time you log in — an unclean disconnect rolls back
    uncommitted work; it doesn't persist across sessions

- Q: A `branch` row's `mgr_id` points at an `employee`. You try to `DELETE` that employee. With foreign
  keys enforced and no special rule set, what happens?
  - ✅ The delete is blocked with a foreign-key error, because removing the employee would leave the
    branch's `mgr_id` pointing at a row that no longer exists
  - ❌ The employee is deleted and the branch's `mgr_id` automatically becomes `NULL` — that only happens
    if the FK was defined `ON DELETE SET NULL`; the default is to block
  - ❌ Both the employee and the branch are deleted automatically — that's `ON DELETE CASCADE`, which must
    be explicitly declared; it isn't the default

## Up next

You now know every way to read *and* write a database — which means you also have every tool an attacker
would love to get their hands on. **Module 11 — SQL Injection & Secure Query Practices** is the security
heart of the course: how an application that builds queries by pasting user input lets an attacker turn a
harmless-looking search box into `... OR 1=1` (dumping every row) or an injected `UPDATE`/`DELETE` that
rewrites your data — and the one real fix, parameterized queries, that shuts the whole class of attack
down. Everything you learned about `WHERE`, `UNION`, and now `UPDATE`/`DELETE` is about to be shown from
the other side of the keyboard.
