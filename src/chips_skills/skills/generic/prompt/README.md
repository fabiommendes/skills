---
type: doc
status: active
tags: [prompt-engineering, claude, sonnet-5, opus-5, effort, adaptive-thinking, agentic-prompting]
relatedTo: [prompt]
---

# Create Effective Claude Prompts

This guide describes a workflow for creating effective prompts when using Claude.

## Best Practices

Summarized from the Anthropic docs, current as of 2026-09-20:

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)

## General principles

**Be clear and direct.** Claude does not know your norms. State the desired
output format and constraints explicitly, and use numbered steps when order or
completeness matters. If you want "above and beyond" work, ask for it: "Create
an analytics dashboard. Include as many relevant features and interactions as
possible. Go beyond the basics."

The golden rule: show the prompt to a colleague with no context. If they'd be
confused, so is Claude.

**Explain why.** 

**Use examples.** They should mirror the real use case, cover edge cases,
and vary enough that Claude doesn't latch onto an unintended pattern. Wrap them
in `<example>` / `<examples>` tags.

**Structure with XML tags.** `<instructions>`, `<context>`, `<input>`. Use
consistent tag names, and nest when the content has a hierarchy.

**Give a role** in the system prompt. One sentence changes the behavior and tone.

**Long context (20k+ tokens):** put the documents at the *top*, above the query,
instructions, and examples — queries at the end improved response quality by up
to 30% in tests. Wrap each document in `<document>` with `<source>` and
`<document_content>` subtags. For long-document tasks, ask Claude to quote the
relevant passages into `<quotes>` tags before doing the work.

## Output and formatting

Tell Claude what to do, not what to avoid. Instead of "do not use markdown",
say "compose your response of smoothly flowing prose paragraphs" — or use an XML
format indicator like `<smoothly_flowing_prose_paragraphs>`. The formatting
style of your prompt influences the output style, so a markdown-free prompt
tends to produce less markdown.

Latest models default to LaTeX for math. Ask for plain text explicitly if you
need it.

