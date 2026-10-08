---
name: audit-db
description: Database access audit of a codebase covering N+1 queries, missing indexes, unique constraints, ON DELETE behavior, denormalization consistency and justification, unbounded reads, transactions and concurrency, integrity constraints, and migration safety, delivered as a PDF/HTML report with ready-to-paste GitHub issues. Use when the user asks for a database, ORM, schema, or query performance audit, or asks about N+1 queries, indexes, cascades, or data consistency.
---

# Audit: database access

Audit the schema and the way the application's services, repositories, and
other data access layers use it, and deliver the report defined by the
`audit-report` skill. The question for every finding is what happens when the
tables grow and when real data arrives: duplicates, deletions, concurrent
requests.

SQL injection and missing tenant filters belong to `audit-webserver`;
retention of personal data belongs to `audit-privacy`.

Copy this checklist and track it:

```
- [ ] 1. Load audit-report
- [ ] 2. Detect the stack and ask for a database
- [ ] 3. Build the table and query inventories
- [ ] 4. Check every category
- [ ] 5. Synthesize and render
```

## 1. Load audit-report

Invoke the `audit-report` skill now and start or resume the log. It defines how
you record findings as you go. The area is `db`; the issue title prefix is
`[DB]`.

## 2. Detect the stack and ask for a database

Identify the database engine, the ORM or query builder (Django ORM,
SQLAlchemy, ActiveRecord, Prisma, TypeORM, Drizzle, Sequelize, JPA/Hibernate,
Ecto, GORM, raw SQL), where the schema is defined (models, migrations, SQL
files), and the layers that query it (services, repositories, resolvers,
serializers, templates). Record the mapping in `methodology`.

The schema in the migrations is the truth. When models and migrations
disagree, report the drift under `integrity` and use the migrations.

