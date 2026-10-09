# File formats

Reference for maintainers. Agents never read or write these files directly:
they go through `audit-findings`, which the `SKILL.md` describes. Formats are
those of `audit-findings` 0.3.0.

An audit lives in `docs/audits/<area>/`:

| File | Role |
|---|---|
| `findings.jsonl` | The append-only log. The only source of truth while the audit runs. |
| `findings.jsonl.lock` | Lock file held during every read and write. Empty. |
| `.gitignore` | Written by `init`; ignores the lock file. |
| `findings.json` | Built from the log by `build` and `render`. Input of the renderer. |
| `report.pdf`, `report.html`, `issues.md` | Written by `render`. |
| `screenshots/` | Optional images referenced by findings. |

## findings.jsonl

One JSON object per line, appended under the lock and never rewritten.
Replaying the lines in order gives the current records.

### Events

| Field | Present | Meaning |
|---|---|---|
| `op` | always | `add`, `update`, `remove`, or `accept`. |
| `id` | always | Record id. |
| `type` | `add` | Record kind (see below). |
| `data` | `add`, `update` | `add`: the whole record. `update`: the fields to change. |
| `reason` | `remove` | Why the record was removed, such as `duplicate of F1`. |
| `agent` | when `--agent` was passed | Free label of the agent that made the change. |
| `ts` | always | UTC time of the change, ISO 8601, seconds. |

Replay rules:

- `add` creates the record. Its `agent` is the record's creator.
- `update` merges `data` into the record; a `null` value deletes the field. It
  clears the accepted mark.
- `accept` marks the record as reviewed until its next `update`.
- `remove` moves the record to the removed set with its `reason`. A removed
  record keeps its data and history, can be shown, and can no longer be
  changed.
- Ids are never reused: the next generated id is one more than the highest
  ever used for the prefix, removed ones included.
- An unknown `op`, an unknown id, or a line that is not JSON makes the log
  unreadable; the error names the line.

### Record kinds

Generated ids are a prefix plus a number. Kinds without a prefix carry their
own `id` in `data`, chosen by the agent.

| Kind | Id | Fields (required in bold) |
|---|---|---|
| `meta` | `meta` (one record) | `lang`, `title`, `project`, `date`, `scope`, `methodology` |
| `category` | own `id` | **`id`**, **`title`**, `applies`, `note`, `status` |
| `finding` | `F1`, `F2`, ... | **`category`**, **`severity`**, **`title`**, **`location`**, **`description`**, **`impact`**, **`fix`**, `snippet`, `language`, `conditions`, `screenshot` |
| `strength` | `S1`, ... | **`text`**, `category`, `evidence` |
| `risk` | `R1`, ... | **`text`** |
| `recommendation` | `REC1`, ... | **`priority`**, **`text`**, `findings` |
| `issue` | `I1`, ... | **`title`**, **`findings`**, **`summary`**, **`acceptance`**, `labels` |
| `inventory` | own `id` | **`id`**, **`columns`**, `title` |
| `row` | `ROW1`, ... | **`table`** (an inventory id), **`cells`** |

Checks made when a record is added or updated:

- No unknown fields; required fields are not empty.
- `lang` is `en` or `pt`; `severity` is `critical`, `high`, `medium`, `low`,
  or `info`; `status` is `todo`, `doing`, or `done`.
- `category`, the ids in `findings`, and `table` refer to live records.
- A row has as many `cells` as its inventory has `columns`.
- `screenshot` exists relative to the audit directory.
- Every `path:line` in a finding's `location` and a strength's `evidence`
  exists, and every line of `snippet` appears in the cited lines.

`init` fills `lang` with `en` and `date` with the local date when they are
missing. `status` on a category is progress tracking, written by `start`,
`done`, and `reopen`; it does not reach `findings.json`.

### Example

The log below has two agents recording at the same time, a duplicate merged
into the finding it repeats, a review, and the synthesis:

