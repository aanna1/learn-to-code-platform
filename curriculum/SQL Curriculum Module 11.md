# Module 11 — SQL Injection & Secure Query Practices

> Tags: `[SEC]`

For ten modules you've been the person writing the SQL. This module shows you the other side of the
keyboard — where an *attacker* writes part of your query for you, and the database runs it without ever
knowing the difference. **SQL injection** is that attack: it's what happens when data from a user
(a login box, a search field, a URL) gets stitched into a SQL statement as if it were code. It has sat
at or near the top of the OWASP list of web-application risks for two decades, it's how an enormous
share of real breaches actually happen, and — this is the good news — it has one clean, well-understood
fix. By the end of this module you'll be able to look at a query and see the hole, exploit it in your
head, and close it for good.

This is also where the CNIT 27200 catalog's phrase **"programmatic access to a database and practical
issues that database developers must handle"** comes to life. Injection is fundamentally a
*programmatic* problem: it's not a flaw in SQL, it's a flaw in how *application code assembles* SQL from
strings. So this module reads a little differently from the others — the villain isn't a query you type,
it's a line of program code that builds one.

## Prerequisites

Modules 06 (`WHERE`, `LIKE`), 08 (`UNION` — the exfiltration attack is a `UNION` you didn't authorize),
and 10 (`UPDATE`/`DELETE` — an injected write is exactly those statements, turned against you). You'll
see all three used as weapons.

## What you'll learn

- What SQL injection is, and why building queries by *string concatenation* is the root cause
- **Authentication bypass** — logging in as anyone with `' OR '1'='1' --`, walked through character by character
- **`UNION`-based exfiltration** — stealing another table's data through a search box
- **Injected writes and blind injection** — and the "stacked query" caveat
- The one real fix: **parameterized queries / prepared statements**, and *why* they work categorically
- **Defense in depth** — allowlist input validation, least privilege, safe error handling
- Why validation and escaping are *supplements*, never *substitutes*, for parameterizing

## The root cause: gluing strings into a query

Almost every web app runs SQL on the user's behalf. Log in, and somewhere on a server a line of code
builds a query out of what you typed. Here's the fatal way to do it — pasting the input straight into
the query text:

```python
# VULNERABLE — do not do this
username = request.form["username"]
password = request.form["password"]
query = "SELECT id, username, role FROM users " \
        "WHERE username = '" + username + "' AND password = '" + password + "'"
db.execute(query)
```

For a normal login (`username = admin`, `password = s3cr3t`) that builds exactly what you'd expect:

```sql
SELECT id, username, role FROM users WHERE username = 'admin' AND password = 's3cr3t'
```

Here's the whole problem in one sentence: **by the time that string reaches the database, there is no
boundary left between the developer's SQL and the user's input — it's all just one line of text.** The
database faithfully parses the entire thing as a command. If the user can sneak SQL *syntax* into their
input, they're no longer filling in a value — they're rewriting your query. Everything below is a
consequence of that single mistake.

We'll attack a small `users` table (a credentials table is the classic target):

```
users
+----+-----------+----------+-------+
| id | username  | password | role  |
+----+-----------+----------+-------+
| 1  | admin     | s3cr3t   | admin |
| 2  | jhalpert  | pam4ever | user  |
| 3  | dwight    | beets    | user  |
+----+-----------+----------+-------+
```

## Attack 1: logging in as anyone

The attacker doesn't type a username. They type SQL. Into the **username** box, put:

```
' OR '1'='1' --
```

Now substitute that into the vulnerable template and watch what the database actually receives:

```sql
SELECT id, username, role FROM users WHERE username = '' OR '1'='1' --' AND password = 'whatever'
```

Read it the way the parser does. The attacker's leading `'` closes the empty username string early. Then
`OR '1'='1'` adds a condition that is *always true*. Then `--` begins a SQL comment, so everything after
it — ` ' AND password = '...'` — is **ignored entirely**, password check and all. What's left is:

```sql
SELECT id, username, role FROM users WHERE username = '' OR '1'='1'
```

`'1'='1'` is true for every row, so the query returns **all three users**. A typical login takes the
first row back as "the logged-in user" — and that's `admin`. No password, full admin access.

Two details make this real rather than hand-wavy. First, that trailing `--` isn't decoration: without it,
the leftover `'` and `AND password = '...'` from the template would still be there, and the always-true
`AND password` would fail (`AND` binds tighter than `OR`, so a bare `' OR '1'='1` *doesn't* bypass a
two-condition query). Commenting out the rest is what makes the attack land. Second, an attacker who
wants a *specific* account skips the `OR` entirely and just types `admin' --` into the username:

```sql
SELECT id, username, role FROM users WHERE username = 'admin' --' AND password = 'x'
```

The `--` deletes the password check; they're logged in as `admin` knowing only the username. This single
technique — close the quote, comment out the rest — is the "hello world" of SQL injection.

## Attack 2: stealing other tables with UNION

Back in Module 08 you learned `UNION` stacks one query's rows onto another's, with a warning that this is
"the engine behind an entire family of attacks." Here it is. Say the store has a product search that
builds this:

```python
# VULNERABLE
query = "SELECT name, price FROM product WHERE name LIKE '%" + search + "%'"
```

The attacker types this into the search box:

```
none%' UNION SELECT username, password FROM users --
```

which assembles into:

```sql
SELECT name, price FROM product WHERE name LIKE '%none%' UNION SELECT username, password FROM users --%'
```

The product search matches nothing (`none`), but the injected `UNION SELECT` runs against `users` and
**stacks every credential onto the results** the page expected to show — so the "product list" comes back
as:

```
+----------+----------+
| name     | price    |
+----------+----------+
| admin    | s3cr3t   |
| dwight   | beets    |
| jhalpert | pam4ever |
+----------+----------+
```

The usernames and passwords, rendered into a product grid. The two `UNION` rules from Module 08 are
exactly the attacker's checklist: match the **column count** (two columns out, so they select two) and
match the **types**. Attackers find the column count by probing — adding `UNION SELECT NULL`, then `NULL,
NULL`, until the error stops — which is why leaking raw database errors helps them (more on that below).

## Attack 3: changing data, and attacking blind

Reading data is bad; injection can also *write* it. If the injectable statement is an `UPDATE`, an
attacker can rewrite rows — `SET role = 'admin'` on their own account, say. You'll also hear about the
dramatic **stacked query**: ending the statement and starting a new one, like `'; DROP TABLE users; --`.

> **Dialect note:** stacked queries are less universal than the movies suggest. Many database drivers
> refuse to run more than one statement per call — the browser engine and Python's SQLite driver both
> reject `SELECT ...; DROP ...` outright ("you can only execute one statement at a time"). So `; DROP
> TABLE` often *doesn't* work — but that is cold comfort, because `UNION`-based reads and boolean logic
> injected *inside a single statement* need no second statement at all. Don't rely on your driver's
> stacking rules as a defense; they're an accident, not a control.

And what if the page shows no results at all — just "login failed" or "search returned nothing"?
Attackers switch to **blind injection**, the boolean/time-based probing that Module 09 hinted at. They
inject a condition and watch the app's *behavior*: `... AND (SELECT substr(password,1,1) FROM users WHERE
username='admin') = 'a'` returns a page if the guess is right and a different page if it's wrong, letting
them read a secret one character at a time. The **time-based** cousin injects a deliberate delay
(`... AND (CASE WHEN <guess> THEN sleep(5) ELSE 0 END)`) and reads the answer from how long the page takes
to load. Slow, but fully automated — no visible output required.

## The one real fix: parameterized queries

Every attack above works because user input got mixed into the *code* of the query. The fix removes that
possibility entirely: **send the query and the data to the database separately.** This is called a
**parameterized query** (or **prepared statement**). You write the SQL with placeholders where values
go, and hand the values over as a separate list:

```python
# SAFE — parameterized query
query = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
db.execute(query, [username, password])
```

The `?` marks are placeholders. Here's why this is a *categorical* fix, not a patch: the database
receives the query template — `... WHERE username = ? AND password = ?` — and **compiles its structure
first**, before it has ever seen the user's input. The values are bound in *afterward*, as pure data that
slots into the placeholders. They are never parsed as SQL, so there is nothing an attacker can type that
becomes code. Feed the parameterized version the exact same attack from Attack 1:

```
username = ' OR '1'='1' --
```

and the database looks for a user whose username is *literally the seven-character string* `' OR '1'='1'
--`. No such user exists, so it returns **zero rows** and the login fails — which is exactly right. The
malicious input was treated as a (weird) username, never as logic. Same input, same query, opposite
outcome, because the input never touched the code path.

This is the single most important habit in this course. Every mainstream language has it built in:

- **Python:** `cursor.execute("... WHERE id = ?", (user_id,))`
- **Java:** `PreparedStatement` with `?` placeholders and `setString(1, input)`
- **PHP (PDO):** `$stmt = $pdo->prepare("... WHERE id = :id"); $stmt->execute(["id" => $input]);`
- **C# / .NET:** `SqlCommand` with `cmd.Parameters.AddWithValue("@id", input)`

Different syntax, identical idea: **the query is code, the input is data, and the two never mix.** Note
this is *not* the same as "escaping the quotes" — escaping tries to sanitize dangerous characters after
the fact and is notoriously easy to get wrong (different quoting rules, Unicode tricks, numeric contexts
with no quotes at all). Parameterizing sidesteps the whole problem instead of trying to out-clever the
attacker.

## What parameters can't do, and defense in depth

Parameterization covers *values*. It can't stand in for a **table or column name**, or the direction in
`ORDER BY salary DESC` — those are parts of the query's structure, not values, so there's no placeholder
for them. When you must build one of those from user input (say, "sort by the column they picked"), use
**allowlist validation**: check the input against a fixed set of known-good options and reject anything
else.

```python
# identifiers can't be parameters — allowlist them
allowed = {"salary", "hire_date", "last_name"}
if sort_column not in allowed:
    raise ValueError("bad sort column")
