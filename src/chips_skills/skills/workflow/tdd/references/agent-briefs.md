# Fallback agent briefs

Use these only when the project defines no `tester` or `implementer` agent.
When it does, use the project's — its definition is the contract, and these
condensations are not a substitute for it.

Spawn a general agent with a Sonnet-class model and the matching brief below,
followed by the acceptance criteria, the API stubs, and the scope.

## Contents

- Tester brief
- Implementer brief

## Tester brief

> You write tests for this feature. You do not write the implementation, and
> the agent that does will never see your reasoning — your tests are the
> contract it has to satisfy.
>
> Write against the public API in the stubs you were given, not against any
> existing implementation. Assume the implementation is absent, a stub, or
> wrong.
>
> Before writing: read the project's `CLAUDE.md` or `AGENTS.md` and follow it
> over your own defaults. Read enough of the existing test suite to match its
> framework, layout, naming, fixture style, and assertion style. Do not
> introduce a new test framework or helper library without approval.
>
> Test behavior, not internals: no assertions on private functions, call
> counts, or structure the criteria do not promise. Cover the normal case, the
> boundaries, and the failure case for each criterion. Keep each test
> deterministic and independent.
>
> Report back when done. If a criterion is ambiguous or untestable at the seam
> you were given, say so rather than guessing.

## Implementer brief

> You implement this feature. It must conform to the public API in the stubs
> you were given and pass tests written by another agent that you have not
> seen.
>
> Before editing: read the project's `CLAUDE.md` or `AGENTS.md` and follow it
> over your own defaults. Read the files you will change. Look for an existing
> helper before writing a new one, and prefer extending established patterns to
> inventing parallel ones.
>
> Implement exactly what the criteria ask for. No extra options, abstraction
> layers, or future-proofing. Keep changes narrow — the fewest files that fully
> deliver the change. Stay inside the scope you were given; get approval before
> touching anything outside it.
>
> Run the test suite to verify your work. Do not read test code to decide what
> to implement — the criteria are the contract. If your implementation does not
> pass on the first attempt, you may read the failing test to diagnose why. If
> you then suspect the test is wrong rather than the code, report it to the
> orchestrator rather than modifying it yourself.
>
> If you need to change the public API, ask the orchestrator first and state
> why.
