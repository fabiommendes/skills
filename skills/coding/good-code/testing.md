# Tests

## Contents

- What to test
- Seams
- How to select the approach
- Assertion density
- Good tests
- Bad tests
- Mocking
- Determinism
- Test code

## What to test

- Tests are code, and code is debt. Decide carefully when and how to write them.
- Test contracts: complex logic, business rules, user actions. Do not test simple implementation details. Do not write tests only to increase the coverage.
- Test boundary conditions explicitly, because bugs occur there.
- Prefer static guarantees to tests. Do not test what the type system guarantees. For type-level code (generic helpers, conditional or mapped types), write type tests where the language permits (for example, `expectTypeOf` in TypeScript, `assert_type` in Python).
- To fix a bug, first write a test that reproduces it and fails for the reported reason. Then fix the bug. Give the test the name of the behavior that broke, not the issue number.

## Seams

A **seam** is the public boundary where you observe the behavior. Tests connect to seams, never to internal details.

Use the innermost seam that covers the behavior. For "the user can reset the password", these are possible seams:

- `POST /auth/reset`: the HTTP endpoint. A real request, slow.
- `resetPassword(email, clock, mailer)`: the service function. Fast.
- `TokenGenerator.create()`: internal. Do not test it, because a refactor breaks the test.

Test the service function. The endpoint must be a thin, general layer on top of it, with routing and serialization and no logic of its own. When the outer layer is thin, a test of the inner layer covers the behavior at a fraction of the cost.

This rule is a design rule as much as a test rule. When the only seam that covers a behavior is expensive (an HTTP round trip, a browser, a real database), the logic is usually in the outer layer. Move the logic to an inner abstraction and test it there.

Expensive tests still have a place, but use a small number of them, each with a wide scope. They only need to show that the outer layer connects correctly to the inner abstraction. One test that calls the endpoint and checks many properties has more value than ten tests that each pay the setup cost to check one property.

## How to select the approach

In order of preference:

**1. Property-based tests or fuzzing.** Best where invariants exist: round trip, idempotence, order, conservation. Write the generators, strategies, or factories one time and use them again in many tests. This reuse keeps the suite small.

**2. Example-based tests**, table-driven when possible: one test function on a table of input and expected output. Use this for pure functions without side effects. Use the parametrization of the framework (`pytest.mark.parametrize`, `test.each`), not a loop, so that the framework reports each case separately. Move the examples to fixture files when they become large.

For large structured output (rendered HTML, generated code, CLI output), it is not practical to write the expected value by hand. Use snapshot tests or golden-file tests. The golden file is the expected value: review each change in it as you review code. Never regenerate it only to make a test pass. Remove unstable parts (timestamps, ids, absolute paths). Keep snapshots small enough to read. A snapshot that nobody reads is a tautology.

**3. Imperative tests with mocks.** Use them only when the two previous approaches do not work. See [Mocking](#mocking).

Do not use two approaches for the same behavior. If a property covers a behavior, do not also write examples for it. The objective is the smallest set of tests that covers the scenarios.

## Assertion density

Decide by the runtime cost of the test.

**Cheap** (no fixture setup, no database, no network, no new process): one logical assertion in each test. A failure shows directly which behavior broke.

**Expensive** (database reset, external services, browser, large fixtures): put the assertions together. Run the happy path one time and check all the observable parts of the result. Separate tests multiply the setup cost and make the suite so slow that nobody runs it. That cost is larger than the precision that you lose.

Edge cases always stay in separate tests. They are usually cheap, and a combined edge-case test gives little information when it fails.

## Good tests

Tests check behavior through public interfaces. The code can change completely; the tests must not change. A good test reads like a specification.

```typescript
// GOOD: tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

- Tests behavior that is important to the caller
- Uses only the public API
- Stays correct after internal refactors
- Describes WHAT, not HOW

## Bad tests

**Connected to the implementation.** The test mocks internal collaborators, tests private methods, or checks the result through a side channel. The sign: the test breaks after a refactor, but the behavior did not change.

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

**Tautological.** The test calculates the expected value in the same way as the code. Thus the test always passes and never disagrees with the code.

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

Expected values come from an independent source of truth: a literal that is known to be correct, a worked example, or the specification.

Properties are not tautologies. `decode(encode(x)) === x` states a relation that the implementation must satisfy, and the relation can fail: it is an independent source of truth. A second run of the algorithm of the implementation to calculate the expected value is not.

## Mocking

Prefer real objects. Mock only at **system boundaries**:

- External APIs (payment, email)
- Databases (sometimes; prefer a test database)
- Time and randomness
- File system (sometimes; prefer temporary directories)

Do not mock your own classes and modules, internal collaborators, or anything that you control.

An injected boundary is a boundary that you can replace. Thus the injection rules in [SKILL.md](SKILL.md) make mocks easy. Design the injected interface with one function for each external operation, not one general fetcher:

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

Each mock returns one specific shape and needs no conditional logic. The mocks show which endpoints a test uses, and each endpoint keeps its type safety.

## Determinism

- Each test is independent: no shared mutable state, and no dependency on the order of the tests.
- Do not use the real clock, network, or randomness, unless the test is about them. Inject or simulate them. Set the seed of the generators when you need randomness.
- Never use `sleep` to wait for an event. Wait for the condition itself with a timeout, or control the clock. A test that passes only on a fast machine is flaky.

## Test code

- Tests are code. Keep them easy to read first. Refactor them, and delete them when they have no more value.
- Give each test the name of the behavior that it locks.
- Follow the existing suite: framework, layout, names, fixture style, and assertion style. Do not add a new test framework or helper library without approval.
- Use the fixtures, factories, and generators of the project before you write new ones. Make test data with builders or factories that set sensible defaults. Set only the fields that are relevant to the test, so that the test shows what is important.
- Do not use branches on the result to select the assertions. Write separate tests. A branch that never runs hides its assertions.
