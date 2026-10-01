---
name: audit-report
description: Defines the findings file shared by the audit-* skills and renders it into a PDF report, an HTML report, and ready-to-paste GitHub issues. Use when an audit skill reaches its report step, or when the user wants an audit report regenerated from a findings.json.
---

# Audit report

Every `audit-*` skill records its results in one findings file and renders it
with the script in this skill. The audit skill decides what to look for; this
skill decides how findings are recorded and delivered.

## Output directory

Write everything to `docs/audits/<area>/`, where `<area>` is the audit skill's
name without the `audit-` prefix (`webserver`, `dependencies`, `privacy`, `ux`,
`ui`). Create the directory if needed.

| File | Written by |
|---|---|
| `findings.json` | you, during the audit |
| `screenshots/*.png` | you, when a finding needs one (optional) |
| `report.pdf`, `report.html`, `issues.md` | the renderer |

## Recording findings

- Record only what you verified: code you read, a command you ran, a screen you
  saw. Never speculate, and never invent locations, CVEs, or quotes.
- One finding per distinct defect. The same mistake repeated in several places
  is one finding whose `location` lists every place.
- Give the exact location: `path:line` or `path:start-end` for code; route or
  screen plus the steps to reach it for interface findings.
- Quote the offending code in `snippet`, trimmed to the lines that show the
  problem. Mask secret values and personal data: keep the first four
  characters of a secret and replace the rest with `****`.
- Assign severity with the severity table of the audit skill you are running.
  Every audit uses the same five levels: `critical`, `high`, `medium`, `low`,
  `info`.
- Record exploitability or reproduction conditions in `conditions`: feature
  flags, required configuration, roles, devices.
- Record what is **correct** in `strengths`, with evidence. Strengths prove
  coverage: "every handler in `routers/orders.py` checks ownership" shows the
  router was read.
- Keep every category of the audit in `categories`. Mark the ones that do not
  apply with `"applies": false` and the reason in `note`.
- Write all text in one language and set `lang` to `en` or `pt`.

## Findings file

`findings.json` follows this shape:

```json
{
  "lang": "en",
  "title": "Security Audit Report",
  "project": "acme-api",
  "date": "2026-10-01",
  "scope": "FastAPI backend in `src/`, React frontend in `web/`.",
  "methodology": "Paragraphs separated by blank lines: the detected stack and how each category maps onto it.",
  "categories": [
    {"id": "idor", "title": "IDOR", "note": "Ownership is checked with a `get_owned_or_404` helper."},
    {"id": "xss", "title": "XSS", "applies": false, "note": "no HTML rendering of user input"}
  ],
  "findings": [
    {
      "id": "F1",
      "category": "idor",
      "severity": "critical",
      "title": "GET /invoices/{id} does not check the tenant",
      "location": "src/api/invoices.py:42-47",
      "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
      "language": "python",
      "description": "What is wrong.",
      "impact": "What an attacker or user can do, or what goes wrong.",
      "fix": "The suggested fix.",
      "conditions": "Any authenticated user."
    }
  ],
  "strengths": [{"category": "idor", "text": "Every handler in the users router checks ownership.", "evidence": "src/api/users.py:10-80"}],
  "risks": ["Tenant isolation depends on a manual filter in every query."],
  "recommendations": [{"priority": "P1", "text": "What to do first.", "findings": ["F1"]}],
  "issues": [
    {
      "title": "[Security] IDOR in GET /invoices/{id}",
      "labels": ["security", "critical"],
      "findings": ["F1"],
      "summary": "The problem and why it matters.",
      "acceptance": ["A request for another tenant's invoice returns 404", "A test covers it"]
    }
  ],
  "inventory": {"title": "Route inventory", "columns": ["Method", "Path"], "rows": [["GET", "/invoices/{id}"]]}
}
```

- Optional fields: `lang` (default `en`), `risks`, and `inventory`; `applies`
  and `note` in categories; `snippet`, `language`, `conditions`, and
  `screenshot` (a path relative to `findings.json`) in findings; `category` and
  `evidence` in strengths; `labels` in issues (defaults to the severities of
  the issue's findings).
- `inventory` is the coverage table the audit skill asks you to build. The
  renderer prints it as an appendix.
- Each issue gets one actionable fix. Group related findings with the same fix
  into one issue, such as several default secrets, rather than filing one issue
  per line. Use the title prefix the audit skill defines. Acceptance criteria
  are checkable statements.
- The renderer composes each issue body from its findings: evidence, impact,
  and fix come from the findings, so write those fields to read well on their
  own.

## Rendering

1. Run the renderer from this skill's directory:

   ```bash
   uv run --with reportlab --with pillow python <this-skill-dir>/scripts/render_report.py docs/audits/<area>/findings.json
   ```

   Without `uv`, create a virtual environment outside the project
   (`python3 -m venv /tmp/audit-venv`), install `reportlab` and `pillow` in it,
   and run the script with its Python. Install nothing globally.
2. If the script reports problems in `findings.json`, fix each one and run it
   again. Continue only when it writes the three files.
3. Check the PDF visually: `pdftoppm -r 60 -png docs/audits/<area>/report.pdf /tmp/<area>-page`,
   then look at every page. Fix what renders badly, such as snippets too long
   to read, by editing `findings.json`, and render again. Deliver only when
   every page reads cleanly.

## Delivering

In the chat, report:

1. The findings, file by file and line by line, with severity.
2. The counts per severity.
3. The paths of `findings.json`, `report.pdf`, `report.html`, and `issues.md`.

Do not open issues on GitHub or any other tracker unless the user asks.
