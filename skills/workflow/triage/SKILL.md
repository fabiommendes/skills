---
name: triage
description: Triage bugs and technical debt into a prioritized backlog for the human to approve. Use when the user asks to triage issues, prioritize bugs, groom the backlog, or find technical debt worth paying down.
argument-hint: "[bugs|debt|all]"
---

# Triage

You act as the project's maintainer: you gather what is wrong with the project,
classify it, and propose what to do first. The human decides the priorities;
you prepare the decision and carry it out.

Take the scope from the argument: `bugs`, `debt`, or `all`. With no argument,
use `all`.

## 1. Gather

Find where the project tracks work: an issue tracker (`gh issue list`), backlog
or issue files in the repo, or both. If you find none, ask the human where
work is tracked.

Collect the inventory for the scope:

- **Bugs:** open bug reports, failing and flaky tests, crashes in logs the human
  points you to.
- **Debt:** `TODO`, `FIXME`, and `HACK` comments; linter and type-checker
  warnings; deprecated APIs and outdated dependencies (use the project's audit
  tool); duplicated code; modules with no tests.

For debt, find the **hotspots**: files that change often and are complex. Rank
files by commit count over the last year (`git log --format= --name-only
--since=1.year | sort | uniq -c | sort -rn`), and read the top of that list.
Debt charges **interest** only where code changes; debt in a file nobody
touches can wait.

The step is done when every item in the tracker and every finding above is in
the inventory, each with a one-line description and its source.

## 2. Classify

For each item, record:

- **Kind:** `bug`, `debt`, `feature`, `question`, `duplicate` (of which item), or
  `invalid`.
- **Impact:** for bugs, what breaks and for how many users. Data loss, security,
  and wrong results outrank crashes; crashes outrank cosmetic issues. For debt,
  the interest: how often the code changes, and what the debt slows down or
  makes risky.
- **Effort:** `S` (hours), `M` (a day or two), or `L` (more; propose a split).
- **Confidence:** `reproduced`, `plausible`, or `needs info`, with what is
  missing.

For a bug whose cause is unclear, dispatch the `investigator` agent rather than
guessing. For a bug report missing a reproduction, draft the question to the
reporter.

## 3. Propose

Rank the items by impact against effort. Security and data-loss bugs go first
regardless of effort. Present to the human:

1. The ranked list: kind, impact, effort, confidence, and one line on why it
   sits at its rank.
2. Duplicates and invalid items you propose to close, each with the reason.
3. Items that need information, with the question for each.
4. Quick wins: high impact, `S` effort.

Stop here and wait for the human's decisions. Re-rank as they direct.

## 4. Apply

After the human approves, carry out only what they approved:

- Update the tracker: labels, priorities, comments, and closing duplicates.
  Show the exact comments before posting them.
- Create issues for approved debt items, each with the evidence and the
  hotspot data behind it.
- Report the next steps for the top items: bugs go to the `investigator`, then
  the `tester` and `implementer`; debt goes through the `safe-refactor` skill.
