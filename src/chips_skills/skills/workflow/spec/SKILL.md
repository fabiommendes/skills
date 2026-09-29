---
name: spec
description: Write a spec with numbered requirements and acceptance criteria. Use when the user wants to specify a feature, write a spec or PRD, or turn a request or issue into requirements.
argument-hint: "[interactive|headless]"
---

# Spec

A spec states what the software does as seen from outside: by a user, a
caller, or another system. It is the source of truth for everyone downstream:
the architect designs from it, the tester writes tests from it, the implementer
builds against it, and the reviewer judges against it. None of them can ask the
requester what they meant, so the spec has to answer it.

The spec covers _what_. The _how_ — modules, internal APIs, data structures —
belongs to the design.

## Modes

- `interactive` (default): you talk with the human who wants the change.
- `headless`: no human is available, as when you run as the `analyst` agent.
  Your questions go to the orchestrator.

Take the mode from the argument. With no argument, use `interactive`.

## 1. Understand

1. Read the project's `CLAUDE.md` or `AGENTS.md`. Follow them over your own defaults.
2. Read the request. Separate what is stated from what you are inferring.
3. Read the project's existing docs, glossary, and specs, if any. Reuse their
   terms; one concept gets one name.
4. Explore the code only to learn the current behavior the change touches: the
   commands, screens, endpoints, or functions a user already sees. Stop when you
   can describe that behavior.

## 2. Resolve ambiguities

List every ambiguity that would lead to materially different behavior. For
each one, write the options you see and the one you recommend.

- **interactive:** ask the human, a few questions at a time, the most
  consequential first. Offer the options and your recommendation; use a
  multiple-choice prompt when the options are discrete. Follow up when an
  answer opens a new branch. Done when no open question would change a
  requirement, or the human tells you to proceed.
- **headless:** send the whole list to the orchestrator in one batch before
  writing. If told to proceed without answers, use your recommended options.

Record every choice made without the requester's answer under "Assumptions".

## 3. Write

- Number every requirement: `R1`, `R2`, ... Downstream agents cite these IDs.
- One requirement states one observable behavior. Split any requirement that
  joins two behaviors with "and".
- Each requirement has acceptance criteria written as checkable examples:
  given a state and an input, the expected output, error, or side effect. Use
  concrete values.
- Cover the failure cases: invalid input, missing resources, permissions,
  conflicts. State the exact error the user sees when it matters.
- Cover the boundaries: empty, one, many, the maximum, and repeated operations.
- Name the user-facing interface when it is part of the request: command names,
  flags, URLs, fields, messages. Leave internal names to the design.
- Write "Out of scope" for behavior a reader might reasonably expect but that
  this change does not deliver.
- Write the smallest spec that delivers the request. Record ideas beyond it
  under "Possible follow-ups", not as requirements.

Use the project's spec template if one exists. Otherwise, use this structure:

```markdown
# <Feature name>

## Context
Why this change exists, in two or three sentences.

## Glossary
New or overloaded terms, one line each.

## Requirements
### R1: <short title>
<The behavior, in one or two sentences.>

Acceptance criteria:
- Given <state>, when <action>, then <result>.

## Out of scope
## Assumptions
## Open questions
## Possible follow-ups
```

Write the spec where the project keeps specs, or in the file the orchestrator
names. If there is neither, ask.

## 4. Check

Read the spec as the tester would: every requirement must be testable without
guessing. Read it as the implementer would: every requirement must be buildable
without asking. Fix what fails either reading.

- **interactive:** show the human the requirement titles, the out-of-scope list,
  and the assumptions. Revise until they approve.
- **headless:** finish with a short report: the spec path, the number of
  requirements, the assumptions, and the open questions with the requirements
  they block.
