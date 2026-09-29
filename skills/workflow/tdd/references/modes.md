# Modes

Read only the section for the mode you are running.

## Contents

- lite
- default
- full
- Briefs

## lite

You do everything: design, tests, implementation.

Honesty comes from ordering alone, so the ordering is strict. No line of
implementation before its test exists and fails.

Work one test at a time within the batch rather than writing the batch's tests
as a block. With a single agent there is no parallelism to buy, so the finer
loop is free, and each test can respond to what the last one taught you.

No agents to spawn, no briefs to write. Report per batch as usual.

## default

You design and write the tests. The implementer writes the code.

1. Design, stubs, report seams and acceptance criteria.
2. Write the batch's tests yourself.
3. Run them, confirm red.
4. Spawn or message the implementer with: the acceptance criteria in prose, the
   API stubs, the files in scope. Never the test code, and never a summary of
   how the tests are structured.
5. The implementer reports. Run the batch's tests.
6. Green → next batch, same implementer.

This is the strongest mode. It is the only one that gets a real red phase and a
blind implementer at the same time, and it costs one agent. Use it unless test
writing is large enough to deserve its own.

## full

You design. The tester writes tests, the implementer writes code, and the two
run pipelined.

1. Design, stubs, report seams and acceptance criteria.
2. Brief the tester on batch 1.
3. The tester returns tests. Run them, confirm red.
4. Brief the implementer on batch 1. Concurrently, brief the tester on batch 2.
5. The implementer reports. Run batch 1's tests **only** — batch 2's tests
   exist now and are red by design.
6. Green → brief the implementer on batch 2, brief the tester on batch 3.

The tester works from your stubs, so it never waits on the implementer. When a
batch forces an API change, revise the stubs and tell the tester before it
starts the next batch.

Both agents stay alive across batches.

## Briefs

The tester gets: acceptance criteria, the API stubs, the seams to test.

The implementer gets: acceptance criteria, the API stubs, the files in scope.

The same criteria, two different jobs, no shared reasoning. That independence is
what full mode buys — when tests and implementation meet without either having
seen the other, agreement is evidence rather than coincidence.
