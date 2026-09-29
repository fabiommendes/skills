---
name: skill-review
description: Reviews an Agent Skill against Anthropic's skill authoring best 
practices and reports concrete fixes. Use when the user asks to review, audit, 
or critique a skill, or a SKILL.md file.
disable-model-invocation: true
---

# Skill Review

Review a Skill (a `SKILL.md` plus any bundled files) and report what to fix.

Unless the user explicitly asks for fixes, the review is a reading task, not a
rewriting task. Do not edit the skill unless the user asks for fixes after
seeing the report.

## Workflow

This is the skill review checklist:

- Step 1: Locate the skill and list its files
- Step 2: Read SKILL.md and every bundled file
- Step 3: Score against the rubric
- Step 4: Draft three evaluation scenarios
- Step 5: Write the report
- Step 6: If user asks for fixes, confirm the changes with them before applying,
  otherwise ignore this step.

**Step 1: Locate the skill and list its files**

The target is a directory containing `SKILL.md`. If the user named a skill but
not a path, search the skill collection for a directory with that name. List the
whole tree — bundled files that nothing references are themselves a finding.

**Step 2: Read SKILL.md and every bundled file**

Read complete files, not previews. Note for each bundled file which line of
SKILL.md points at it.

**Step 3: Score against the rubric**

Work through [reference/checklist.md](reference/checklist.md) item by item. For
each item, record pass, fail, or not applicable, and for every fail quote the
offending line and state the replacement.

**Step 4: Draft evaluation scenarios**

If the frontmatter does not contain `disable-model-invocation: false`, consider
three concrete tasks a user might bring to this skill: one squarely in scope,
one at the edge of scope, and one that should *not* trigger the skill. For each,
judge from the `description` field alone whether the skill would trigger. A
near-miss on the in-scope or out-of-scope case is a description bug. Only report 
if the skill would trigger incorrectly, note it as a finding.

**Step 5: Write the report**

Use the report format below. Rank findings by impact: discovery problems
(`name`, `description`) first, then correctness, then structure, then polish.

## Report format

```markdown
# Review: <skill-name>

**Verdict:** ship as-is | fix before sharing | needs rework

## Blocking
- **<issue>** (`<file>:<line>`) — <what is wrong>. Fix: <specific replacement>

## Worth fixing
- ...

## Evaluation scenarios
1. In scope: "<task>" → triggers / misses
2. Edge: "<task>" → triggers / misses
3. Out of scope: "<task>" → correctly ignored / false trigger

## Checklist

```
<one line per rubric item: ✓ / ✗ / n/a. with a phrase only for items marked with an ✗>
```

Keep every finding actionable. "Description is vague" is not a finding; a
proposed replacement description is. Be specific and concise in the descriptions.

## Judgment calls

The rubric encodes defaults, not laws. Before reporting a violation, ask whether
the skill has a reason to break the rule:

- **Short skills.** A 30-line skill with no bundled files is fine. Do not demand
  progressive disclosure that nothing needs.
- **Degrees of freedom.** Terse, open-ended instructions are correct for tasks
  with many valid approaches; rigid step-by-step scripts are correct for fragile
  ones. Flag the mismatch, not the style.
- **Repo conventions.** If sibling skills share a frontmatter field or layout,
  treat that as the local convention rather than a defect.

Report at most one finding per underlying cause. A vague description and a
missing trigger term are one finding, not two.