query = f"SELECT * FROM employee ORDER BY {sort_column}"   # safe: value came from the allowlist, not the user
```

Parameterized queries are the primary defense; these layers make the system harder to attack even if
something slips:

- **Allowlist input validation.** Reject input that doesn't fit the expected shape (an email that isn't
  an email, an ID that isn't a number). This shrinks the attack surface — but it is a *supplement*, never
  a substitute. Blocklists ("strip out the word `UNION`") are trivially bypassed (`UNunionION`,
  encodings, casing); allowlists are far better, and parameterizing is better still.
- **Least privilege.** The account your application connects with should have exactly the permissions it
  needs and no more. A read-only web page's database user has no business being able to `UPDATE`,
  `DELETE`, `DROP`, or read the `users` table — so even a successful injection hits a wall. You'll set
  these permissions with `GRANT`/`REVOKE` in Module 12; this is where they pay off.
- **Safe error handling.** Never show raw database errors to users. Messages like `unknown column
  'password' in ...` hand attackers a map of your schema and confirm their probes (recall how Attack 2's
  attacker counted columns by reading errors). Log the detail server-side; show the user a generic
  "something went wrong."

Layer them, but keep the order straight: **parameterize first**, then validate, then restrict privileges,
then fail safely. The extra layers reduce damage; only parameterization removes the vulnerability.

## Try it: spot it, exploit it, fix it

This is a preview of Checkpoint C. An employee directory has a search-by-last-name feature built the
dangerous way:

```python
query = "SELECT first_name, last_name FROM employee WHERE last_name = '" + search + "'"
```

An attacker types this into the box:

```
x' OR '1'='1' --
```

What does the database run, what comes back, and how do you fix it?

<details>
<summary>Work it out, then check</summary>

**What the database runs** — substitute the input into the template:

```sql
SELECT first_name, last_name FROM employee WHERE last_name = 'x' OR '1'='1' --'
```

The `'` closes the `'x` string, `OR '1'='1'` is always true, and `--` comments out the template's leftover
trailing quote. So it reduces to `WHERE last_name = 'x' OR '1'='1'`, which is true for every row. Instead
of one employee, the attacker dumps the **entire table** — all eight people, salaries and all if those
columns were selected. A search box just became "download the whole employee list."

**The fix** — parameterize, so the input is a value and never syntax:

```python
query = "SELECT first_name, last_name FROM employee WHERE last_name = ?"
db.execute(query, [search])
```

Now the same `x' OR '1'='1' --` is searched for as a *literal last name*. Nobody has that last name, so
the query returns **zero rows** — the search politely finds nothing, and the attack is dead. (Note this
module is read-and-reason rather than run-in-the-IDE: the vulnerability lives in *application code*
gluing the string together, and the browser has no application tier, so there's no server-side string to
exploit here — but the reasoning is exactly what a real code review demands of you.)