```json
{"op": "add", "id": "meta", "type": "meta", "data": {"lang": "en", "date": "2026-10-08", "title": "Security Audit Report", "project": "acme-api", "scope": "FastAPI backend in `src/`."}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "idor", "type": "category", "data": {"id": "idor", "title": "IDOR"}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "xss", "type": "category", "data": {"id": "xss", "title": "XSS", "applies": false, "note": "No HTML rendering of user input."}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "update", "id": "meta", "data": {"methodology": "Read every router in `src/api/`."}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "update", "id": "idor", "data": {"status": "doing"}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "F1", "type": "finding", "data": {"category": "idor", "severity": "critical", "title": "GET /invoices/{id} does not check the tenant", "location": "src/api/invoices.py:1-2", "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()", "language": "python", "description": "No tenant filter.", "impact": "Any user reads any invoice.", "fix": "Filter by the caller tenant.", "conditions": "Any authenticated user."}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "F2", "type": "finding", "data": {"category": "idor", "severity": "critical", "title": "GET /invoices/{id} does not check the tenant", "location": "src/api/invoices.py:1-2", "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()", "language": "python", "description": "No tenant filter.", "impact": "Any user reads any invoice.", "fix": "Filter by the caller tenant.", "conditions": "Any authenticated user."}, "agent": "a2", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "S1", "type": "strength", "data": {"category": "idor", "text": "The users router checks ownership.", "evidence": "src/api/users.py:1-2"}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "routes", "type": "inventory", "data": {"id": "routes", "title": "Route inventory", "columns": ["Method", "Path"]}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "ROW1", "type": "row", "data": {"table": "routes", "cells": ["GET", "/invoices/{id}"]}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "ROW2", "type": "row", "data": {"table": "routes", "cells": ["GET", "/users/{id}"]}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "update", "id": "idor", "data": {"status": "done"}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "remove", "id": "F2", "reason": "duplicate of F1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "accept", "id": "F1", "ts": "2026-10-09T01:53:10+00:00"}
{"op": "accept", "id": "S1", "ts": "2026-10-09T01:53:10+00:00"}
{"op": "add", "id": "R1", "type": "risk", "data": {"text": "Tenant isolation depends on a manual filter in every query."}, "ts": "2026-10-09T01:53:10+00:00"}
{"op": "add", "id": "REC1", "type": "recommendation", "data": {"priority": "P1", "text": "Add a tenant filter to every invoice query.", "findings": ["F1"]}, "ts": "2026-10-09T01:53:10+00:00"}
{"op": "add", "id": "I1", "type": "issue", "data": {"title": "[Security] IDOR in GET /invoices/{id}", "labels": ["security", "critical"], "findings": ["F1"], "summary": "Invoices are fetched without a tenant check.", "acceptance": ["A request for another tenant invoice returns 404"]}, "ts": "2026-10-09T01:53:10+00:00"}
```

## findings.json

`build` turns the live records into this file; the renderer reads only this
file. Agents, timestamps, review marks, category progress, removed records,
and inventory ids do not reach it. Without a log, a hand-written
`findings.json` renders directly with `render <path>`, and `import <path>`
turns it into a log.

| Field | Type | Required | Built from |
|---|---|---|---|
| `lang` | `"en"` or `"pt"` | no, default `en` | `meta` |
| `title`, `project`, `date`, `scope`, `methodology` | string | yes | `meta` |
| `categories` | list of `{id, title, applies?, note?}` | yes | `category` records, in order of creation |
| `findings` | list of finding objects with `id` | yes | `finding` records, in id order |
| `strengths` | list of `{text, category?, evidence?}` | yes | `strength` records |
| `risks` | list of strings | no | the `text` of `risk` records |
| `recommendations` | list of `{priority, text, findings?}` | yes | `recommendation` records |
| `issues` | list of `{title, findings, summary, acceptance, labels?}` | yes | `issue` records |
| `inventory` | a table or a list of `{title, columns, rows}` | no | each `inventory` with its `row` records; identical rows are merged |

Text fields render `` `code` `` spans; blank lines in `methodology`,
`description`, `impact`, `fix`, and `conditions` separate paragraphs.
`recommendations` are sorted by `priority` and findings by severity within
each category when rendered. An issue's `labels` default to the severities of
its findings.

The example log above builds into:

```json
{
  "lang": "en",
  "date": "2026-10-08",
  "title": "Security Audit Report",
  "project": "acme-api",
  "scope": "FastAPI backend in `src/`.",
  "methodology": "Read every router in `src/api/`.",
  "categories": [
    {"id": "idor", "title": "IDOR"},
    {"id": "xss", "title": "XSS", "applies": false, "note": "No HTML rendering of user input."}
  ],
  "findings": [
    {
      "id": "F1",
      "category": "idor",
      "severity": "critical",
      "title": "GET /invoices/{id} does not check the tenant",
      "location": "src/api/invoices.py:1-2",
      "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
      "language": "python",
      "description": "No tenant filter.",
      "impact": "Any user reads any invoice.",
      "fix": "Filter by the caller tenant.",
      "conditions": "Any authenticated user."
    }
  ],
  "strengths": [
    {"category": "idor", "text": "The users router checks ownership.", "evidence": "src/api/users.py:1-2"}
  ],
  "risks": ["Tenant isolation depends on a manual filter in every query."],
  "recommendations": [
    {"priority": "P1", "text": "Add a tenant filter to every invoice query.", "findings": ["F1"]}
  ],
  "issues": [
    {
      "title": "[Security] IDOR in GET /invoices/{id}",
      "labels": ["security", "critical"],
      "findings": ["F1"],
      "summary": "Invoices are fetched without a tenant check.",
      "acceptance": ["A request for another tenant invoice returns 404"]
    }
  ],
  "inventory": [
    {
      "title": "Route inventory",
      "columns": ["Method", "Path"],
      "rows": [["GET", "/invoices/{id}"], ["GET", "/users/{id}"]]
    }
  ]
}
```
