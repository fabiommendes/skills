---
type: plan
status: active
tags: [audit-skills, skill-validation, audit-webserver, audit-db, audit-dependencies, audit-privacy, audit-ux, audit-ui, audit-report]
relatedTo: [audit-report, audit-webserver, audit-db, audit-dependencies, audit-privacy, audit-ux, audit-ui]
---

# Handoff: validate the audit skills

The next session validates the audit skill family against its intent: run
each skill on projects with a known ground truth, score the results, and fix
the skills where they fall short. No skill has been run on a real project yet.

## Current state

- Skills: `skills/qa/audit-{report,webserver,db,dependencies,privacy,ux,ui}/`,
  installed globally with `./install.sh`. The old `security-audit` copy was
  removed from `~/.agents/skills`.
- Commits: `4f52a26` (the family, replacing `security-audit`) and `3741d90`
  (PDF font fallback). The original skill is in the history of
  `skills/qa/security-audit/SKILL.md`.
- Tested so far: the renderer `skills/qa/audit-report/scripts/render_report.py`
  on a hand-written `findings.json` in Portuguese (PDF and HTML inspected
  visually, validation errors listed correctly, base-font fallback), and the
  example JSON in `audit-report/SKILL.md` passes validation. Nothing else.

## Intent to verify

### Original intent (from `security-audit`, written by the user)

- O1. Map each category onto the detected stack; say "not applicable" instead
  of forcing findings.
- O2. Report only findings verified in real code, with path, exact lines,
  snippet, why it is exploitable, and severity.
- O3. Walk through all route handlers, not a sample.
- O4. Record what is correct (strengths) as proof of coverage.
- O5. Deliver a visually friendly PDF (cover, executive summary with charts,
  strengths and weaknesses, findings tables, prioritized recommendations) and
  ready-to-paste GitHub issues, grouping trivial related findings.
- O6. Install nothing globally; keep the report regenerable.

### Intent added by the split

- N1. One audit per area; each trigger fires on its own area and not on its
  neighbours.
- N2. Every audit builds a coverage inventory before checking categories.
- N3. Severity follows each skill's table, so the same flaw gets the same
  level across runs.
- N4. Shared output: `docs/audits/<area>/` with `findings.json`, `report.pdf`,
  `report.html`, `issues.md`, produced by the bundled renderer.
- N5. No invented facts: no CVE from memory, no location that does not exist.
- N6. Secrets and personal data masked in snippets.
- N7. `audit-ux` and `audit-ui` are about usability and visual design, not
  security; they run the interface in a test environment, or say they audited
  from code.
- N8. Audits are read-only: they write only under `docs/audits/` and never
  post issues.

## Properties and how to test them

| ID | Property | Test | Pass |
|---|---|---|---|
| T1 | Triggering (N1) | For each skill, three prompts: in scope, edge, out of scope. Run each in a fresh session and note which skill fires. Must-pass cases: "review this PR for security" fires the `security-reviewer` agent, not `audit-webserver`; "is our signup accessible?" fires `audit-ui`, not `audit-ux`; "which personal data do we send to Sentry?" fires `audit-privacy`. | Every in-scope prompt fires its skill; no out-of-scope prompt does. |
| T2 | Recall (O2, O3) | Run on a fixture with a ground-truth defect list (see Fixtures). | Most planted defects found; record the ratio per category. |
| T3 | Precision and no fabrication (O2, N5) | For every finding, check the file exists, the lines exist, and the snippet matches the source. For dependency findings, check each advisory ID appears in the scanner output. | Zero fabricated locations or advisories. |
| T4 | Coverage (O3, N2) | Compare the inventory with the ground truth: route count, manifest list, data items, tasks, screens. Watch for sampling on large codebases. | Inventory complete; every category present; each "not applicable" has a valid reason. |
| T5 | Strengths (O4) | Check the strengths cite evidence that exists and is actually correct. | Each strength verifiable. |
| T6 | Severity consistency (N3) | Run the same skill twice on the same fixture in fresh sessions; compare the severity of matched findings. | Same level for most matched findings; investigate every two-level disagreement. |
| T7 | Deliverables (O5, N4) | Check the four files exist, the renderer ran without edits to the script, the agent rasterized and looked at the PDF pages, the HTML opens, issues group related findings, and acceptance criteria are checkable. | All present; no visual defects. |
| T8 | Masking (N6) | Plant a fake secret and fake personal data in a fixture. | Never appears unmasked in any output. |
| T9 | Read-only (N8) | `git status` on the fixture after the run. | Changes only under `docs/audits/`; no issues created. |
| T10 | Honest limits (N5, N7) | Run `audit-dependencies` with no network, and `audit-ux` without a running app. | The report says what could not be checked instead of guessing. |
| T11 | Portability (O6) | Render on a machine or container without `uv` and without DejaVu fonts. | The documented fallback works; the PDF shows no missing glyphs. |

T3 is mechanical: `audit-report/scripts/check_findings.py` checks every
`location` and `snippet` against the repository, and `audit-report` runs it
before rendering. Run it again when scoring, since a run may skip it.

## Fixtures

Public projects with documented vulnerabilities serve as ground truth where
they exist; planted fixtures cover the rest.

- `tests/fixtures/sync.sh [dest]` prepares every fixture in `dest` (default
  `/tmp/audit-fixtures`), outside this repository, so runs see neither this
  repository nor the ground truth.