</details>

## Recap

SQL injection happens when an application builds a query by **concatenating user input into the query
string**, erasing the boundary between code and data so the database parses an attacker's input as SQL.
With it, an attacker can **bypass login** (`' OR '1'='1' --` closes the string, adds an always-true
condition, and comments out the password check), **exfiltrate other tables** by injecting a `UNION SELECT`
into a search, **modify data** through injected `UPDATE`/`DELETE`, and even read secrets **blind** by
watching the app's behavior or response time when no output is shown. The one categorical fix is the
**parameterized query** (prepared statement): the SQL structure is compiled first with `?`/`:name`
placeholders, then the values are bound as pure data that can never become code — so the exact same
malicious input is treated as a harmless literal. Around that primary defense, layer **allowlist
validation** (the only safe way to handle identifiers like sort columns, since they can't be
parameterized), **least privilege** to cap the blast radius, and **safe error handling** so leaked
messages don't map your schema. Validation and escaping are supplements; only parameterization removes
the hole.

## Quiz seeds

- Q: What is the root cause of SQL injection?
  - ✅ User input is concatenated directly into the query string, so the database can't tell the
    developer's SQL from the attacker's input and parses all of it as code
  - ❌ SQL is an inherently insecure language that should be avoided — SQL is fine; the flaw is in how
    application code *builds* queries from strings, not in SQL itself
  - ❌ The database has a bug that lets attackers run commands — it's not a database bug; the database is
    faithfully running the malformed query the application handed it

