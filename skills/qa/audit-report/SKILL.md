---
name: audit-report
description: Defines how the audit-* skills record findings with the audit-findings command line, which several agents can share in parallel and across sessions, and renders them into a PDF report, an HTML report, and ready-to-paste GitHub issues. Use when an audit skill reaches its first step, or when the user wants an audit report regenerated from a findings.json.
---

# Audit report

Every `audit-*` skill records its results with the `audit-findings` command
line and renders them with it. The audit skill decides what to look for; this
skill decides how findings are recorded and delivered.

Run every command as `uvx audit-findings@0.3.1 <command>`, from the project
root. Below, that prefix is shortened to `audit-findings`. Without `uv`, create
a virtual environment outside the project (`python3 -m venv /tmp/audit-venv`),
install `audit-findings==0.3.1` in it, and run its `audit-findings`. Install
nothing globally.

## Output directory

Everything goes to `docs/audits/<area>/`, where `<area>` is the audit skill's
name without the `audit-` prefix (`webserver`, `db`, `dependencies`, `privacy`,
`ux`, `ui`). Pass `-a <area>` to every command.

| File | Written by |
|---|---|
| `findings.jsonl` | `audit-findings`, as you record; never edit it by hand |
| `screenshots/*.png` | you, when a finding needs one (optional) |
| `findings.json`, `report.pdf`, `report.html`, `issues.md` | `audit-findings render` |

## Starting or resuming

If `docs/audits/<area>/findings.jsonl` exists, the audit is under way: run
`audit-findings -a <area> status` and continue from what it lists. Do not read
the log itself.

Otherwise create it, then record every category of the audit skill:

```bash
audit-findings -a webserver init <<'EOF'
{"lang": "en", "title": "Security Audit Report", "project": "acme-api",
 "scope": "FastAPI backend in `src/`, React frontend in `web/`."}
EOF

audit-findings -a webserver add category <<'EOF'
[{"id": "idor", "title": "IDOR"},
 {"id": "xss", "title": "XSS", "applies": false, "note": "no HTML rendering of user input"}]
EOF
```

Use the category ids and titles the audit skill gives, and record every
category, even the ones that do not apply: mark those with `"applies": false`
and the reason in `note`. A category whose coverage is partial says so in
`note`.

Write all text in one language and set `lang` to `en` or `pt`. `date` defaults
to today. Set `methodology` once you know it: paragraphs separated by blank
lines with the detected stack and how each category maps onto it.

```bash
audit-findings -a webserver update meta <<'EOF'
{"methodology": "..."}
EOF
```

Run `start <category>` when you begin a category and `done <category>` when
you finish it; `status` then shows what is left.

## Recording findings

Pass records as JSON on stdin, one object or an array. `add` prints the id of
each record and refuses the whole batch if one record is wrong: a missing
field, an unknown category, or a location or snippet that is not in the
source. Fix what it reports and run it again.

```bash
audit-findings -a webserver add finding <<'EOF'
{"category": "idor", "severity": "critical",
 "title": "GET /invoices/{id} does not check the tenant",
 "location": "src/api/invoices.py:42-47",
 "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
 "language": "python",
 "description": "What is wrong.",
 "impact": "What an attacker or user can do, or what goes wrong.",
 "fix": "The suggested fix.",
 "conditions": "Any authenticated user."}
EOF
```

- Record only what you verified: code you read, a command you ran, a screen you
  saw. Never speculate, and never invent locations, CVEs, or quotes.
- One finding per distinct defect. The same mistake repeated in several places
  is one finding whose `location` lists every place. When `add` warns that a
  finding overlaps another, read both with `show`; if they are the same
  defect, run `merge <new id> <old id>`. When it warns that a finding overlaps
  one removed earlier, read the reason and remove the new one if it applies.
- Give the exact location: `path:line` or `path:start-end` for code; route or
  screen plus the steps to reach it for interface findings.
- Quote the offending code in `snippet`, trimmed to the lines that show the
  problem. Mask secret values and personal data: keep the first four
  characters of a secret of 12 or more characters and replace the rest with
  `****`; replace shorter secrets entirely with `****`.
- Assign severity with the severity table of the audit skill you are running:
  `critical`, `high`, `medium`, `low`, or `info`.
- Record exploitability or reproduction conditions in `conditions`: feature
  flags, required configuration, roles, devices.
- `snippet`, `language`, `conditions`, and `screenshot` (a path relative to the
  output directory) are optional.

Record what is **correct** as strengths, with evidence. Strengths prove
coverage: "every handler in `routers/orders.py` checks ownership" shows the
router was read.

```bash
audit-findings -a webserver add strength <<'EOF'
{"category": "idor", "text": "Every handler in the users router checks ownership.",
 "evidence": "src/api/users.py:10-80"}
EOF
```

