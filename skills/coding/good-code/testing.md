# Testing

## Contents

- What to test
- Seams
- Choosing an approach
- Assertion density
- Good tests
- Bad tests
- Mocking
- Determinism
- Test code

## What to test

- Tests, like code, are debt. Be strategic about when and how you write them.
- Test contracts: complex logic, business rules, user actions. Do not test
  trivial implementation details. Do not write tests just to increase
  coverage.
- Test boundary conditions explicitly; that's where the bugs are.
- Prefer static guarantees over tests. Do not write tests for things the type
  system can enforce. For type-level code itself (generic helpers, conditional
  or mapped types), write type-level tests where the language supports them
  (e.g., `expectTypeOf` in TypeScript, `assert_type` in Python).
- When fixing a bug, first write a test that reproduces it and fails for the
  reported reason, then fix it. Name the test after the behavior that was
  broken, not after the issue number.

## Seams

A **seam** is the public boundary you observe behavior at. Tests attach to
seams, never to internals.

Prefer the innermost seam that covers the behavior. For "user can reset their
password" the candidates might be:

- `POST /auth/reset`: the HTTP endpoint. Real request, slow.
- `resetPassword(email, clock, mailer)`: the service function. Fast.
- `TokenGenerator.create()`: internal. Do not test this; it breaks on refactor.

Test the service function. The endpoint should be a thin generic layer over it,
holding routing and serialization and no logic of its own. When the outer layer
is thin, testing the inner one covers the behavior at a fraction of the cost.

This is a design obligation as much as a testing one. When the only seam
covering a behavior is expensive (an HTTP round trip, a browser, a live
database), logic is usually stranded in the outer layer. Pull it into an inner
abstraction and test there.

Expensive tests still earn a place, but as a small number of broad ones: enough
to verify the bridge between the outer layer and the inner abstraction is wired
correctly. One test that exercises the endpoint and asserts many properties
beats ten that each pay the setup cost to assert one thing.

## Choosing an approach

In order of preference:

**1. Property-based testing or fuzzing.** Best where invariants exist: round
trips, idempotence, ordering, conservation. Build the generators, strategies, or
factories once and reuse them across tests. That reuse is what keeps the suite
small.

**2. Example-based testing**, table-driven where it fits: one test function over
a table of input and expected output pairs. Use this for pure functions with no
side effects. Use the framework's parametrization (`pytest.mark.parametrize`,
`test.each`) rather than a loop, so each case reports on its own. Move examples
into fixture files when they get bulky.

For large structured outputs (rendered HTML, generated code, CLI output) where
writing the expected value by hand is impractical, use snapshot or golden-file
tests. The golden file is the expected value: review every diff to it as you
would review code, and never regenerate it just to make a test pass. Strip
unstable parts (timestamps, ids, absolute paths) and keep snapshots small enough
to read. A snapshot nobody reads is a tautology.

**3. Imperative tests with mocks.** Only when neither of the above works. See
[Mocking](#mocking).

Do not layer these. If a property covers a behavior, do not also write examples
for it. The goal is the smallest set of tests that covers the scenarios.

## Assertion density

Judge by what the test costs to run.

**Cheap** (no fixture setup, no database, no network, no process spawn): one
logical assertion per test. A failure then points straight at the behavior that
broke.

**Expensive** (database reinitialization, external services, browser, large
fixtures): bundle assertions. Drive the happy path once and assert everything
observable about the result. Splitting these into isolated tests multiplies the
setup cost and makes the suite slow enough that it stops being run, which costs
more than the lost precision.

Edge cases stay fine-grained either way. They are usually cheap, and a bundled
edge-case test tells you little when it fails.

## Good tests

Tests verify behavior through public interfaces. Code can change entirely; tests
shouldn't. A good test reads like a specification.

```typescript
// GOOD: tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

- Tests behavior callers care about
- Uses the public API only
- Survives internal refactors
- Describes WHAT, not HOW

## Bad tests

**Implementation-coupled.** Mocks internal collaborators, tests private methods,
or verifies through a side channel. The tell: it breaks when you refactor but
behavior hasn't changed.

```typescript
// BAD: asserts on an internal call
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

```typescript
// BAD: bypasses the interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: verifies through the interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**Tautological.** The expected value is computed the way the code computes it,
so the test passes by construction and can never disagree with the code.

```typescript
// BAD: expected value recomputes the implementation
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: expected value is an independent literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

Expected values must come from an independent source of truth: a known-good
literal, a worked example, the spec.

Properties are not tautologies. `decode(encode(x)) === x` asserts a relation the
implementation must satisfy, and it can fail: that is an independent source of
truth. Re-running the implementation's own algorithm to produce the expected
value is not.

## Mocking

Prefer real objects. Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes; prefer a test database)
- Time and randomness
- File system (sometimes; prefer temporary directories)

Don't mock your own classes and modules, internal collaborators, or anything
else you control.

A boundary you injected is a boundary you can substitute, so mockability follows
from the injection rules in [SKILL.md](SKILL.md). Shape the injected interface
as one function per external operation rather than one generic fetcher:

```typescript
// GOOD: each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

Each mock then returns one specific shape, needs no conditional logic, shows
which endpoints a test exercises, and keeps type safety per endpoint.

## Determinism

- Each test is independent: no shared mutable state, no reliance on test order.
- No real clock, network, or randomness unless the behavior under test is about
  them. Inject or fake them instead; seed generators when you need randomness.
- Never `sleep` to wait for something to happen. Wait on the condition itself
  with a timeout, or control the clock. A test that passes only when the
  machine is fast enough is flaky.

## Test code

- Tests are code: keep them readable above all else, refactor them, and delete
  them when they stop adding value.
- Name each test after the behavior it pins down.
- Match the existing suite: framework, layout, naming, fixture style, and
  assertion style. Do not introduce a new test framework or helper library
  without approval.
- Reuse the project's fixtures, factories, and generators before writing new
  ones. Build test data with builders or factories that fill sensible defaults,
  and set only the fields relevant to the test, so the test shows what matters.
- Do not branch on the result to decide what to assert; split it into separate
  tests. A branch that never runs hides its assertions.