Ask the user whether a database with realistic volume is available: a test or
staging copy, or read-only statistics from production. With one, read row
counts and index usage (`pg_class.reltuples`, `pg_stat_user_tables`,
`pg_stat_user_indexes`, or the engine's equivalent) and run `EXPLAIN` for the
query sites on large tables. Run `EXPLAIN ANALYZE` only on a test database,
since it executes the query. Never write to any database. Without one, audit
from the code, say so in `methodology`, and estimate table sizes as step 3
describes.

When the project's tests run locally, count the queries a list endpoint issues
by turning on the ORM's query log through configuration or environment
variables, without editing project files. Query counts that grow with the
number of rows are the strongest evidence for N+1.

## 3. Build the table and query inventories

Record two inventory tables.

**Tables.** One row per table: table, model or migration `file:line`, size
class, indexes, unique constraints, foreign keys with their ON DELETE rule,
and denormalized columns. Size classes:

- `large`: grows with users, events, or time (orders, messages, logs, audit
  trails, line items);
- `medium`: grows with customers or tenants (accounts, projects);
- `small`: bounded (settings, lookups, plans).

Use row counts when step 2 gave you a database; otherwise give the growth
driver as the reason.

**Query sites.** Start from the routes, jobs, and commands, follow them into
the services and repositories, and record one row per query on a `large` or
`medium` table: site `file:line`, entry point (route or job), table, filter,
join, and sort columns, the index that serves them, and whether it runs inside
a loop. Count the entry points to confirm none was skipped. On a large
codebase, cover one module at a time and record each module as done in
`methodology`, rather than sampling.

## 4. Categories

### 1. N+1 queries (`n-plus-one`)

A query per row of a previous result: relations read inside loops, templates,
and serializers (nested DRF serializers, Pydantic models built from ORM
objects, `to_json` methods) without eager loading (`select_related`,
`prefetch_related`, `joinedload`, `selectinload`, `includes`, `include`,
`JOIN FETCH`); GraphQL resolvers without batching (DataLoader); and writes in
loops (insert, update, or delete per row) where a bulk operation exists. Also
the opposite: eager loading of large collections that the caller does not use.

### 2. Indexes (`indexes`)

On `large` and `medium` tables, filters, joins, sorts, and uniqueness checks
on columns without an index whose leading columns match; foreign key columns
without an index (PostgreSQL does not create one); case-insensitive or
function-based lookups (`lower(email)`, `LIKE '%term%'`) that a plain index
cannot serve. Also redundant indexes (one is a prefix of another) and indexes
no query uses, which cost every write.

### 3. Unique constraints (`uniqueness`)

Uniqueness that the code assumes but the database does not enforce
(check-then-insert races, get-or-create without a constraint), and unique
rules that fail on real data. For composite unique constraints in particular,
check:

- the scope: global where it must be per tenant or per parent, or per parent
  where it must be global;
- nullable columns: most engines treat NULLs as distinct, so
  `UNIQUE (tenant_id, external_id)` admits duplicates when `external_id` is
  NULL;
- normalization: case, accents, and whitespace in emails, slugs, and names;
- soft delete: a unique rule that blocks recreating a deleted record, or one
  that ignores `deleted_at` and lets active duplicates in (a partial unique
  index solves both);
- natural keys that repeat in reality (person names, titles, phone numbers
  shared by a family).

### 4. ON DELETE behavior (`on-delete`)

For every foreign key, what deleting the parent does, and whether that is
documented and intended:

- cascades that delete data users still need (deleting a user deletes the
  invoices of their company), and long cascade chains;
- `SET NULL` on a column the model treats as required;
- the ORM's cascade disagreeing with the database's (Django `on_delete` and
  SQLAlchemy `cascade=` run in the application, so bulk deletes, raw SQL, and
  other clients bypass them, and signals do not fire);
- soft-deleted parents whose children remain active;
- relations with no foreign key at all, which leave orphans.

### 5. Denormalization consistency (`denorm-consistency`)

For every denormalized value (counters, totals, copied fields, cached JSON,
materialized views), list every code path that writes the source data and
check that each one updates the copy in the same transaction, or that a
trigger or recompute job keeps it right. Distinguish snapshots, values copied
on purpose to record history (the price on an order line), from caches, which
must follow the source.

### 6. Denormalization justification (`denorm-justification`)

Denormalized values with no hot read path that needs them, no measurement or
comment that explains them, or a cheap indexed join that would replace them.

### 7. Unbounded reads (`unbounded`)

List endpoints and jobs without a limit or pagination on `large` tables;
whole tables or collections loaded into memory; `SELECT *` or full model
loads that carry large columns (blobs, JSON, text) the caller does not use;
counting or existence checks that load rows (`len(queryset)`); deep `OFFSET`
pagination on large tables where keyset pagination fits.

### 8. Transactions and concurrency (`transactions`)

Operations that write several rows or tables without a transaction;
read-modify-write without a row lock or an atomic update (`balance = balance
+ x` computed in the application loses updates); external calls (HTTP, email,
queues) inside a transaction, or events published before the commit;
transactions held open across user interaction or long loops; isolation
level assumptions the engine does not provide.

### 9. Integrity constraints (`integrity`)

Rules the code relies on that the schema does not enforce: missing foreign
keys, columns nullable where the code requires a value, statuses and enums
stored as free text without a CHECK or enum type, amounts without a CHECK on
sign, money in floating point, timestamps without time zone, and drift
between models and migrations.

### 10. Migration safety (`migrations`)

Migrations that lock or rewrite `large` tables: index creation without
`CONCURRENTLY` (or the engine's online equivalent), a NOT NULL column added
without a default or backfill, type changes that rewrite the table, and data
migrations in the same transaction as schema changes. Also migrations that
cannot be reversed without saying so, and schema changes made outside the
migration tool.

## Severity

| Level | Meaning |
|---|---|
| `critical` | Normal use loses or corrupts data: a cascade deletes data users still need, a missing unique constraint admits duplicate payments or records with legal effect, concurrent requests lose updates to balances or stock. |
| `high` | A primary path whose cost grows with a `large` table (N+1, unindexed filter or sort, unbounded read), a denormalized value that drifts and is shown to users or used in decisions, or a migration that locks a `large` table. |
| `medium` | The same on a secondary path or a `medium` table, or an integrity rule enforced only in application code that holds today. |
| `low` | Hygiene with no current effect: redundant or unused indexes, a consistent denormalization without justification, an intended ON DELETE rule that is not documented. |
| `info` | An observation with no risk on its own. |

## 5. Synthesize and render

Record all ten categories, findings, and strengths as `audit-report` defines,
write the synthesis, and render. For each finding, put the schema and the query
site in `location`, the table's size class and row count when known in
`conditions`, and query counts or `EXPLAIN` output in `description` when you
measured them. Mark findings made from code alone, without measurement, with
"from code" in `conditions`.
