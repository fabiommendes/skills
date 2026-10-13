# full mode

You design. The tester writes tests, the implementer writes code, and the two
run pipelined.

1. Design, stubs, report seams and acceptance criteria.
2. Brief the tester on batch 1.
3. The tester returns tests. Run them, confirm red.
4. Brief the implementer on batch 1. Concurrently, brief the tester on batch 2.
5. The implementer reports. Run batch 1's tests **only**: batch 2's tests exist
   now and are red by design.
6. Green → brief the implementer on batch 2, brief the tester on batch 3.

The tester works from your stubs, so it never waits on the implementer. When a
batch forces an API change, revise the stubs and tell the tester before it
starts the next batch.

Both agents stay alive across batches.

## Briefs

The tester gets: acceptance criteria, the API stubs, the seams to test.

The implementer gets: acceptance criteria, the API stubs, the files in scope.

The same criteria, two different jobs, no shared reasoning. That independence is
what full mode buys: when tests and implementation meet without either having
seen the other, agreement is evidence rather than coincidence.