**Prefills are gone.** Starting with the 4.6 generation, a partial assistant
message on the last turn returns a 400 error. Replacements: structured outputs
or tool enums for format control; a direct "respond without preamble"
instruction for preamble stripping; moving continuations into the user turn
("Your previous response was interrupted and ended with `[...]`. Continue from
where you left off."); injecting reminders into the user turn or through tools
for context hydration.

## Thinking and effort

Adaptive thinking (`thinking: {type: "adaptive"}`) replaces manual extended
thinking. `budget_tokens` returns a 400 error on 4.7+ models; control depth with
the `effort` parameter (`low` / `medium` / `high` / `xhigh` / `max`) and use
`max_tokens` as the hard ceiling.

Defaults differ by model: on Opus 4.6–4.8 and Sonnet 4.6, omitting `thinking`
means thinking is off. **On Opus 5 and Sonnet 5, thinking is on by default.**

Adaptive-thinking triggering is promptable. To think less:

```text
Thinking adds latency and should only be used when it will meaningfully improve
answer quality - typically for problems that require multistep reasoning. When in
doubt, respond directly.
```

Prefer general instructions ("think thoroughly") over hand-written step-by-step
plans; Claude's own reasoning usually exceeds what a human prescribes. `<thinking>`
tags inside few-shot examples teach a reasoning pattern.

## Claude Sonnet 5

Existing Sonnet 4.6 prompts work well out of the box. What usually needs tuning:

**Response length.** Sonnet 5 calibrates length to task complexity rather than a
fixed verbosity — shorter on lookups, longer on open-ended analysis. If your
product depends on a style, tune it, preferring positive examples over "don't"
instructions:

```text
Provide concise, focused responses. Skip non-essential context, and keep examples minimal.
```

**Effort.** Defaults to `high`. Use `xhigh` for the hardest coding and agentic
work, `medium` for cost-sensitive paths, `low` only for short scoped or
latency-sensitive tasks. Rough migration mapping: Sonnet 5 at `medium` ≈ Sonnet
4.6 at `high`; Sonnet 5 at `high` ≈ Sonnet 4.6 at `max`. When benchmarking,
match by observed thinking length, not by effort name.

Sonnet 5 respects effort strictly at the low end — at `low` and `medium` it
scopes work to exactly what was asked, with some risk of under-thinking on
moderately complex tasks. If reasoning looks shallow, **raise effort rather than
prompting around it**.

**`max_tokens` needs headroom.** It caps thinking plus response text, so tight
budgets at `high`/`xhigh` can yield a response that is nearly all thinking
followed by a truncated answer with `stop_reason: "max_tokens"`. Sonnet 5 also
uses a new tokenizer producing roughly 30% more tokens for the same text, so
limits tuned for 4.6 may truncate.

**Sampling parameters are rejected.** Non-default `temperature`, `top_p`, or
`top_k` return a 400 error. Steer tone and variety through the system prompt
instead. Manual extended thinking is also removed (400).

**Tool use.** More agentic than 4.6; reaches for tools and self-verification
loops readily, and `high`/`xhigh` effort increases tool usage substantially.
With thinking *disabled* it is less likely to reach for tools — add an explicit
nudge if you depend on them.

**Progress updates.** Sonnet 5 gives regular, good updates during long agentic
traces on its own. Remove scaffolding like "after every 3 tool calls, summarize
progress."

**Literal instruction following.** It does not silently generalize an
instruction from one item to another, and does not infer requests you didn't
make. Good for structured extraction and tuned pipelines; when you want breadth,
state the scope ("Apply this formatting to every section, not just the first").

**Code review harnesses** tuned for older models may show lower recall — a
harness effect, not a capability regression. "Only report high-severity issues"
is now followed faithfully. Ask for coverage and filter in a separate pass:

```text
Report every issue you find, including ones you are uncertain about or consider
low-severity. Do not filter for importance or confidence at this stage - a separate
verification step will do that. For each finding, include your confidence level and
an estimated severity so a downstream filter can rank them.
```

**Frontend defaults.** Sonnet 5 settles into a consistent house style on
open-ended briefs, and vague redirection ("make it clean") just swaps one fixed
palette for another. Two things work: specify a concrete alternative (exact
palette hexes, typography, spacing, radii), or have the model propose options
first — "Before building, propose 4 distinct visual directions tailored to this
brief (each as: bg hex / accent hex / typeface, plus a one-line rationale). Ask
the user to pick one, then implement only that direction." With `temperature`
unavailable, the propose-first pattern is the recommended way to get variety
across runs.

**Interactive coding products.** Use `xhigh` or `high`, add an auto mode, and
reduce required user turns. Specify task, intent, and constraints fully in the
first turn — underspecified prompts spread over many turns cost more tokens and
sometimes perform worse.

## Claude Opus 5

Built for complex agentic coding and long-horizon work; performs well on
existing Opus 4.8 prompts. Its 1M-token context window is both default and
maximum, and instruction following holds throughout it.

**Verbosity is the big one.** Opus 5's user-facing responses run *longer* than
prior Opus models', and effort controls how much it thinks, not how much it
says. Lowering effort will not reliably shorten the visible answer — prompt for
brevity explicitly:

```text
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and
spend most of the response on the main answer. When asked to explain something, give
a high-level summary unless an in-depth explanation is specifically requested.
```

In a long system prompt, repeat a short reminder near the end
(`<tone_preference>Keep outputs reasonably concise.</tone_preference>`).

**Narration.** It announces what it is about to do, at length. Describe the
cadence you want instead: one sentence before the first tool call, brief updates
only on important findings or direction changes, and a closing message that
leads with the outcome.

**Written deliverables** (reports, Markdown files) are also longer. Add
"match the length of written documents to what the task needs; do not pad with
filler sections, redundant summaries, or boilerplate."

**Remove verification instructions.** Opus 5 verifies its own work unprompted.
Carried-over instructions like "include a final verification step" or "use a
subagent to verify" cause over-verification — deleting them saves tokens with no
quality loss. Same for "double-check your answer" style re-check prompts.

**Constrain scope.** Opus 5 can widen a task, adding steps that weren't
requested. For narrow work:

```text
Deliver what was asked, at the scope intended. Make routine judgment calls yourself,
and check in only when different readings of the request would lead to materially
different work. If the request seems mistaken or a better approach exists, say so in
a sentence and continue with the task as asked rather than quietly narrowing,
widening, or transforming it.
```

**Subagents.** Opus 5 delegates more readily than prior models. Coordination
quality is good (writer-verifier patterns work, agents rarely overwrite each
other), but delegation multiplies cost on small tasks:

```text
Delegate to a subagent only for large tasks that are genuinely independent and
parallelizable, such as a wide multi-file investigation. Do not delegate work you can
finish yourself in a handful of tool calls, and do not use subagents to verify or
double-check your own work. If one subagent can complete the task, use one rather
than several, and keep spawn counts low.
```

In Claude Code / the Agent SDK there are deterministic caps:
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`,
and the SDK's `max_budget_usd`.

**Correction narration.** Opus 5 narrates corrections to its own earlier
statements more than prior models. Limit it to corrections that change the
user's code, conclusions, or decisions.

**Effort.** `low` and `medium` give strong quality at a fraction of the tokens
and latency — use them as the primary cost/latency control, `xhigh` for
demanding agentic work. Re-run an effort sweep on your own evals rather than
inheriting a prior model's defaults.

**Thinking disabled is discouraged.** It can only be disabled at effort `high`
or below, and doing so produces two artifacts: tool calls written as visible
text instead of structured `tool_use` blocks (the call never runs, and in agent
loops the leaked text pollutes later turns), and internal `<thinking>`-style XML
tags leaking into the response. Thinking on at `low` effort generally beats
thinking off at similar cost. If you must disable it, remove any system-prompt
rule telling the model not to think (it increases tag leakage) and add:

```text
When you use a tool, you may say a brief sentence first. If no tool can express what
the user asked for, say so instead of guessing. Do not include internal or system XML
tags in your response.
```

**Code review.** High precision and recall, holding up at lower effort — enables
a fast pass at review time and a thorough one later. As with Sonnet 5, "be
conservative" is taken literally; ask for everything and filter separately.

## Agentic and tool-use patterns

**Say what you mean about action.** "Can you suggest some changes" gets
suggestions; "change this function to improve its performance" gets edits. To
make action the default, add a `<default_to_action>` block; to make research the
default, add a `<do_not_act_before_instructions>` block.

**Dial back aggressive language.** Prompts written to fight undertriggering on
older models ("CRITICAL: You MUST use this tool when...") now cause
overtriggering. Plain "Use this tool when..." is enough.

**Parallel tool calls** happen natively; an explicit
`<use_parallel_tool_calls>` block pushes the rate to near 100%. Include the
caveat about dependent calls and never guessing parameters.

**Long-horizon work across context windows:** use a different prompt for the
first window (set up tests and scripts), have the model track tests in a
structured file like `tests.json` and progress in freeform notes, use git as the
state log, and prefer starting a fresh context window over compaction — these
models are good at rediscovering state from the filesystem. Give explicit
restart instructions ("review progress.txt, tests.json, and the git logs").

**Autonomy and safety.** Without guidance, models may take hard-to-reverse
actions. Ask for confirmation on destructive operations, force-pushes, and
anything visible to others, and forbid destructive shortcuts like `--no-verify`.

**Overengineering.** Newer Opus models add unrequested files, abstractions, and
defensive code. A scope/documentation/defensive-coding/abstractions block keeps
solutions minimal.

**Test gaming.** Tell the model that tests verify correctness rather than define
the solution, forbid hardcoded values and helper-script workarounds, and invite
it to report that a task or test is wrong rather than working around it.

**Hallucination.** An `<investigate_before_answering>` block ("never speculate
about code you have not opened; if the user references a file, you MUST read it
before answering") keeps answers grounded.

**Temporary files.** Scratch files often improve agentic coding results; ask for
cleanup at the end of the task if you'd rather not keep them.

## Migration checklist

1. Be specific about desired behavior and add quality modifiers.
2. Request animations and interactive elements explicitly.
3. Move from `budget_tokens` to adaptive thinking plus `effort`.
4. Remove prefilled assistant messages on the final turn.
5. Dial back anti-laziness and tool-forcing language.
6. Keep conversation history append-only and pass thinking blocks back
   unchanged.
7. Re-check `max_tokens` — thinking is on by default on Opus 5 and Sonnet 5, and
   Sonnet 5's tokenizer emits ~30% more tokens for the same text.
8. Drop `temperature` / `top_p` / `top_k` for Sonnet 5 (400 error).