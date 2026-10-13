# default mode

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
