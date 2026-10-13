---
name: good-code
description: |
  Language-agnostic code design and readability heuristics covering naming, comments and docstrings, module layout, type and data modeling, function design, error handling, classes, boundaries, and tests. Use when designing types or modules, refactoring, reviewing code or a diff for quality, or when the user asks about naming, structure, or code smells.
---

# Good Code

Optimize for the reader. Here are some heuristics to guide you.

Apply them to the code you are writing or changing. If you notice problems in
surrounding code, do not fix or list them one by one: mention briefly that there
are some style issues and ask whether to fix them.

Writing or reviewing tests? Read [testing.md](testing.md).


## Names

Names reflect design. If naming a thing is hard or convoluted, the design is
probably wrong.

- Names reveal intent: why it exists, what it does, how it's used. Knowing the
  name and type should make the purpose and usage of the entity immediately
  clear.
- One word per concept across the codebase. Don't mix `fetch`, `get`, and
  `retrieve` for the same operation, or reuse one verb for different operations.
  Check if the project defines a glossary of key terms and concepts, and use
  them consistently.
- Length tracks scope. A loop index can be `i`; a module-level export cannot.
- One-letter names are acceptable when they map to established mathematical
  conventions (i, j, k for indices, x, y, z for coordinates, etc.). They are for
  mathematical abstractions and never refer to domain objects. E.g., `x`/`xs`
  are ok for a generic function over a collection, but a callback that expects a
  specific User type should use `user` rather than `u`.
- Classes and types are noun phrases; functions that cause side effects are verb
  phrases. Pure functions may be nouns (`area`) or verbs (`computeArea`); pick
  one style per codebase.
- Avoid type or scope encoding in the name. No cute names, no noise words
  (`Data`, `Info`, `Manager`, `Processor`) that distinguish nothing.
- Replace literals that carry domain meaning (limits, timeouts, rates) with
  named constants.


## Comments

- DO NOT reference process documents (handoffs, plans, specs under review) in
  comments; they may not be available to future readers and become stale.
- Explain the reason behind a decision, not that someone made it (e.g., in a
  conversation). The comment should be self-contained, complete, and not rely on
  external context.

When you encounter a comment in code you are changing:

- **Delete**: wrong and misleading comments should be deleted immediately; they
  are actively harmful. Also remove comments that do not add value:
  restatements of the code or types, commented-out code, attributions, etc.
- **Keep**: intent behind a non-obvious decision, warnings about consequences,
  legal headers, clarification of something you genuinely cannot change,
  justifications for linter or type checker suppressions, safety checks, etc.
- **Refactor**: TODOs, FIXMEs, and comments that indicate technical debt. Fix
  them if the fix is trivial and local, move them to an issue if the fix is
  clear but not local, or leave them as they are if unclear.
- **Reword**: poorly phrased comments should be reworded to improve clarity and
  accuracy.

Documentation comments/docstrings:

- Public APIs should be documented. It is ok to document private APIs, but keep
  details to a minimum.
- The documentation comment/string and the documented code always form a
  paragraph: ensure there are blank lines separating it from other paragraphs
  at the same nesting level.
- Never use the block comment form (`/** ... */` or `""" ... """`) on a single
  line. Multiline comments always start with a single sentence that summarizes
  them. If further explanation is required, follow the summary sentence with
  additional details. For functions, this may include information about the
  parameters, return value, exceptions, and side effects.
- Do not document parameters or the return value when all of them are obvious
  from the function signature. If a single parameter needs clarification,
  explain it in a second paragraph. If two or more need it, document all of
  them, including the trivial ones.


## Module layout

- Keep related functionality together.
- The module should read top-down: the most important definitions go first
  (usually types), followed by the rest in order of decreasing importance and
  likelihood of being consumed from the outside. This rule also applies to
  methods in a class. In languages that require definition before use, if the
  core definition depends on too many prior definitions, move them to a helper
  module.
- If a module gets too big, consider breaking it into smaller helper modules.
- Modules are often organized as collections (a library of functions) or as
  functionality centered around a specific type. In the latter case, put that
  type at the top: emphasize it!
- If more than one type is the focus of the same module, consider breaking it
  into separate modules. Auxiliary types do not count.
- Think of how it would read as prose: sentences, paragraphs, sections,
  chapters. In code, we separate paragraphs with blank lines and sections with
  section comments, and each file corresponds to a chapter.


## Types

- Design around data. Functions come second.
- Types should be focused and composable. Composability often favors cohesion,
  reuse, and expressiveness.
- Compose beyond composition: inspect the domain and look for relationships that
  can be described as some sort of algebraic structure. How can we combine
  behaviors? Which pieces of data are naturally processed together? Which
  transformations are important? Can you identify a functional pattern like
  Functor (map/flatMap), Monoid (empty/combine), or Applicative (pure/<*>)? In
  languages that do not use functional nomenclature, apply the patterns without
  the names.
- Make invalid states unrepresentable: model your types to minimize the number
  of invalid states that can be represented. Ideally there should be none. A bug
  cannot happen if we cannot express it in code. Enum types, sealed classes,
  type unions, and similar constructs often help achieve this goal.
