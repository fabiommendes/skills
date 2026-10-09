# Validating an audit skill

Instructions for an agent asked to check that an `audit-*` skill uses
`audit-report` correctly. This is a review of the skill's text, not an audit
of a codebase: do not run the audit, and do not edit the skill unless asked.

Read `../SKILL.md` (the `audit-report` skill) first. It is the contract the
audit skill must follow; every check below refers to it. Then read the audit
skill's `SKILL.md` in full.

## What to check

Check every item and note each failure with its `SKILL.md:line`.

### 1. Frontmatter and introduction

- `name` is `audit-<area>`, and `<area>` is the directory name without the
  `audit-` prefix.
- `description` says what the audit covers, that it is "delivered as a
  PDF/HTML report with ready-to-paste GitHub issues", and when to use it
  ("Use when ...").
- The introduction says the skill delivers the report defined by the
  `audit-report` skill. When its scope overlaps another audit, it says which
  audit owns the shared concern (such as `audit-webserver` for access
  control).

### 2. Checklist

- The skill tells the agent to copy and track a checklist.
- The first item is `1. Load audit-report`; the last is
  `<n>. Synthesize and render`.
- Every checklist item has a matching `## <n>. <title>` section with the same
  number and title, in the same order.

### 3. Loading audit-report

The `## 1. Load audit-report` section must:

- tell the agent to invoke the `audit-report` skill now and start or resume
  the log, as its first action;
- give the area, equal to `<area>` from the skill name;
- give the issue title prefix, in square brackets, such as `[DB]`.

Fail the skill if it loads `audit-report` later than step 1, makes loading
optional, or describes the recording rules itself instead of deferring to
`audit-report`.

### 4. Categories

- Every category has a stable id in backticks next to its title, such as
  `### 3. IDOR (`idor`)` or `1. **Task completion (`tasks`):**`. Ids are
  lowercase, use only letters, digits, and hyphens, and are unique within the
  skill.
- The final step states the number of categories in words ("all ten
  categories"), and the number matches the categories listed.
- When a category can be not applicable, the skill says so rather than
  forcing a finding. It may say how to recognize it; it must not invent a
  field for it (`audit-report` uses `applies` and `note`).

### 5. Severity

- A `## Severity` table defines exactly the five levels `critical`, `high`,
  `medium`, `low`, and `info`, each with a meaning specific to this audit.

### 6. Inventory

When the skill builds a coverage table:

- it says to record it as an inventory table (or tables), names every
  column, and says what one row is ("one row per route");
- it does not refer to an `inventory` field, a list of tables, or any JSON
  shape.

### 7. Fields named in the instructions

Every field the skill tells the agent to fill must exist in `audit-findings`:

| Record | Fields |
|---|---|
| meta | `lang`, `title`, `project`, `date`, `scope`, `methodology` |
| category | `id`, `title`, `applies`, `note` |
| finding | `category`, `severity`, `title`, `location`, `snippet`, `language`, `description`, `impact`, `fix`, `conditions`, `screenshot` |
| strength | `text`, `category`, `evidence` |

Fail any other field name, such as `cwe`, `coverage`, `evidence` on a
finding, or `inventory`. Facts with no field of their own, such as a CVE id,
a WCAG criterion, or a measured query count, must be placed in an existing
field (`title`, `description`, `conditions`), and the skill must say which.

### 8. Synthesize and render

The last step must:

- tell the agent to record all categories, findings, and strengths as
  `audit-report` defines, write the synthesis, and render;
- give only audit-specific guidance on top: what goes in `location`,
  `conditions`, or `description` for this kind of finding, and when to group
  findings into one issue;
- defer delivery to `audit-report` or match it (findings with severity,
  counts, paths of the deliverables).

### 9. What the skill must not contain

Fail the skill if it:

- tells the agent to write, fill, or edit `findings.json` or
  `findings.jsonl`;
- refers to `render_report.py`, `check_findings.py`, a `scripts/` directory,
  or `uv run --with reportlab`;
- spells out `audit-findings` commands with a version pin. The pin lives in
  `audit-report` only; a second copy goes stale on the next release;
- names an `audit-findings` command or record kind that does not exist (see
  "Commands" below);
- tells the agent to install tools globally, or to open issues on GitHub
  without the user asking;
- tells subagents to record risks, recommendations, or issues; those belong
  to the main agent's synthesis.

### 10. Screenshots

When the audit needs screenshots (interface audits), the skill saves them in
`docs/audits/<area>/screenshots/` and puts the path relative to
`docs/audits/<area>/` in the finding's `screenshot`. It masks personal data in
screenshots when the audit handles personal data.

## Commands

Check every command the skill names against `audit-findings --help`. Take the
version pin from the `Run every command as` line of `../SKILL.md` and run, in
an empty temporary directory:

```bash
uvx audit-findings@<version> --help
```

Record kinds accepted by `add`: `category`, `finding`, `strength`, `risk`,
`recommendation`, `issue`, `inventory`, `row`.

## Dry run

Confirm that the skill's categories record cleanly. In an empty temporary
directory, outside every repository:

```bash
uvx audit-findings@<version> -a <area> init <<'EOF'
{"title": "Validation", "project": "validation", "scope": "-", "methodology": "-"}
EOF
uvx audit-findings@<version> -a <area> add category <<'EOF'
[{"id": "<id 1>", "title": "<title 1>"}, {"id": "<id 2>", "title": "<title 2>"}]
EOF
uvx audit-findings@<version> -a <area> status
```

List every category of the skill in the `add category` call, with the ids and
titles exactly as the skill writes them. The call must print one id per
category, and `status` must list the same number of categories as the final
step states. When the skill builds an inventory, also add it with the columns
the skill names and one row of placeholder cells:

```bash
uvx audit-findings@<version> -a <area> add inventory <<'EOF'
{"id": "<table id>", "title": "<title>", "columns": ["<column 1>", "<column 2>"]}
EOF
uvx audit-findings@<version> -a <area> add row <<'EOF'
{"table": "<table id>", "cells": ["-", "-"]}
EOF
```

Delete the temporary directory when done.

## Report

Reply with:

1. `OK` and the checks that passed, when nothing failed.
2. Otherwise, one line per failure: the check number, `SKILL.md:line`, what is
   wrong, and the fix. Mark each failure as **blocking** (the agent running
   the audit would record wrong data, skip a step, or run a command that
   fails) or **minor** (wording that works but drifts from the other audit
   skills).
3. The output of the dry run, trimmed to the ids and the `status` summary.