When the audit skill asks for a coverage table, declare it once and add rows
as you go. Identical rows are merged when the report is built.

```bash
audit-findings -a webserver add inventory <<'EOF'
{"id": "routes", "title": "Route inventory", "columns": ["Method", "Path"]}
EOF
audit-findings -a webserver add row <<'EOF'
[{"table": "routes", "cells": ["GET", "/invoices/{id}"]}]
EOF
```

To change a record, pass the fields to change to `update <id>`; `null`
deletes an optional field. `remove <id> --reason "..."` deletes a record that
nothing refers to; the reason stays in the log, and `list --removed` shows it.
`list [kind] [--category C] [--severity S]` and `show <id>...` read records
back.

## Splitting the audit across agents

For a large codebase, record the meta and the categories yourself, then give
each subagent a set of category ids. Tell each subagent to:

- invoke this skill and follow "Recording findings";
- pass `--agent <its name>` to every command, with the name you gave it, and
  run `start` and `done` for its categories;
- record findings, strengths, and inventory rows, but no risks,
  recommendations, or issues;
- reply with the ids it recorded and the categories it finished, not the
  findings themselves.

When the audit skill splits the work by part instead (one subagent per module
or document, each looking for several categories), give each subagent its
part and the categories to look for. It skips `start` and `done`; you run
`done` for each category once every part is reviewed.

The log takes a lock on every write, so subagents can record at the same time.
The agent name is a free label: the log stores it with every change, `show`
prints who changed a record and when, and `list --agent <name>` filters by the
agent that created it. It never reaches the report. Do not pass `--agent`
yourself.

### Reviewing subagent findings

`status` lists under "to review" every finding and strength a subagent
recorded that you have not accepted yet. Review each one before the synthesis:

1. Read it with `show <id>` and reread the cited code.
2. Keep it with `accept <id>`, after fixing it with `update <id>` if needed.
   A later `update` by anyone sends it back to review.
3. Fold a duplicate into the finding it repeats with `merge <duplicate>
   <kept>`: references in issues and recommendations move to the kept finding.
   Then `update` the kept finding if the duplicate cited places it misses.
4. Drop a finding that is wrong, unverified, or out of scope with
   `remove <id> --reason "..."`. The reason stays in the log and is shown when
   an agent later records a finding at the same place.

Resolve the overlapping findings `status` lists the same way. Continue to the
synthesis when nothing is left to review. A later session resumes the same
way, from `status`.

## Synthesis

When every category is `done` or does not apply, write the parts that need the
whole picture. `status` lists every finding with its id, severity, and title;
use `show` for detail.

```bash
audit-findings -a webserver add risk <<'EOF'
["Tenant isolation depends on a manual filter in every query."]
EOF
audit-findings -a webserver add recommendation <<'EOF'
{"priority": "P1", "text": "What to do first.", "findings": ["F1"]}
EOF
audit-findings -a webserver add issue <<'EOF'
{"title": "[Security] IDOR in GET /invoices/{id}", "labels": ["security", "critical"],
 "findings": ["F1"], "summary": "The problem and why it matters.",
 "acceptance": ["A request for another tenant's invoice returns 404", "A test covers it"]}
EOF
```

- Each issue gets one actionable fix. Group related findings with the same fix
  into one issue, such as several default secrets, rather than filing one issue
  per line. Use the title prefix the audit skill defines. Acceptance criteria
  are checkable statements. `labels` defaults to the severities of the issue's
  findings.
- The renderer composes each issue body from its findings: evidence, impact,
  and fix come from the findings, so write those fields to read well on their
  own.
- Every finding above `info` must be in an issue and a recommendation. Check it
  with `audit-findings -a <area> coverage`, which lists the findings missing
  from either and exits with an error until there are none; `--all` includes
  `info` findings.

## Rendering

1. Render:

   ```bash
   audit-findings -a <area> render
   ```

   It checks every location and snippet against the source again, writes
   `findings.json`, and renders it. For each problem it reports, reread the
   code and `update` the finding, or `remove` it with a reason if the code is
   not there. Run
   it again until it writes the report files.
2. Check the PDF visually: `pdftoppm -r 60 -png docs/audits/<area>/report.pdf /tmp/<area>-page`,
   then look at every page. Fix what renders badly, such as snippets too long
   to read, with `update`, and render again. Deliver only when every page
   reads cleanly.

To regenerate a report from a `findings.json` that has no log, run
`audit-findings render <path>/findings.json`; add `--no-check` if the source
has changed since. To continue such an audit, run `audit-findings import
<path>/findings.json` first; it creates the log next to the file.

## Delivering

In the chat, report:

1. The findings, file by file and line by line, with severity.
2. The counts per severity.
3. The paths of `findings.json`, `report.pdf`, `report.html`, and `issues.md`.

Do not open issues on GitHub or any other tracker unless the user asks.
