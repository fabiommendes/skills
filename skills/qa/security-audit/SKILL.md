---
name: security-audit
description: Audit a codebase for five classes of security flaw (tenant isolation, client-side-only authorization, IDOR, hardcoded secrets, unsanitized input/XSS) and produce a PDF report plus ready-to-paste GitHub issues
---

# audit

Review a codebase for five classes of security flaw, then deliver a visual PDF
report and a set of ready-to-paste GitHub issues.

Before auditing anything, detect the project's stack: language, framework,
ORM/query builder, auth mechanism, frontend, and deploy files (Docker, CI, Helm,
Terraform). Map each category below onto that stack's equivalent. When a
category does not apply — for example, XSS in a project with no frontend — say
so explicitly instead of forcing a finding.


## Categories

### 1. Unlocked database (tenant/owner isolation)

In Supabase this is missing RLS. In hand-rolled APIs it is list, search,
aggregate, report, and export queries that do not filter by the authenticated
user or by the organization/workspace/tenant they belong to.

Identify first *which* isolation mechanism the project uses — RLS, tenant
middleware, manual `user_id` filtering — then point out where it is absent or
leaky.

### 2. Authorization decided in the browser

Privileged operations (admin, settings, user management, write actions) where
the frontend hides the UI by role (`isAdmin`, `canEdit`, `role`, ...) but the
server performs no equivalent check.

Cross-reference every frontend role gate with its corresponding endpoint and
confirm the backend validates the privilege on every sensitive route.

### 3. IDOR

Routes that fetch, modify, or delete an object by ID (path, query, or body)
without verifying the object belongs to the caller's user or tenant.

Walk through *all* backend route handlers systematically — not a sample.

### 4. Exposed keys (hardcoded)

API keys, tokens, passwords, signing secrets (JWT, webhooks), private keys, and
default credentials embedded in source, configs, `docker-compose`, charts, CI,
scripts, and documentation.

Pay particular attention to:

- Public defaults that become real secrets when not overridden, e.g.
  `${VAR:-default-value}`.
- Missing startup validation that would reject those defaults.
- Secrets committed in git history.
- Keys bundled into the frontend build.

### 5. Unsanitized input (XSS)

Frontend: `innerHTML` / `dangerouslySetInnerHTML` and framework equivalents
(`v-html`, `[innerHTML]`), markdown or HTML rendered without sanitization,
user-controlled URLs in `href`/`src` (`javascript:`), `eval` / `new Function`.

Backend: user input reaching email HTML, templates, or responses without
escaping.

Check whether the project already has a sanitization library and whether it is
applied at each point found.


## Audit rules

- Report only findings verified in real code. No speculation.
- For each finding give: file path, exact line number(s), the code snippet, why
  it is exploitable, and severity (critical / high / medium / low /
  informational).
- List findings file by file, line by line.
- Also record what was checked and is **correct** (e.g. "router X validates
  ownership in every handler"). This becomes the strengths section and proves
  the audit's coverage.
- Note exploitability conditions: feature flags, required insecure config, etc.


## Report

After the audit, generate a visually friendly PDF at
`docs/security-audit/security-audit-report.pdf` containing:

1. **Cover** — title "Security Audit Report — \<project name\>", date, audited
   scope, and a methodology note explaining how each category was mapped onto
   the detected stack.
2. **Executive summary** — total findings per severity, a doughnut chart by
   severity, and a bar chart by category. Palette: critical `#B91C1C`, high
   `#EA580C`, medium `#D97706`, low `#2563EB`, strength `#059669`.
3. **Strengths and weaknesses** — what is protected (with evidence) and the
   central risks.
4. **Detailed findings table** per category: Severity | File:line | Description,
   with a colored severity chip.
5. **Prioritized recommendations** (P1, P2, P3, ...).
6. **"GitHub issues" section** at the end — see below.

### GitHub issues section

For each actionable finding, include the complete Markdown text of an issue,
ready to copy and paste, inside a delimited block (e.g. between
`--- ISSUE n ---` and `--- END ISSUE n ---`). Each issue contains:

- Title in the form `[Security] <short description of the flaw>`
- Suggested labels: `security` + severity
- Description of the problem and why it is exploitable
- Evidence: `file:line` with the code snippet
- Impact
- Suggested fix
- Acceptance criteria (a verifiable checklist)

Group related trivial findings into a single issue where it makes sense (e.g.
several default secrets on the same theme) so the issue list is not spammed.

### PDF generation rules

- Install nothing globally. Use an isolated environment (a Python venv with
  `reportlab` + `matplotlib`, or the local stack's equivalent; a headless
  browser, `wkhtmltopdf`, or `pandoc` doing HTML→PDF is also fine).
- Leave the generator script in `docs/security-audit/` so the report can be
  regenerated later.
- Verify the generated PDF: page count, chart rendering, and table legibility
  (rasterize the pages if possible). Fix visual defects before delivering.
- A4 pages, ~2cm margins, header/footer with the report name and page number.


## Deliverables

1. The PDF report.
2. The findings list in the chat, file by file, line by line.
3. The path of every generated file.