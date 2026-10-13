---
name: good-code
description: |
  Language-agnostic rules for code design and readability: names, comments and docstrings, module layout, types and data, functions, error handling, classes, boundaries, and tests. Use when you design types or modules, refactor, review code or a diff for quality, or when the user asks about names, structure, or code smells.
metadata:
  translatedFrom: 3df68456df25cbf8316c438f73c9734466fd59d5
---

# Good code

Write code for the reader. These rules guide the work.

Apply them to the code that you write or change. If you see problems in the code around it, do not fix or list each one. Tell the user that there are some style problems, and ask if they want a fix.

If the task is to write or review tests, read [testing.md](testing.md).


## Names

Names show the design. If it is difficult or confusing to find a name for a thing, the design is probably wrong.

- A name shows the intent: why the entity exists, what it does, and how to use it. The name and the type alone must make the purpose and the use clear.
- Use one word for each concept in the full codebase. Do not use `fetch`, `get`, and `retrieve` for the same operation. Do not use the same verb for different operations. If the project has a glossary of key terms and concepts, use its terms consistently.
- The length of a name follows its scope. A loop index can be `i`. A module-level export cannot.
- One-letter names are correct when they follow a known mathematical convention (i, j, k for indices; x, y, z for coordinates). Use them for mathematical abstractions only, never for domain objects. For example, `x` and `xs` are correct in a generic function on a collection. A callback that receives a `User` must use `user`, not `u`.
- Classes and types are noun phrases. Functions with side effects are verb phrases. Pure functions can be nouns (`area`) or verbs (`computeArea`). Use one style in each codebase.
- Do not put the type or the scope in the name. Do not use names that are too creative. Do not use general words (`Data`, `Info`, `Manager`, `Processor`) that do not identify anything.
- Replace literals that have a domain meaning (limits, timeouts, rates) with named constants.


## Comments

- Do NOT refer to process documents (handoffs, plans, specs in review) in comments. Future readers possibly cannot get them, and the comments become out of date.
- Give the reason for a decision, not the fact that someone made it (for example, in a chat). A comment must be complete and must not need external context.

When you find a comment in the code that you change:

- **Delete**: delete wrong or misleading comments immediately, because they cause damage. Also delete comments without value: comments that repeat the code or the types, commented-out code, author credits.
- **Keep**: the intent of a decision that is not obvious, warnings about consequences, legal headers, notes about something that you cannot change, the reason for a linter or type checker suppression, security checks.
- **Refactor**: TODOs, FIXMEs, and comments about technical debt. If the fix is simple and local, fix it. If the fix is clear but not local, move it to an issue. If the fix is not clear, keep the comment.
- **Rewrite**: rewrite unclear comments to make them clear and precise.

Doc comments and docstrings:

- Document public APIs. You can document private APIs, but keep the details to a minimum.
- A doc comment or docstring and the code that it documents are one paragraph. Put blank lines between this paragraph and other paragraphs at the same nesting level.
- Do not use the block form (`/** ... */` or `""" ... """`) on one line. A multi-line comment starts with one sentence that gives a summary. Put more details after the summary. For a function, the details can include the parameters, the return value, the exceptions, and the side effects.
- Do not document the parameters or the return value when the signature makes them obvious. If one parameter needs a note, explain it in a second paragraph. If two or more parameters need a note, document all of them, also the simple ones.


## Module layout

- Keep related functionality together.
- A reader reads the module from top to bottom. Put the most important definitions first (usually the types). Put the other definitions after them, in order of importance and of their use from outside the module. This rule also applies to the methods of a class. In languages that require a definition before its use, if the main definition needs many definitions before it, move them to a helper module.
- If a module becomes too large, divide it into smaller helper modules.
- A module is usually a collection (a library of functions) or the functionality of one type. In the second case, put that type at the top, where the reader sees it first.
- If a module has more than one main type, put each type in its own module. Helper types do not count.
- Read the module as prose: sentences, paragraphs, sections, chapters. In code, blank lines separate paragraphs and section comments separate sections. Each file is one chapter.


## Types

- Design the data first. Design the functions after the data.
- Make types small and composable. Composition usually gives cohesion, reuse, and clear code.
- Look for more than composition. Analyze the domain and find relations that an algebraic structure describes. How do behaviors combine? Which data do you process together? Which transformations are important? Do you see a functional pattern, such as Functor (map/flatMap), Monoid (empty/combine), or Applicative (pure/<*>)? In languages that do not use functional names, use the patterns without the names.
- Make invalid states impossible to represent. Design the types so that they can represent the minimum number of invalid states, ideally zero. If the code cannot express a bug, the bug cannot occur. Enumerated types, sealed classes, union types, and similar constructs help.
- Use data hiding if the previous approach fails, or if the representation uses complex internal types. A simple type shows all its fields or hides all its fields. Hide all fields to implement the "Parse, don't validate" pattern.
- Prefer immutable data. Use it as the default. Use mutable data only when you have a good reason. A small performance gain outside a frequent loop is not a sufficient reason.
- If a type becomes too large, extract parts of it and use composition. Do this when the parts are meaningful alone and you can reuse or test them separately.
- If a pattern repeats across types, extract it to a generic type abstraction. Define generics, interfaces, or protocols, as the language and the context permit.
- Use type aliases and type-level programming freely to make the code easier to read.
  - Usually, give a primitive type an alias that shows the intent (for example, `UserId`, not `String`). Later, you can make the alias stricter, for example a newtype or a branded type.
  - Treat type-level operations as functional code: composable, reusable, focused, and documented. If the language permits, write type-level tests to prove that they are correct.


