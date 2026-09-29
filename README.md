# chips-skills

A collection of skills and subagents for coding agents. It is mainly designed
to be used with [Claude](https://claude.ai), but it should probably work with
other agents with minimum adjustments.

To install every skill and agent from a local clone, for the current user and
Claude Code:

```bash
./install.sh
```

Skills are copied, so run it again after changing a skill. Agents are
symlinked, so changes to them take effect immediately.


## Skills

Skills live under `skills/<category>/<skill>`. Install them with
[`npx skills`](https://github.com/vercel-labs/skills).

List the skills available in this repository:

```bash
npx skills add fabiommendes/skills --list
```

Install one or more skills in your project, or globally with `-g`:

```bash
npx skills add fabiommendes/skills --skill tdd --skill spec
```

Keep them up to date with `npx skills update`.


## Agents

Subagents live under `agents/<name>/AGENT.md`. Together they form a software
team that the `factory` skill orchestrates:

| Agent | Role |
|---|---|
| `analyst` | Turns a written request into a spec. |
| `architect` | Designs the public API and writes the stubs. |
| `tester` | Writes tests from the spec, blind to the implementation. |
| `implementer` | Implements the spec, blind to the test code. |
| `reviewer` | Reviews tests and implementation against the spec. |
| `security-reviewer` | Reviews a change for security flaws. |
| `breaker` | Attacks business rules and design with counterexamples. |
| `user` | Uses the software as a black box and reports what breaks. |
| `investigator` | Reproduces and diagnoses bugs, without fixing them. |
| `documenter` | Writes user-facing docs from the spec and the interface. |
| `text-reviewer` | Fixes and tightens prose in comments and docs. |
| `grader` | Helps a teacher classify and grade student submissions. |

To install a single agent for Claude Code, link its directory into
`~/.claude/agents/`:

```bash
ln -s "$PWD/agents/reviewer" ~/.claude/agents/reviewer
```


## Contributing

I am very particular about these skills: I want to test them, and I want them
to reflect my coding standards, philosophy, and taste.


## References

I collected some skills from other sources. Some skills are included verbatim
and others with small modifications.