- Q: A login runs `WHERE username = '<input>' AND password = '<input>'`. Why does the payload `' OR
  '1'='1' --` log the attacker in, but a bare `' OR '1'='1` (no `--`) does not?
  - ✅ The `--` comments out the trailing `AND password = '...'` so only the always-true `OR` remains;
    without it, `AND` (which binds tighter than `OR`) still enforces the password check and the leftover
    quote breaks the syntax
  - ❌ The two are identical; the `--` is just a stylistic choice — the `--` is essential: it removes the
    password condition and the template's leftover quote
  - ❌ `' OR '1'='1` fails because `OR` isn't valid in a `WHERE` clause — `OR` is valid; the difference is
    the uncommented `AND password` check that survives without the `--`

- Q: Why does a **parameterized query** stop injection where "escaping the input" is unreliable?
  - ✅ The query structure is compiled before the input is seen, and the value is then bound as pure data
    that's never parsed as SQL — so no input can become code, rather than trying to sanitize dangerous
    characters after the fact
  - ❌ It automatically deletes any SQL keywords from the input — it doesn't filter the input at all; it
    keeps the input out of the code path entirely, so keywords in it are harmless
  - ❌ It encrypts the user's input before running it — there's no encryption; the mechanism is separating
    the compiled query from the bound values

- Q: You need to let users sort a report by a column they choose. Why can't you parameterize the column
  name, and what should you do instead?
  - ✅ Placeholders only stand in for *values*, not identifiers like column names; validate the chosen
    column against an **allowlist** of known-good names and reject anything else
  - ❌ You can parameterize it exactly like a value with a `?` — placeholders can't represent a column or
    table name, only a value, so this won't work
  - ❌ Just escape the column name and concatenate it — escaping an identifier is error-prone; an
    allowlist of permitted columns is the safe approach

- Q: Which statement about defense in depth is correct?
  - ✅ Parameterized queries are the primary fix; least privilege, allowlist validation, and safe error
    handling reduce damage but don't replace parameterizing
  - ❌ Strong input validation with a blocklist of dangerous words makes parameterized queries unnecessary
    — blocklists are easily bypassed and validation is a supplement, not a substitute for parameterizing
  - ❌ Least privilege alone prevents injection — it caps the blast radius of a successful injection but
    doesn't stop the attack from happening

## Up next

First, put the attack you just previewed into practice: **Checkpoint C — Find and Fix the Injectable
Query** hands you a small vulnerable query pattern like the search box above, and you identify the
injection and rewrite it safely — reinforcing Modules 06–08 plus this one. Then, because least privilege
kept coming up as a way to limit the damage of an attack — and that's a control you set
in SQL itself — **Module 12 — Access Control, Views & Auditing** closes the security track: `GRANT` and
`REVOKE` to give each user exactly the permissions they need and nothing more, **views** as an
access-control boundary that exposes only the safe columns of a table, and audit logging plus
backup/recovery as the integrity controls that let you answer "who changed this, and can we undo it?" It's
the practical, defensive counterpart to the attacks you just learned to run.
