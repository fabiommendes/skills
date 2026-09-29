# Tests

## Contents

- Where tests attach
- Assertion density
- Choosing an approach
- Good tests
- Bad tests

## Where tests attach

A **seam** is the public boundary you observe behavior at. Tests attach to
seams, never to internals.

Prefer the innermost seam that covers the behavior. For "user can reset their
password" the candidates might be:

- `POST /auth/reset` — the HTTP endpoint. Real request, slow.
- `resetPassword(email, clock, mailer)` — the service function. Fast.
- `TokenGenerator.create()` — internal. Do not test this; it breaks on refactor.

Test the service function. The endpoint should be a thin generic layer over it,
holding routing and serialization and no logic of its own. When the outer layer
is thin, testing the inner one covers the behavior at a fraction of the cost.

This is a design obligation as much as a testing one. When the only seam
covering a behavior is expensive — an HTTP round trip, a browser, a live
database — that usually means logic is stranded in the outer layer. Pull it into
an inner abstraction and test there.

Expensive tests still earn a place, but as a small number of broad ones: enough
to verify the bridge between the outer layer and the inner abstraction is wired
correctly. One test that exercises the endpoint and asserts many properties
beats ten that each pay the setup cost to assert one thing.

## Assertion density

Judge by what the test costs to run.

**Cheap** — no fixture setup, no database, no network, no process spawn: one
logical assertion per test. A failure then points straight at the behavior that
broke.

**Expensive** — database reinitialization, external services, browser, large
fixtures: bundle assertions. Drive the happy path once and assert everything
observable about the result. Splitting these into isolated tests multiplies the
setup cost and makes the suite slow enough that it stops being run, which costs
more than the lost precision.

Edge cases stay fine-grained either way. They are usually cheap, and a bundled
edge-case test tells you little when it fails.

## Choosing an approach

In order of preference:

**1. Property-based testing or fuzzing.** Best where invariants exist: round
trips, idempotence, ordering, conservation. Build the generators, strategies, or
factories once and reuse them across tests. That reuse is what keeps the suite
small.

**2. Example-based testing**, table-driven where it fits: one test function over
a table of input and expected output pairs. Use this for pure functions with no
side effects. Move examples into fixture files when they get bulky.

**3. Imperative tests with mocks.** Only when neither of the above works. See
[mocking.md](mocking.md).

Do not layer these. If a property covers a behavior, do not also write examples
for it. The goal is the smallest set of tests that covers the scenarios.

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
implementation must satisfy, and it can fail — that is an independent source of
truth. Re-running the implementation's own algorithm to produce the expected
value is not.

**Horizontal slicing.** Writing every test for a feature before any of its
implementation. Bulk tests verify imagined behavior: you test the shape of
things rather than what users actually need, and you commit to a test structure
before understanding the implementation. Batches of at most 3 acceptance
criteria are what keep this in check — each batch is small enough that its tests
can still respond to what the last batch taught you.