- Use data hiding if the previous approach fails or if the representation uses
  convoluted internal types. Simple types should either expose all fields or
  hide all of them. The latter is useful to implement the "Parse, don't
  validate" pattern.
- Prefer immutability. Make it the default and change only if there is a good
  reason for mutability. Marginal performance gains outside of hot loops are not
  a sufficient justification.
- If a type is too big, extract parts and use composition when they can be
  meaningfully separated and reused or tested independently.
- If a pattern recurs across types, extract it into a generic type abstraction
  and define generics, interfaces, or protocols depending on the language and
  context.
- Use type aliases and type-level programming freely to improve readability.
  - Primitive types should usually be aliased to signal intent (e.g., `UserId`
    instead of `String`). This also opens the door to future hardening into
    new/branded types.
  - Treat type-level operations as functional code: composable, reusable,
    focused, documented. If the language allows, write type-level tests to
    ensure correctness.


## Functions

- Keep functions focused: do one thing, at a single level of abstraction. Pure
  functions always do one thing; effectful functions should perform a single
  effect.
- When designing a collection of functions or methods, design for composability.
  Extract the minimal set of primitives that cover all desired behaviors and
  expose them as the public API.
- Flat and small. Deep nesting is the signal to extract, possibly to a nested
  function if the language supports it. For large, complex functions, nested
  helpers do not count toward the size of the outer function.
- Fewer arguments are better; three is the practical ceiling. If the function
  receives many options, wrap them in a configuration object (or use
  keyword-only arguments in Python).
- Avoid unnamed boolean arguments: at the call site, it is unclear whether
  `true` enables or disables the feature. Name flags so the default reads
  naturally (`cache=True` rather than `no_cache=False`). If both read naturally, prefer consider extracting as an enum.
- No output arguments. Mutate the owning object or return a value.
- Prefer separating commands from queries: a function either changes state or
  answers a question. Atomic or idiomatic exceptions (`pop`, compare-and-swap)
  are fine.
- Small amounts of duplication are acceptable; extract when it introduces a
  useful and understandable abstraction. If you find it hard to name the
  abstraction, it might not be worth extracting.
- Do not over-abstract. Apply the same rule as for comments: `isEven(x)` is a bad
  abstraction for `x % 2 === 0` for the same reason we would not write a comment
  explaining this trivial piece of code. It is ok to leak low-level details for
  trivial logic.
- If the function is too long or complex, consider extracting the internals into
  a private class. The instance works like a closure that allows inspection of
  intermediate steps of execution.


## Error handling

The two most common approaches to error handling are the result/optional pattern
and exceptions. Results force the caller to handle unhappy outcomes; exceptions
let them propagate. Each places different obligations on the caller. A codebase
can mix both styles if each is used consistently in a predictable manner, but do
not mix them haphazardly.

- Prefer exceptions for exceptional conditions (broken invariants, unexpected
  states, unavailable resources, etc.), not for regular control flow.
- Prefer result types (e.g., `Result<T, E>`, `Optional<T>`, or similar) for
  expected branching from the happy path.
- However, language conventions take precedence (e.g., Python collections raise
  `KeyError` and `IndexError` instead of returning optionals, so in Python we
  follow that).
- Carry context: exceptions and results should provide information about the
  operation attempted and why it failed. Avoid bare message strings as the only
  source of context. Use optionals when the context is trivial and there is a
  single obvious reason for failure.
- Optional types over collections and strings require extra thought: is there a
  semantic difference between `null` and the empty value? If not, drop the
  nullable; if there is, clearly document what the difference means.


## Classes

- Classes are one way to define types in object-oriented languages. Do not bring
  in OO concepts just because the type was declared as a class. Avoid gratuitous
  hierarchies, data hiding, state, and variance considerations.
- Avoid concrete inheritance: OO conflates types, interfaces, code reuse, and
  taxonomies. Only the latter requires concrete inheritance. Use it when the
  domain has a genuine, stable taxonomy; otherwise it is usually a brittle and
  unnecessary abstraction.
- Classes can represent many things: types, hierarchies, closures, shared
  behavior for an interface, or an abstract base class. Do not mix roles.
- Depend on interfaces at boundaries or where more than one implementation
  exists. Keep construction (wiring, factories, injection) separate from runtime
  logic.


## Boundaries

- Wrap non-core third-party APIs in an interface shaped to your needs. Don't let
  external types spread through your code: the wrapper is where you absorb
  their churn.
- Apply a similar rule to transport and persistence layers (APIs, databases):
  design the core types first, derive a DTO for each boundary from them, and
  don't let DTOs spread to the core of your application.
- If you use a framework or library that is core to your application, adopt its
  conventions and nomenclature.


## Refactoring and evolution

When refactoring, fixing bugs, or tweaking:

- Breaking public APIs in library code is expensive. Prefer additive changes and
  deprecations.
- Breaking private or internal APIs in typed codebases can be cheap. If the
  blast radius is small, you can refactor aggressively. Large blast radii
  require planning, but the refactor might still be worth it.


## Simple design

The design is good enough when, in this priority order, it:

1. Passes all its tests.
2. Expresses the author's intent.
3. Uses no more code than it needs.

**Boy Scout Rule:** leave the code you change slightly cleaner than you found
it. Do it incrementally, in the course of other work, not as a separate cleanup
project.
