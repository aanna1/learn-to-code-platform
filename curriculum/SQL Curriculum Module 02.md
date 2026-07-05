# Module 02 — The Relational Model & Keys

> Tags: `[27200]`

Every relational database you'll ever touch is built from exactly two ideas: tables, and the
keys that connect them. That's it. Once those two ideas are solid, everything from here on —
querying, joining, designing a whole schema — is just variations on this module.

By the end you'll be able to look at a table and name its primary key, explain the difference
between a key that means something in the real world and one that doesn't, and — the part that
actually makes databases *relational* — use a foreign key to link one table to another instead
of cramming everything into one.

## Prerequisites

Module 01 — specifically, that a relational database stores data in tables made of rows and
columns, the way a spreadsheet does.

## What you'll learn

- The difference between a table's columns (attributes) and rows (entries), precisely
- What a primary key is, why every table needs exactly one, and how it solves the "two rows
  that look identical" problem
- The difference between a surrogate key and a natural key
- What a foreign key is and how it links one table to another — including a table linking to
  *itself*
- Why real databases split information across several small tables instead of one giant one

## Tables: rows and columns, precisely

Picture a table of students:

```
students
+------------+----------+-----------+
| student_id | name     | major     |
+------------+----------+-----------+
| 1          | Jack     | Biology   |
| 2          | Kate     | Sociology |
| 3          | Claire   | English   |
+------------+----------+-----------+
```

Every table in a relational database has two parts, and it's worth being precise about which
word means which:

- A **column** defines a single *attribute* — one kind of fact every row will have. `name` and
  `major` are columns; every student has exactly one of each.
- A **row** is a single *entry* — one actual student. Reading across a row tells you everything
  the table knows about that one thing.

So "the `major` column" means the whole vertical strip of majors, and "Kate's row" means the
one horizontal slice with her ID, her name, and her major in it. This vocabulary sounds obvious
written down, but get comfortable saying it out loud — the rest of this course, and the exam,
constantly asks you to reason about "this column" versus "this row," and mixing them up is an
easy way to lose points on a question you actually understood.

## The primary key: what makes a row unique

Here's a problem. Add two more students to the table above:

```
+------------+----------+-----------+
| student_id | name     | major     |
+------------+----------+-----------+
| 1          | Jack     | Biology   |
| 4          | Jack     | Biology   |
+------------+----------+-----------+
```

Two different students, same name, same major. If someone says "update Jack's major," which
Jack? Name and major aren't enough to pin down a specific row — and in a real school, this
isn't a rare edge case, it's Tuesday.

Every table needs one column (or small set of columns) guaranteed to be different for every
single row. That column is the **primary key**. In the table above, `student_id` is it: even
though the two Jacks are identical in every other column, their IDs — 1 and 4 — are not. The
primary key is how you say "this exact row, and no other" without ambiguity.

A primary key can be a number, a string, almost anything — the one hard rule is that no two rows
in the table are ever allowed to share one. There are two flavors you'll see constantly:

**Surrogate keys** have no meaning outside the database — they're just an ID the system made
up to keep rows distinct. `student_id` is one. Employee ID 100 doesn't mean anything about the
employee; it's just a label the database invented.

**Natural keys** already mean something in the real world. A Social Security number uniquely
identifies a person whether or not a database exists at all — using it as a primary key means
reusing a real-world identifier instead of inventing one.

```
-- surrogate key: made up by the database, means nothing outside it
employee (employee_id PK, first_name, last_name)

-- natural key: already unique in the real world
employee (ssn PK, first_name, last_name)
```

> **Watch out:** natural keys feel convenient because they're "already unique," but they're
> riskier than they look — email addresses get reassigned, SSNs turn out to have edge cases,
> license plates get reissued. Surrogate keys (a plain auto-generated ID) are the safer default
> for most tables you design, precisely because they carry no real-world meaning that could
> quietly turn out to be wrong. You'll design your own keys starting in Module 03 — this is
> the rule of thumb to bring with you.

## The foreign key: linking one table to another

Now picture an `employee` table that includes which office branch each person works in:

```
employee
+-------------+------------+-----------+-----------+
| employee_id | first_name | last_name | branch_id |
+-------------+------------+-----------+-----------+
| 100         | Jan        | Levinson  | 1         |
| 101         | Michael    | Scott     | 2         |
| 102         | Josh       | Porter    | 3         |
+-------------+------------+-----------+-----------+

branch
+-----------+-----------+
| branch_id | name      |
+-----------+-----------+
| 1         | Corporate |
| 2         | Scranton  |
| 3         | Stamford  |
+-----------+-----------+
```

`branch_id` in the `employee` table isn't the employee's own primary key — it's *the branch
table's* primary key, borrowed and stored on a different table. That's a **foreign key**: an
attribute whose value points at the primary key of a row in another table. Michael Scott's
`branch_id` is `2`, which is the `branch` table's primary key for Scranton — so that one column
is what tells you Michael works in Scranton, without repeating "Scranton" as text anywhere on
the employee table.

