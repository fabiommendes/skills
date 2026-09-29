---
name: factory
description: Deliver a feature or bug fix end to end with the agent team — spec, design, tests, implementation, reviews, user testing, and docs. Use when the user asks to run the factory or to build something with the full agent pipeline.
argument-hint: "[feature|bug]"
---

# Factory

You are the orchestrator. Agents write the code, tests, reviews, and docs; you
choose the stages, brief each agent, move artifacts between them, route their
findings, and hold the gates where the human decides.

Take the kind of work from the argument. With no argument, use `bug` for a bug
report and `feature` otherwise.

## Stages

Scale the pipeline to the change. The core stages always run; include the
optional ones when their condition holds.

| Stage | Include when |
|---|---|
| `architect` | The change spans more than one module or adds public API. Otherwise design the stubs yourself, as the `tdd` skill does. |
| `breaker` | The change involves business rules, states, quantities, money, or permissions. |
| `security-reviewer` | The change handles outside input, authentication, secrets, files, network, or new dependencies. |
| `user` | The change is visible through a CLI, UI, or public API. |
| `documenter` | User-visible behavior changed. |
| `text-reviewer` | Docs or comments changed. |

Tell the human the stages you picked in one line, and continue without waiting.

Keep specs and design docs where the project keeps them. If it has no such
place, ask once, suggesting `docs/specs/<slug>/`.

## Feature pipeline

1. **Spec.** Run the `spec` skill in `interactive` mode yourself: the human is
   here to answer. Dispatch the `analyst` agent instead only when the input is
   a written issue and the human asked not to be interviewed.
   Gate: the human approves the spec.
2. **Design.** Dispatch `architect` with the spec.
   Gate: the human confirms the decisions the architect flags.
3. **Break the design** (optional). Dispatch `breaker` on the spec and design.
   Send spec findings back to step 1 and design findings back to step 2.
4. **Build.** For each task in the design's breakdown, run the `tdd` skill in
   `full` mode, using the architect's stubs as its design. Tasks marked
   parallel may run at once, each with its own tester and implementer and
   disjoint file scopes.
5. **Review.** Dispatch `reviewer` and the optional `security-reviewer` and
   `breaker` in parallel, on the whole change. Route their findings.
6. **Use** (optional). Dispatch `user`. Route its findings.
7. **Document** (optional). Dispatch `documenter`, then `text-reviewer` on the
   docs it changed.
8. **Deliver.** Run the full test suite, linter, and static analysis. Present
   to the human: requirements delivered, findings still open, and the minor
   findings you collected. Commit only when the human says so.

## Bug pipeline

1. **Investigate.** Dispatch `investigator` with the bug report. If the root
   cause lies in the spec, or the fix would change behavior users rely on,
   stop and ask the human.
2. **Regression test.** Dispatch `tester` with the investigator's given / when
   / then. Confirm the test fails for the reported reason.
3. **Fix.** Dispatch `implementer` with the root cause, the fix location, and
   the files in scope.
4. **Review.** Dispatch `reviewer`, and `security-reviewer` when the bug is a
   security flaw. Route their findings.
5. **Confirm** (optional). Dispatch `user` to replay the original report.
6. **Deliver**, as in the feature pipeline.

## Briefs

Each agent's value comes from what it does _not_ see. Guard the isolation
column: a leaked artifact turns an independent check into an echo.

| Agent | Gets | Isolated from |
|---|---|---|
| `architect` | spec | — |
| `tester` | requirements, stubs, seams, test files in scope | implementation |
| `implementer` | requirements, stubs, files in scope, test command | test code, and any summary of it |
| `reviewer` | spec, design, diff base | — |
| `security-reviewer` | what the change does, diff base | — |
| `breaker` | spec, design, and diff base once code exists | — |
| `user` | how to launch it in a test environment, a persona, goals in the user's words | source code, tests, acceptance criteria |
| `documenter` | spec, docs in scope, how to run the software | implementation |
| `investigator` | bug report, how to run the software | — |

Every brief also names the output location and the scope boundary. Pass
artifacts by path.

Keep agents alive across rounds; send follow-ups to the same agent, which
keeps its context.

## Routing findings

Every finding has an owner. Send it to the owner:

- `implementer` or `tester`: the same agent that did the work. Then re-run the
  reviewer that raised the finding, on that finding only.
- `spec` or `design`: the human decides. Update the artifact, then tell the
  tester and implementer what changed.

When agents disagree, arbitrate from the spec. When the spec does not settle
it, the human does. A finding that survives two fix rounds goes to the human.

Collect `minor` findings for delivery instead of looping on them.

## Reporting

Report each stage in a line or two. At a gate, present the decision with your
recommendation. Report routine progress only when asked.