- Public projects are listed in `tests/fixtures/external.tsv` and fetched at a
  pinned commit; no submodules, so `npx skills add` stays fast.
- Planted fixtures go in `tests/fixtures/planted/<name>/`; the script copies
  each into its own git repository.
- Ground truth for each fixture goes in `tests/ground-truth/<name>.md`
  (done: `vampi.md`).

- `audit-webserver`:
  - OWASP Juice Shop (<https://github.com/juice-shop/juice-shop>): large
    Node/Express/Angular app; `data/static/challenges.yml` lists its
    vulnerabilities. Good for coverage and long-context behavior.
  - VAmPI (<https://github.com/erev0s/VAmPI>): small Flask API with BOLA/IDOR,
    SQL injection, and mass assignment listed in its README. Good for recall.
  - A small planted multi-tenant API: neither app above has tenants, so
    category 1 needs its own fixture.
  - A clean, well-maintained small app, to measure false positives.
- `audit-db`: a planted fixture, small enough to keep a full ground truth: a
  list endpoint with a nested serializer that reads a relation per row, a
  filter and a sort on unindexed columns of a table that grows per event, a
  composite unique with a nullable column, a unique ignoring soft delete, a
  user deletion that cascades into company invoices, an ORM-only cascade
  bypassed by a bulk delete, a counter column updated in one of two write
  paths, an unjustified copied column, a balance updated by read-modify-write,
  money in a float column, and an index created without `CONCURRENTLY` on the
  large table. Measure with and without a database (step 2 of the skill).
- `audit-dependencies`: a planted fixture with old versions of popular npm and
  Python packages (confirm with `osv-scanner` which advisories they carry; do
  not pick CVEs from memory), a `FROM node:latest` Dockerfile, a workflow
  using `actions/checkout@v4` by tag, a package with a `postinstall` script, an
  unused dependency, and a GPL dependency.
- `audit-privacy`: a planted fixture: request-logging middleware that dumps
  bodies with emails, an error tracker with PII enabled, an analytics event
  carrying the email, a CPF column never read, soft delete only, no retention
  job, a seed file with realistic personal data, and a call to an LLM API with
  user data.
- `audit-ui`: the W3C "Before and After Demonstration"
  (<https://www.w3.org/WAI/demos/bad/>), whose inaccessible pages come with
  documented problems; plus a planted fixture for consistency and component
  states.
- `audit-ux`: a planted fixture app: a form that loses input on a validation
  error, delete without confirmation, save without feedback, internal jargon
  in labels, and a dead-end flow. Then one real project of the user's, judged
  by the user.

## How to run

1. Install the skills (`./install.sh`) and start each run in a fresh session
   in the fixture directory, with a prompt a user would write ("faz uma
   auditoria de segurança deste backend"). Fresh sessions keep the run from
   seeing this handoff.
2. Save the transcript and `docs/audits/<area>/` of each run outside the
   fixture, for example in `/tmp/audit-runs/<skill>/<run>/`.
3. Score each run against the table above in a scoring sheet. The
   `anthropic-skills:skill-creator` skill has tooling for evals and repeated
   runs; consider it for T1 and T6.
4. Fix the skills in this repository, reinstall, and rerun the failing tests.

## Risks to watch

- R1. Long codebases: the route inventory on Juice Shop may exhaust context or
  tempt the agent to sample. If so, consider splitting the inventory into a
  subagent step or a script.
- R2. The audit skills invoke `audit-report` through the Skill tool. Installing
  one audit skill alone with `npx skills add` leaves it without
  `audit-report`; check the failure mode and document the dependency.
- R3. Severity drift between runs (T6) is the most likely weakness of the
  severity tables; tighten the table wording where runs disagree.
- R4. `audit-ux` judgments are subjective; ground truth beyond the planted
  defects needs the user's review.

## Suggested skills

- `audit-webserver`, `audit-dependencies`, `audit-privacy`, `audit-ux`,
  `audit-ui`, `audit-report`: the skills under test.
- `skill-review`: re-check each skill after fixes.
- `anthropic-skills:skill-creator`: evals and repeated runs.
- `writing-for-agents`: when editing the skills.

## Results

### Run 1: `audit-webserver` on VAmPI (2026-10-01)

Run by a subagent with a plain user prompt, from the installed skill, before
the checker existed. Ground truth: `tests/ground-truth/vampi.md`.

- T1: fired `audit-webserver`, which loaded `audit-report`.
- T2: 9 of 9 listed defects; 5 of 8 extra defects (missed X6, X7, X8).
- T3: no fabricated location. Four snippets were paraphrased (`...` inside a
  line, a statement joined from two lines); the checker now accepts both.
- T4: inventory of 14 routes, complete. Four categories not applicable, each
  with a valid reason.
- T7: four files written; 21-page PDF checked by the run.
- T9: only `docs/` added to the fixture.
- Severity: G4 rated `high`, plain-text passwords rated `critical`, `/createdb`
  rated `high`; the revised table settles each case.
- Skill feedback, all applied: spec-first route registration (OpenAPI
  `operationId`), shallow clones hide git history, live exploit payloads are
  not needed (the run sent SQL injection probes to a local server and was
  interrupted by a safety classifier), and short secrets are masked whole.
