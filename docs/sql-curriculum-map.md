# SQL Language Curriculum Map — Security-Focused, CNIT 27200-Aligned

**Status:** Draft for review — planning only, no content authored yet.
**Supersedes:** the generic 10-module SQL outline in `docs/sql-integration-plan.md` and
`docs/language-expansion-plan.md` (§4). Those docs still own the *engineering* plan (sql.js,
results-grid, test-harness contract); this doc replaces only their *curriculum outline*
section with a security-framed, exam-aligned one. See "Reconciling with the other SQL docs"
at the bottom.

**Goal (as given):** teach SQL from a cybersecurity angle, such that a learner who finishes
the course can sit Purdue's **CNIT 27200 (Database Fundamentals)** test-out exam and pass.

---

## Sources consulted

- `Language Information/4_SQL/SQL Tutorial Full Course.txt` — the source transcript (Giraffe
  Academy, ~7,070 lines / ~260 minutes, MySQL dialect). Scanned in full for topic coverage.
- [CNIT 27200 — Purdue course catalog](https://catalog.purdue.edu/preview_course_nopop.php?catoid=8&coid=77655) — official
  description.
- [CNIT Advanced Credit Exams — Purdue Testing Services](https://www.purdue.edu/studentsuccess/testing-services/tests/advanced/CNIT.php) —
  test-out logistics (this is the authoritative page for *how* the exam works).
- [CNIT Test-Out info PDF](https://polytechnic.purdue.edu/sites/default/files/files/CNIT_Test_Out_April_2024.pdf) and
  [Form 231 + Advanced Credit Checklist](https://www.purdue.edu/studentsuccess/testing-services/documents/Form%20231%20and%20Checklist_updated%20June%202025.pdf) —
  eligibility/registration mechanics.
- [CNIT 27200 sitemap — Course Hero](https://www.coursehero.com/sitemap/schools/108-Purdue-University/courses/3275245-CNIT27200/) —
  real student-uploaded lecture slides and exam-review docs (week 8 outer joins, week 12 DML,
  exam-1 review on identifying/non-identifying FK relationships, ER-diagram labs in Oracle
  Data Modeler). Used only to corroborate topic scope, not as exam content.

## What CNIT 27200 actually is

**Database Fundamentals**, 3 credits, lecture + lab. Catalog description: *"A study of
relational database concepts. These concepts include data design, modeling, and
normalization; the use of Structured Query Language (SQL) to define, manipulate, and test the
database; programmatic access to a database and practical issues that database developers
must handle."* It's the *first* database course — the follow-on **CNIT 372 (Database
Programming)** is where PL/SQL, stored procedures, and triggers live. That boundary matters:
test-out content should stop where 372 begins.

Confirmed topic scope (catalog + lecture-slide titles):

- **Data modeling**: entities, attributes, relationships, ER diagrams (built in Oracle Data
  Modeler in the actual course), cardinality (1:1, 1:N, N:M), **identifying vs. non-identifying
  relationships**, associative entities for many-to-many. This is explicitly exam-1 material
  (a student "exam 1 review" doc found in the search is built entirely around identifying vs.
  non-identifying foreign keys).
- **Normalization**: 1NF → 2NF → 3NF.
- **SQL DDL**: `CREATE`/`ALTER` tables, primary/foreign keys, constraints.
- **SQL DML**: `INSERT`/`UPDATE`/`DELETE`, plus `COMMIT`/`ROLLBACK` (a lecture slide is
  literally titled "week12_SQL DML.pdf — Insert, Update, Delete, Commit, Rollback").
- **SQL queries**: multi-table joins — **equijoins, natural joins, nonequijoins, self-joins**,
  inner joins, and outer joins (a "week8_SQL outerjoins.pdf" slide reviews inner joins before
  teaching outer joins).
- **Environment**: the real course runs on an **ECN-hosted Oracle database** via **Oracle SQL
  Developer**, not MySQL.

**Test-out mechanics** (this shapes how the course should train, not just what it covers):

- 2 hours, **handwritten and hand-graded** — no computer, no SQL editor, no autocomplete. The
  exam tests whether a learner can *write correct SQL and ERDs by hand*, not whether they can
  debug against a live database.
- 70% to pass, **one attempt only**, no study guide provided by Purdue — "students are expected
  to be well-versed in the course material" going in.
- Prerequisite: credit in CNIT 15501 (or equivalent intro course) **and** CNIT 18000/18200.
  The platform can't grant those, so the SQL course should assume the learner already knows
  general programming (true of anyone who did the Python course here) but should say so
  explicitly on the landing page.

## What the transcript covers well vs. what's missing

The transcript is a strong source for the *mechanical SQL* half of the course, but it's a
generic beginner tutorial — it was never written against 27200's syllabus, and it has zero
security content. Coverage check (full-text scan):

| Topic | In transcript? | Where |
|---|---|---|
| Databases/RDBMS intro, installing MySQL | Yes | opening ~200 lines |
| Primary keys, foreign keys | Yes | lines ~685, ~823 |
| Constraints (`NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`) | Yes | line ~2850 |
| `AUTO_INCREMENT` | Yes (MySQL-specific) | line ~2902 |
| `SELECT`/`WHERE`/`ORDER BY`/filtering | Yes | early-mid course |
| Aggregate functions, `GROUP BY` | Yes | line ~4468 |
| `UNION` | Yes | line ~4779 |
| Joins (inner/outer/self) | Yes | line ~4986 |
| Nested queries ("subqueries," different term used) | Yes | lines ~5254–5494 |
| Triggers | Yes (brief) | line ~5702 — **out of scope for 27200**, belongs to CNIT 372 |
| ER diagrams, entities, attributes, cardinality (1:1/1:N/N:M) | Yes | lines ~6039–7068 (final 14% of the course) |
| **Normalization (1NF/2NF/3NF) vocabulary** | **No** | not found anywhere |
| **Identifying vs. non-identifying relationships** | **No** | not found — but this is explicitly exam-1 material per Course Hero |
| **Transactions (`COMMIT`/`ROLLBACK`)** | **No** | not found — but explicitly a week-12 lecture topic |
| **`GRANT`/`REVOKE`, roles, privileges** | **No** | not found — needed for the security framing |
| **SQL injection, parameterized queries** | **No** | not found (one throwaway line says "security is essential," nothing technical) |
| Oracle-specific syntax (`VARCHAR2`, `SEQUENCE`, `TO_DATE`, `ROWNUM`/`FETCH FIRST`) | No (MySQL dialect throughout) | — |

So four modules' worth of content — normalization, the identifying/non-identifying FK
distinction, transactions, and the entire security track — **has no source material in the
transcript and must be authored fresh**, the same gap the Python build hit with graded
exercises and the C build hit with the master curriculum doc. This is expected, not a
blocker, but it changes the authoring plan (see Next steps).

---

## Course design decisions

1. **Two braided goals, one course.** Every module either (a) covers something the CNIT 27200
   test-out exam requires, or (b) covers something a security-minded database developer needs
   that 27200 doesn't test. Modules are labeled with which. Nothing is added that contradicts
   27200 prep — the security modules extend past its boundary, they don't replace its content.
2. **Teach portable/standard SQL, callout Oracle where it matters.** The platform's engine is
   `sql.js` (SQLite), but the real exam is handwritten against Oracle conventions. Since it's
   hand-graded rather than compiled, exact dialect is secondary to correct relational logic —
   but a few Oracle-specific idioms are common enough on exams that they need explicit
   callouts even though they won't *run* in the browser IDE: `SEQUENCE` (vs. SQLite
   `AUTOINCREMENT`/MySQL `AUTO_INCREMENT`) for surrogate keys, `VARCHAR2`/`NUMBER` types,
   `TO_DATE`, and `ROWNUM`/`FETCH FIRST n ROWS ONLY` (vs. `LIMIT`). Treat these as `<Callout
   type="note">` asides in the relevant modules, not separate lessons.
3. **"Programmatic access to a database"** (from the catalog description) can't become a real
   client-server exercise on a static, backend-less site. Fold it in conceptually inside the
   injection module: how application code builds a query string is *exactly* the mechanism
   that makes injection possible, so it's a natural, honest place to cover the idea without
   needing a live app tier.
4. **Design labs, not just query labs — RESOLVED (2026-07-02).** The real course's labs are
   ER-diagramming exercises (parent/child entities, resolving many-to-many). The platform's
   query format (`schema.sql` + `tests.json`) grades *queries* well but can't grade a *diagram*.
   Decision — a **two-track format**, both deterministic and fully in-browser (full spec:
   `docs/sql-integration-plan.md` → "Modeling & normalization exercises"):
   - **Track 1 (default): grade as DDL** whenever the answer has a canonical schema — the
     normalized 3NF tables, the associative table for an N:M, the FK that makes a relationship
     identifying. These stay ordinary query-contract exercises, graded via structural probes
     (`sqlite_master`, `PRAGMA table_info`, `PRAGMA foreign_key_list`). "Write the `CREATE
     TABLE` that fixes this 2NF violation" and Checkpoint A's normalized schema live here.
   - **Track 2: a new `structured` exercise kind** for answers with no SQL artifact (FD lists,
     "which normal form + why," partial/transitive-dependency ID, cardinality, identifying vs.
     non-identifying, ERD structure, attribute→table decomposition). A `question.json`/
     `answer.json` bundle with constrained fields (`single-select`, `multi-select`, `token-set`,
     `matching`, `partition`, `erd-spec`) graded by exact canonical-form comparison — no NLP, no
     backend. It adds a `"modeling"` lesson type + a `<StructuredExercise>` renderer (additive,
     mirroring the results-grid seam) and keeps the grade_check ⟺ browser lock-step.
   Each Track-2 exercise keeps an ungraded "draft it first" area (handwritten-exam practice).
5. **Handwritten-exam skill, not just browser-IDE skill.** Because the real exam bans
   computers, a couple of modules should include a "write it before you run it" exercise
   pattern (predict/draft the query in a plain text area, then reveal and run) so learners
   practice producing correct SQL without autocomplete — not a structural change to the IDE,
   just an authoring pattern to reuse from the Python/C curriculum docs' predict-then-reveal
   convention.

---

## Module list (12 modules + capstone)

Each module = a trimmed lecture + `quiz.json` + graded exercises, following the platform's
existing content contract. `[27200]` tags core test-out content; `[SEC]` tags the security
throughline; checkpoints land right after the module that completes their prerequisites (same
convention as the C course).

### 01 — Databases, RDBMS & Why Attackers Care `[27200]` `[SEC]`
What a database is, what an RDBMS is (from the transcript's opening). Then the framing hook
for the whole course: databases are the highest-value target in most breaches (they hold the
data attackers actually want), introduce the CIA triad (confidentiality/integrity/
availability) applied to data, and preview where the course will return to security. Sets up
both the test-out goal and the security lens explicitly on day one.

### 02 — The Relational Model & Keys `[27200]`
Tables, rows, columns, primary keys, foreign keys, why relationships exist instead of one flat
table. Transcript-sourced (PK/FK sections).

### 03 — Entity-Relationship Modeling `[27200]`
Entities, attributes, relationships, cardinality (1:1, 1:N, N:M), associative entities for
many-to-many, and the **identifying vs. non-identifying relationship** distinction (fresh
content — not in the transcript, but explicitly exam-1 material). Practice building ERDs from
a short business scenario, mirroring the real course's lab style.

### 04 — Normalization `[27200]`
Fresh content (no transcript source). Functional dependencies, update/insert/delete anomalies,
1NF → 2NF → 3NF, and when denormalization is a legitimate tradeoff rather than a mistake.

**★ Checkpoint A — Design & Normalize.** Given a messy, redundant spreadsheet-style dataset,
produce an ERD and a normalized (3NF) schema. Reinforces Modules 02–04.

### 05 — Defining the Schema (DDL) `[27200]`
`CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, data types, constraints (`PRIMARY KEY`,
`FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`). Oracle-dialect callouts for
`VARCHAR2`/`NUMBER`/`SEQUENCE` vs. the browser engine's SQLite types.

### 06 — SELECT, Filtering & Sorting `[27200]`
`SELECT`/column aliases/`DISTINCT`, `WHERE`, comparison and logical operators, `LIKE`, `IN`,
`BETWEEN`, `IS NULL`, `ORDER BY`, `LIMIT` (with the `ROWNUM`/`FETCH FIRST` Oracle callout).
Strong transcript coverage.

### 07 — Functions & Aggregates `[27200]`
String/numeric/date functions, `GROUP BY`, `HAVING`, aggregate functions
(`COUNT`/`SUM`/`AVG`/`MIN`/`MAX`). Transcript-sourced.

### 08 — Joins `[27200]`
Equijoins, natural joins, nonequijoins, self-joins, inner joins, left/right/full outer joins,
`UNION`. This is the single most heavily emphasized topic in the real course's materials
(a dedicated lecture on outer joins alone) — give it the most exercise depth.

**★ Checkpoint B — Multi-Table Report.** A seeded multi-table schema (e.g., a small store or
library DB); write a series of join-based queries to answer realistic business questions.
Reinforces Modules 05–08.

### 09 — Subqueries `[27200]`
Nested/scalar subqueries, `IN`/`NOT IN` subqueries, correlated subqueries, `EXISTS`.
Transcript-sourced ("nested query").

### 10 — Data Manipulation & Transactions `[27200]`
`INSERT`/`UPDATE`/`DELETE`, then `COMMIT`/`ROLLBACK` and why transactions exist (atomicity,
the "did my delete actually happen" problem). The commit/rollback half is fresh content — not
in the transcript, but an explicit week-12 lecture topic in the real course.

### 11 — SQL Injection & Secure Query Practices `[SEC]`
The security core of the course. How string-concatenated queries let attacker input change a
query's meaning (walked through concretely, not abstractly); parameterized queries / prepared
statements as the fix; input validation as defense-in-depth, not a substitute. This is also
where "programmatic access to a database" (the catalog's phrase) gets covered conceptually —
how application code assembles a query is exactly the mechanism that makes injection possible.

**★ Checkpoint C — Find and Fix the Injectable Query.** Given a small vulnerable query
pattern, learners identify the injection and rewrite it safely. Reinforces Modules 06–08 + 11.

### 12 — Access Control, Views & Auditing `[SEC]`
`GRANT`/`REVOKE`, roles, the principle of least privilege, views as an access-control boundary
(not just a convenience), and the basics of audit logging and backup/recovery as integrity
controls. Closes the loop on the catalog's "practical issues that database developers must
handle" line from a security angle.

### Capstone — Design, Build & Secure a Small Database
End-to-end: a short business scenario → ERD → normalize → `CREATE TABLE` with constraints →
seed data → a set of join/aggregate queries answering real questions → a deliberate review
pass for injection risk and access-control decisions. Mirrors the real course's own "design a
database for X" lab pattern and doubles as a portfolio piece.

---

## Cheat sheet outline (mirrors the C/Python cheat sheets)

1. **Relational model** — tables/rows/columns, PK/FK, ER-diagram symbol reference.
2. **Normal forms** — 1NF/2NF/3NF checklist.
3. **DDL** — `CREATE`/`ALTER`/`DROP`, constraint syntax, Oracle-vs-standard type table.
4. **DQL** — `SELECT`/`WHERE`/`ORDER BY`/`LIMIT` quick reference, operators.
5. **Aggregates** — function list, `GROUP BY`/`HAVING` pattern.
6. **Joins** — a one-page visual (inner/left/right/full/self) — the highest-value page given
   how central joins are to the real exam.
7. **Subqueries** — scalar vs. `IN` vs. correlated vs. `EXISTS`, when to use which.
8. **DML & transactions** — `INSERT`/`UPDATE`/`DELETE`, `COMMIT`/`ROLLBACK`.
9. **Security** — injection pattern to avoid, parameterized-query pattern to use,
   `GRANT`/`REVOKE` syntax, least-privilege checklist.

---

## Reconciling with the other SQL docs

- `docs/language-expansion-plan.md` §4 and `docs/sql-integration-plan.md` each contain a
  **generic 10-module SQL outline** written before the CNIT 27200 / security requirement was
  known. That outline is superseded by the module list above for curriculum purposes. Their
  **engineering content is unaffected and still the plan of record**: the `sql.js` engine
  choice, the results-grid `outputMode` addition to `<Ide>`, the `RunResult.resultSets`
  interface change, and the `schema.sql`/`tests.json` exercise-bundle contract all still apply
  — this course's exercises will be authored into exactly that shape.
- Update needed (not done in this pass): add a pointer from `sql-integration-plan.md`'s
  "Curriculum outline" section to this doc, the same way `c-integration-plan.md` points at
  `c-curriculum-map.md`.

---

## Next steps

1. **Review this module list before any content gets authored.** In particular sanity-check
   Module 03's identifying/non-identifying framing and Module 04's normalization depth — those
   came from a Course Hero exam-review doc and general DB-fundamentals convention, not an
   official syllabus (Purdue provides none). If you or anyone you know has taken CNIT 27200 or
   has old course notes/slides, a quick cross-check against this list would de-risk it further.
2. ~~**Decide the exercise format for Modules 03–04** (ERD/normalization).~~ **DONE
   (2026-07-02)** — resolved as the two-track format in design decision #4 above (full contract
   in `docs/sql-integration-plan.md`). Modules 03–04 can now be authored against it; remaining
   work is engineering the `"modeling"` lesson type + `<StructuredExercise>` renderer in S3 and
   the Track-2 grade_check in S2, both already folded into the phases.
3. **Author the four gap modules' content from scratch**: 03's identifying/non-identifying
   relationships, 04 (normalization), 10's transaction half, and both of 11–12 (the security
   track). These have no transcript source, unlike the other eight modules which can lean on
   `SQL Tutorial Full Course.txt` directly. Consider whether a short reference pass (e.g., a
   standard DB-fundamentals text for normalization rigor, OWASP's SQL-injection material for
   Module 11) is warranted before drafting — recommend doing this per-module rather than
   upfront.
4. **This content plan is independent of, and can proceed in parallel with, the runtime
   engineering track** in `docs/sql-integration-plan.md` (S0 spike → S1 results-grid → S2 test
   harness). Content authoring doesn't block on the runtime, but exercise authors should target
   the `schema.sql`/`starter.sql`/`solution.sql`/`tests.json` contract that doc defines so the
   two tracks meet cleanly at S3.
5. Once this list is approved, the natural authoring pipeline mirrors the C build: a
   `sql-curriculum-builder` skill (analogous to `c-curriculum-builder`) expands a master
   curriculum doc into one "SQL Curriculum Module NN.md" per module in the course voice, then
   an SQL-adapted `curriculum-converter` turns each into the platform lesson bundle.
6. Add the cross-reference from `sql-integration-plan.md` noted above.
