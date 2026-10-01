---
type: plan
status: active
tags: [audit-skills, skill-validation, audit-webserver, audit-db, audit-dependencies, audit-privacy, audit-ux, audit-ui, audit-report]
relatedTo: [audit-report, audit-webserver, audit-db, audit-dependencies, audit-privacy, audit-ux, audit-ui]
---

# Handoff: validate the audit skills

The next session validates the audit skill family against its intent: run
each skill on fixtures with a known ground truth, score the results, and fix
the skills where they fall short.

## Where things are

- Skills: `skills/qa/audit-{report,webserver,db,dependencies,privacy,ux,ui}/`
  in this repository, installed with `./install.sh`.
- Fixtures, ground truth, and methodology: the `skills-validation` repository
  (`~/git/ai/skills-validation`), kept apart so `npx skills add` does not
  download it. Its README holds the shared tests T1 to T11 and the run
  procedure; each `<skill>/METHODOLOGY.md` holds the skill's intent, specific
  tests, and run log; each `<skill>/<repo>/GROUND-TRUTH.md` the answers.
- `audit-report/scripts/check_findings.py` checks every location and snippet
  in a `findings.json` against the source (T3).

## Status

| Skill | Fixtures with ground truth | Runs |
|---|---|---|
| `audit-webserver` | `vampi` | 1 (feedback applied in `2b4f346`) |
| `audit-db` | `lobsters` (real fixes), `ledger` (planted) | none |
| `audit-dependencies`, `audit-privacy`, `audit-ux`, `audit-ui` | planned in their `METHODOLOGY.md` | none |

## Next steps

1. Run `audit-db` on `ledger` and `lobsters`, each from a fresh session or a
   subagent with a plain user prompt; score against the ground truth.
2. Rerun `audit-webserver` on `vampi` to confirm the fixes, then on
   `juice-shop` for long-context behavior (risk R1).
3. Write the planted fixtures for the remaining skills.

## Risks to watch

- R1. Long codebases: inventories may exhaust context or tempt the agent to
  sample. `audit-db` asks to cover one module at a time; check whether it
  does on `lobsters` and `juice-shop`.
- R2. The audit skills invoke `audit-report` through the Skill tool. Installing
  one audit skill alone with `npx skills add` leaves it without
  `audit-report`; check the failure mode and document the dependency.
- R3. Severity drift between runs (T6); tighten the table wording where runs
  disagree.
- R4. `audit-ux` judgments are subjective; ground truth beyond the planted
  defects needs the user's review.