## Functions

- Keep functions focused: one task, at one level of abstraction. A pure function always does one task. A function with effects does one effect.
- When you design a set of functions or methods, design them for composition. Find the minimum set of primitives that gives all the necessary behaviors, and make them the public API.
- Keep functions flat and short. Deep nesting tells you to extract code, possibly to a nested function if the language permits. In a large and complex function, nested helpers do not count in the length of the outer function.
- Use few arguments. Three is the practical maximum. If a function has many options, put them in a configuration object (or use keyword-only arguments in Python).
- Do not use boolean arguments without a name: at the call site, the reader does not know if `true` enables or disables the feature. Give flags names so that the default reads naturally (`cache=True`, not `no_cache=False`). If both values read well, use an enum.
- Do not use output arguments. Change the object that owns the data, or return a value.
- Keep commands and queries separate: a function changes the state or answers a question, not both. Atomic or idiomatic exceptions (`pop`, compare-and-swap) are correct.
- A small quantity of duplicate code is correct. Extract it when the result is a useful abstraction that is easy to understand. If it is difficult to find a name for the abstraction, possibly the extraction has no value.
- Do not add unnecessary abstractions. Use the same rule as for comments: `isEven(x)` is a bad abstraction for `x % 2 === 0`, for the same reason that we do not write a comment that explains this simple code. Low-level details in simple logic are correct.
- If a function is too long or too complex, move its internal steps to a private class. The instance is a closure that lets you inspect the intermediate steps.


## Error handling

The two usual approaches to errors are the result/optional pattern and exceptions. A result makes the caller handle the failure. An exception lets the error go up the call stack. Each approach gives the caller different obligations. A codebase can use both styles if it uses each one consistently and predictably. Do not mix them without a rule.

- Use exceptions for exceptional conditions (broken invariants, unexpected states, resources that are not available), not for the normal control flow.
- Use result types (for example `Result<T, E>`, `Optional<T>`, or similar) for expected failures.
- The conventions of the language have priority. For example, Python collections raise `KeyError` and `IndexError` and do not return optionals, so in Python, do the same.
- Include context: an exception or a result tells the operation that failed and why. Do not use a plain text message as the only context. Use optionals when the context is trivial and the failure has only one obvious cause.
- Optional collections and strings need more care. Is `null` different from the empty value? If not, remove the nullable type. If yes, document what the difference means.


## Classes

- In object-oriented languages, a class is one way to define a type. Do not add object-oriented concepts only because the type is a class. Do not add hierarchies, data hiding, state, or variance rules without a need.
- Do not use concrete inheritance. Object-oriented languages mix types, interfaces, code reuse, and taxonomies. Only taxonomies need concrete inheritance. Use it when the domain has a real and stable taxonomy. In other cases, it is usually a fragile and unnecessary abstraction.
- A class can be many things: a type, a hierarchy, a closure, the shared behavior of an interface, or an abstract base class. Give each class one role.
- Depend on interfaces at boundaries, or where more than one implementation exists. Keep construction (wiring, factories, injection) separate from the runtime logic.


## Boundaries

- Wrap third-party APIs that are not central to your code in an interface that fits your needs. Do not let external types spread through the code. The wrapper is the place where you absorb their changes.
- Apply a similar rule to the transport and persistence layers (APIs, databases). Design the core types first. Derive one DTO for each boundary from them. Do not let DTOs go into the core of the application.
- If you use a framework or a library that is central to the application, use its conventions and its names.


## Refactoring and change

When you refactor, fix bugs, or change code:

- A change that breaks the public API of a library is expensive. Prefer additions and deprecations.
- A change that breaks private or internal APIs in a typed codebase can be cheap. If the change affects a small area, you can refactor aggressively. A change that affects a large area needs a plan, but it can still be worth the cost.


## Simple design

The design is good enough when it does these things, in this order of priority:

1. It passes all its tests.
2. It shows the intent of the author.
3. It uses no more code than necessary.

**The Boy Scout rule:** leave the code that you change a bit cleaner than before. Do this in small steps, during other work, not as a separate cleanup project.
