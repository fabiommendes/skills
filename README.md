# chips-skills

A collection of skills and subagents for coding agents. It is mainly designed
to be used with [Claude](https://claude.ai), but it should probably work with
other agents with minimum adjustments.

For most users, install skills with [`npx skills`](https://github.com/vercel-labs/skills).
For example, to install skills globally:

```bash
npx skills add fabiommendes/skills --skill tdd --skill spec
```

If you're developing skills in a local clone and want changes to take effect
immediately, run:

```bash
./dev-install.sh
```

This links every skill into `~/.agents/skills/` and every agent into
`~/.claude/agents/`. It also removes broken skill links from
`~/.agents/skills/`.


## Skills

Skills live under `skills/<category>/<skill>`. Use `npx skills` to list or
selectively install them. Developers working from a local clone can use
`dev-install.sh` to link all skills directly from the checkout.

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