This is the whole reason the word *relational* is in "relational database." Tables don't just
sit next to each other — foreign keys are the mechanism that *relates* them. And a table can
hold more than one foreign key: `branch` above could also have a `manager_id` foreign key
pointing back at `employee`, to record which employee manages each branch. Two tables, pointing
at each other in both directions, each with their own job.

A foreign key doesn't even have to point at a *different* table. Add a `supervisor_id` column
to `employee` itself:

```
employee
+-------------+------------+---------------+
| employee_id | first_name | supervisor_id |
+-------------+------------+---------------+
| 100         | Jan        | NULL          |
| 101         | Michael    | 100           |
| 103         | Angela     | 101           |
+-------------+------------+---------------+
```

Angela's `supervisor_id` is `101` — Michael's own `employee_id`, in the very same table. This is
called a **self-referencing foreign key**, and it's how you model "employees have supervisors,
and supervisors are also employees" without a separate table just for supervisors. Jan's
`supervisor_id` is `NULL` because she doesn't report to anyone in this data — a foreign key
pointing at nothing is allowed, it just means "no relationship here."

## Why split into multiple tables at all?

At this point a fair question is: why not just put the branch's name, address, and phone number
directly on every employee row, and skip the foreign key entirely?

Try it and see what breaks. If ten employees work at the Scranton branch, "Scranton, 456 Main
Street, 555-0100" now lives on ten separate rows. The branch changes its phone number, and
suddenly you need to find and update it in ten places — miss one, and your database now
disagrees with itself about the branch's own phone number. Worse, if the Scranton branch has
zero employees on some particular day, is there anywhere in the database that still remembers
Scranton exists at all?

A foreign key fixes all of this by storing branch information *once*, in the `branch` table, and
having every employee point at it. Update the phone number once, and every employee who works
there is automatically "updated" too — there was never a second copy to forget. This idea — one
fact, stored in exactly one place, referenced everywhere it's needed — is the seed of
**normalization**, which gets a full module of its own (Module 04) once you've learned to model
relationships properly in Module 03. For now, just internalize the instinct: if you notice
yourself about to repeat the same chunk of information on every row, that's usually a sign it
belongs in its own table instead.

## Try it: predict the row

```
employee
+-------------+------------+-----------+
| employee_id | first_name | branch_id |
+-------------+------------+-----------+
| 100         | Jan        | 1         |
| 101         | Michael    | 2         |
| 102         | Andy       | 3         |
+-------------+------------+-----------+

branch
+-----------+----------+
| branch_id | name     |
+-----------+----------+
| 1         | Corporate|
| 2         | Scranton |
| 3         | Stamford |
+-----------+----------+
```

Which branch does Andy work at?

<details>
<summary>Predict the answer, then click to check</summary>

**Stamford.** Andy's `branch_id` is `3`, and in the `branch` table, the row with `branch_id = 3`
is Stamford. That's the entire mechanism of a foreign key: follow the value from one table to
the matching primary key in the other, and read off whatever you need from that row. In Module
08 you'll write a single query — a **join** — that does exactly this lookup for every employee
at once, instead of doing it by hand.

</details>

## Recap

A table stores rows of related data, organized into columns that each hold one attribute. Every
table needs a primary key — one column (or combination of columns) guaranteed unique across
every row — so that no two entries can ever be confused, even if every other column matches. A
foreign key stores another table's primary key as a way of pointing at a specific row somewhere
else, which is the actual mechanism that makes a relational database *relational*; it can point
at a different table, or, self-referencing, back at rows in its own table. And the reason real
schemas are made of several small tables instead of one big one is to avoid storing the same
fact in more than one place — a rule of thumb that becomes a formal process, normalization, in
Module 04.

## Quiz seeds

- Q: A `students` table has two rows with identical `name` and `major` values. How can you tell
  them apart?
  - ✅ By their primary key — it's guaranteed to be unique for every row, even if every other
    column matches
  - ❌ You can't — duplicate data means duplicate rows, and the table is just broken.
    In a well-designed table the primary key still distinguishes them
  - ❌ By the order the rows were inserted — row order isn't a reliable way to identify data in
    a relational database

- Q: What's the difference between a surrogate key and a natural key?
  - ✅ A surrogate key has no meaning outside the database (like an auto-generated ID); a
    natural key is already a unique real-world identifier (like a Social Security number)
  - ❌ A surrogate key is always a number and a natural key is always text — the format isn't
    what distinguishes them, where the value's meaning comes from is
  - ❌ Only one table in a database is allowed to use a surrogate key — any table can use
    either kind

- Q: What does a foreign key actually store?
  - ✅ The primary key value of a row in another table (or, for a self-referencing key, another
    row in the same table)
  - ❌ A copy of every column from the related row — that would duplicate data, which is the
    exact problem foreign keys are meant to avoid
  - ❌ A password that controls access to the related table — foreign keys are about linking
    data, not about security permissions

## Up next

Module 03 turns these two ideas — tables and keys — into a formal design tool: the **ER
diagram**. You'll learn to model entities, attributes, and relationships (including the
identifying-vs-non-identifying distinction the exam cares about) *before* a single table gets
created, the way a real database gets designed from a set of business requirements.
