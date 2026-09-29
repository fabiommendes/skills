---
name: tdd
description: Test-driven development with an implementer blind to the test code. Use when the user asks for TDD or to build a feature or fix a bug test-first.
argument-hint: "[lite|default|full]"
---

# Test-Driven Development

One red → green loop, run at three different agent counts. The mode changes who
writes the tests, not what a good test is or the order things happen in.

You are the **orchestrator** unless told otherwise.

## Modes

| Mode | Agents | Use when |
|---|---|---| 
| `lite` | you alone | Small change, one or two seams, no parallelism to win. |
| `default` | you + implementer | Most work. You write the tests; the implementer never reads them. |
| `full` | you + tester + implementer | Large surface, or test writing is substantial enough to deserve its own agent. |

Take the mode from the argument. With no argument, or if the argument is a command use `default`.

Read the section for your mode in [references/modes.md](references/modes.md),
not all three.

## Invariants

These hold in every mode.

- **Red before green.** The test for a behavior exists and fails for the right
  reason before that behavior is implemented.
- **One cycle, one slice.** A cycle delivers one vertical slice, worked in
  batches of at most 3 acceptance criteria. Needing more than about 3 batches
  means this should have been two cycles — split it.
- **Tests are never written from the implementation.** In `lite` the ordering
  enforces this. In `default` and `full` the implementer also never reads test
  code to decide what to build.
- **Batches are gated independently.** While one batch is being implemented,
  the next batch's tests may already exist and fail. Track which tests belong
  to which batch and gate a batch on its own tests only.

## Design

Before any test, design the public surface and nothing below it: function
signatures, types, class definitions, module structure. No implementation
details.

Write stubs for anything that does not exist yet. The stubs are the contract
both other roles work from, and they are what lets one batch start before the
previous one lands.

Design for testability. Push side effects out with dependency injection or
higher-order functions. Keep outer layers — HTTP handlers, CLI entry points,
browser-facing code — thin over an inner abstraction that holds the logic, so a
cheap seam exists to test at. [references/testing.md](references/testing.md)
covers where tests attach and what they should look like.

Name the seams you intend to test and the acceptance criteria, and report both
to the human in bullets before starting. Do not wait for approval. Stop and ask
only when a later batch needs a seam outside that set, which means the design
moved.

## The loop

1. Design the surface, write stubs, report seams and acceptance criteria.
2. Take the next batch: up to 3 acceptance criteria.
3. The batch's tests get written — by you or by the tester, per the mode.
4. Run them. Confirm they fail, and that they fail for the reason you expect. A
   test that passes against a stub is testing nothing.
5. The batch's implementation gets written from the criteria and the stubs,
   never from the test code.
6. Run the batch's tests. Green → next batch. Not green → diagnose, and if the
   test is wrong rather than the code, fix the test and say so.
7. After the last batch, run the whole suite and check the slice against its
   acceptance criteria.

When the strategy is not working, change it and say so. A batch that exposes a
wrong API assumption is the loop doing its job: revise the stubs, tell whoever
is downstream, continue.

## Refactoring

Small refactors inside the code you are already touching are in scope.
Refactoring is not the goal of a cycle unless the human says it is.

Anything visible from outside — renaming a public function, changing a
signature, moving a module — gets raised with the human first, even when it is
obviously an improvement.

## Spawning agents

Use the project's `tester` and `implementer` agents when they exist. Projects
override the defaults that way, and their definitions already carry the role
contract.

When the project defines neither, spawn a general agent with the matching brief
from [references/agent-briefs.md](references/agent-briefs.md) and request a
Sonnet-class model.

Keep spawned agents alive across batches; they accumulate the context that
makes later batches cheap.

When an agent reports that a test looks wrong, get the views to agree. You are
the final arbiter when they do not.

## Reporting

You and the human are peers. Be direct and concise, and skip the ceremony.

Report per batch in a line or two: what it covers, whether it went green. Also
report a design change, a new seam, or a disagreement between agents. Do not
announce that you filled in a stub — the stub existing implies it — and do not
report routine progress.
