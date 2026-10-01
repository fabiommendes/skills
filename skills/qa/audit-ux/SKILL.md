---
name: audit-ux
description: Usability audit of an application's user flows using task walkthroughs and Nielsen's heuristics, covering task completion, feedback, error prevention and recovery, consistency, and help, delivered as a PDF/HTML report with ready-to-paste GitHub issues. Use when the user asks for a UX or usability audit, or wants to find where users get stuck, confused, or lose work.
---

# Audit: UX

Audit how well users can accomplish their tasks, and deliver the report
defined by the `audit-report` skill. This audit is about behavior and flow:
what the user must do, understand, and remember. Visual design and
accessibility belong to `audit-ui`.

Copy this checklist and track it:

```
- [ ] 1. Load audit-report
- [ ] 2. Set up the interface
- [ ] 3. Build the task inventory
- [ ] 4. Walk through every task
- [ ] 5. Check every heuristic
- [ ] 6. Write findings.json and render
```

## 1. Load audit-report

Invoke the `audit-report` skill now. It defines the findings file you fill in
as you go. The area is `ux`; the issue title prefix is `[UX]`.

## 2. Set up the interface

Ask the user how to run the application in a test environment, with test data,
and who its users are. Use the browser tools available (Claude in Chrome,
Playwright) for web interfaces, and the terminal for command-line tools. Work
only in the environment the user names.

If the interface cannot run, audit from the code (routes, components, copy,
validation) and say so in `methodology`. Mark each finding made from code
alone with "from code" in `conditions`.

Save screenshots of findings in `docs/audits/ux/screenshots/`.

## 3. Build the task inventory

List the tasks users come to do, from the navigation, routes, documentation,
and the user's description: sign up, create the main object, find something,
change settings, recover a password. Mark each as primary or secondary. Record
one row per task in `inventory`: task, primary or secondary, entry point,
number of steps, completed (yes, with workaround, no).

## 4. Walk through every task

Do each task as a first-time user would. At every step ask:

1. Will the user know what to do next to reach the goal?
2. Will they see the control that does it?
3. Will they understand that this control does what they want?
4. After acting, will they see that it worked?

A "no" to any question is a finding. Then repeat the task making typical
mistakes: invalid or empty input, going back, cancelling midway, reloading,
double-clicking submit, opening the same page in two tabs.

## 5. Categories

Map each finding to the category it violates. The first is about whole tasks;
the others are Nielsen's ten usability heuristics.

1. **Task completion (`tasks`):** dead ends, steps that need information from
   elsewhere, flows that lose the user's input, tasks that take far more steps
   than needed.
2. **Visibility of system status (`status`):** feedback after actions, progress
   for slow operations, the current location and state.
3. **Match with the real world (`language`):** the users' words instead of
   internal or technical terms, natural order of information.
4. **User control and freedom (`control`):** undo, cancel, going back without
   losing work, leaving unwanted states.
5. **Consistency and standards (`consistency`):** the same action named and
   placed the same way everywhere, platform conventions followed.
6. **Error prevention (`error-prevention`):** constraints and defaults that
   prevent mistakes, confirmation before destructive actions.
7. **Recognition rather than recall (`recognition`):** options and information
   visible when needed instead of memorized from a previous screen.
8. **Flexibility and efficiency (`efficiency`):** shortcuts, bulk actions, and
   remembered choices for frequent users.
9. **Focused content (`minimalism`):** each screen shows what the task needs;
   secondary information does not compete with it.
10. **Error recovery (`error-recovery`):** error messages in plain language
    that say what went wrong and how to fix it, with the user's input kept.
11. **Help and documentation (`help`):** help where the user needs it, task
    oriented and findable.

## Severity

| Level | Meaning |
|---|---|
| `critical` | The user cannot complete a primary task, or loses data or work. |
| `high` | A primary task succeeds only with a workaround or after significant confusion, or a secondary task cannot be completed. |
| `medium` | The user is noticeably slowed down or confused, or a minor problem recurs on many screens. |
| `low` | A minor or rare annoyance. |
| `info` | An observation or improvement idea with no current problem. |

## 6. Write findings.json and render

Fill `findings.json` as `audit-report` defines, with all eleven categories in
`categories`, and render it. For each finding, put the screen or route and the
steps to reproduce in `location` and `description`, the component's
`file:line` in `fix` when you found the cause in code, and the screenshot in
`screenshot`.
