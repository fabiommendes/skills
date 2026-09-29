---
name: clean-code
description: Broad-stroke code quality heuristics — naming, function size, comments, error handling, class responsibility, boundaries, tests, and simple design. Use when writing new code, refactoring, or reviewing a diff for readability and structure.
---

# Clean Code

These are defaults for judgment, not rules to enforce mechanically. Specific
codebase conventions overrule these heuristics — see "Where this is contested"
before applying.

The governing principle: code is read far more often than it is written, so
optimize for the reader. Every heuristic below is downstream of that.

## Names

Names reflect design. If naming a thing is hard, the design is probably wrong.

- Names reveal intent: why it exists, what it does, how it's used. Knowing the
  name + type should make the purpose and usage of the entity immediately clear.
- One word per concept across the codebase. Don't mix `fetch`, `get`, and
  `retrieve` for the same operation, or reuse one verb for different operations.
- Length tracks scope. A loop index can be `i`; a module-level export cannot.
- Classes are noun phrases, functions that cause side effects are verb phrases.
  Pure functions can be either way.
- No type or scope encoding in the name, no cute names, no noise words
  (`Data`, `Info`, `Manager`, `Processor`) that distinguish nothing.
- Replace magic numbers and bare literals with named constants.

## Module layout

- Keep related functionality together.
- If a module gets too big, consider breaking it into smaller helper modules.
- The module should read top-down: the most important definitions go first
  (usually types) and follow in order of decreasing importance and likelihood
  they will be consumed from the outside. This rule also applies to methods in a
  class layout.

## Functions

- Do one thing per function.
  - Pure functions always do one thing.
  - Keep effectful functions isolated (a single effect) and focused.
- Do not mix levels of abstraction.
- Flat and small. Deep nesting is the signal to extract.
- If the language supports it, nested functions are useful to encapsulate helper
  logic. Do not consider the nested function when evaluating the size of the
  outer function. This is only relevant for large complex functions.
- Fewer arguments is better; three is the practical ceiling. If the function
  receives many options, wrap them in a configuration object.
- Avoid unamed boolean arguments: it should be clear from reading the call site
  if `true` activate or disable the feature. When the boolean can be omitted,
  the default value should be `false`.
- No output arguments. Mutate the owning object or return a value.
- Command or query, never both: a function either changes state or answers a
  question.
- Extract duplication into abstraction.
  - Small levels of duplication are acceptable; extract when it introduces an
    useful and understandable abstraction.
- Do not over abstract. Use the same rule for comments: `isEven(x)` is a bad
  abstraction for `x % 2 === 0` for the same reason we would not put a comment.
  It is ok to leak low level for trivial logic.


## Comments

Treat every comment as a small failure to express something in code.

- Delete: restatements of the code, types, commented-out code, attributions, etc.
- Keep: intent behind a non-obvious decision, warnings about consequences, legal
  headers, TODOs, and clarification of something you genuinely cannot change.
- A wrong comment is worse than none. Comments rot; code doesn't lie.

Documentation comments (or documentation strings) are an exception: public APIs
should be documented. It is ok to document private APIs, but keep details 
to a minimum.

## Error handling

The result pattern forces handling unhappy outcomes, exceptions let them
propagate. Design around this principle: each have their own trade-offs and put
different obligations on the caller. A code base can mix both styles if each is
used consistently in its appropriate context.

- Exceptions are for exceptional conditions, not for regular control flow.
- Prefer result types (e.g., `Result<T, E>`, `Optional<T>` or similar) for
  expected branching from the happy path.
- Carry context: exceptions and results should provide information about the
  operation attempted and why it failed. Avoid bare message strings as the only
  source of context.
- Optional types over collections and strings require extra thought: is there a
  semantic difference between `null` and the empty object? If not, drop the
  nullable, if true, document it.

## Classes and types

- Avoid concrete inheritance: OO conflates types, interfaces, code reuse and
  taxonomies. Only the later requires concrete inheritance and is usually
  brittle unnecessary abstraction.
- Classes can represent types, closures, shared behavior for an interface or an
  hierarchy. Do not mix roles.
- 


- One reason to change (Single Responsibility Principle). A class you can only
  describe with "and" is two classes.
- Small, with few instance variables, and cohesive: most methods should touch
  most of the state. Falling cohesion is the cue to split.
- Decide whether a thing is an **object** (hides data, exposes behavior) or a
  **data structure** (exposes data, no behavior) and commit. Half-objects that
  are getter/setter bags over private fields hide nothing.
- Law of Demeter: talk to your immediate collaborators, not to what they return.
  Long `a.getB().getC().doSomething()` chains couple you to a structure you
  don't own.
- Depend on abstractions; keep construction (wiring, factories, injection)
  separate from runtime logic.

## Boundaries

- Wrap third-party APIs in an interface shaped to your needs. Don't let external
  types spread through your code — the wrapper is where you absorb their churn.
- Write learning tests against unfamiliar libraries: they teach you the API and
  then catch breaking changes on upgrade.

## Tests

- Prefer static guarantees over tests. Do not write tests for things the type system can enforce.
- Keep tests readable above all else.
- One concept per test. Test names state what behavior is being verified.
- Fast, Independent (no ordering dependencies), Repeatable (any
  environment), Self-validating (pass/fail, not output to inspect), Timely
  (written alongside the code, not months later).
- Test boundary conditions explicitly; that's where the bugs are.
- Test complex logic, business rules, user actions. Do not test trivial implementation details.
- Test is code: keep good practices, refactor and remove it if it does not add value. 
- Test must verify a contract of your code: do not write just to increase coverage.

## Simple design

The design is good enough when, in this priority order, it:

1. Passes all its tests.
2. Contains no duplication.
3. Expresses the author's intent.
4. Uses no more classes and methods than it needs.

Rules 2 and 3 are refactoring targets you apply continuously; rule 4 is the
brake on over-abstraction the earlier rules can produce.

**Boy Scout Rule:** leave each file you touch slightly cleaner than you found
it. Incremental, in the course of other work — not a separate cleanup project.

## Where this is contested

Apply these with a caveat; reasonable practitioners reject them outright:

- **Function size taken to extremes.** Decomposing into many two-line functions
  can scatter a single coherent operation across a file and make it harder to
  follow, not easier. This is specially true in functions that codify a long
  linear chain of operations: write helper functions only to keep the
  abstraction level consistent. Otherwise divide each step with comments rather
  than extracting a new function.
- **"Comments are failures."** Explanatory comments about *why* — tradeoffs,
  history, rejected alternatives — carry information no naming scheme can.
- **DRY above all.** Premature deduplication couples code that merely looks
  alike; some duplication is cheaper than the wrong abstraction.

When this skill conflicts with the project's own conventions or a
language-specific skill, the project wins.
