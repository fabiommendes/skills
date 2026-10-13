This project is a collection of skills and subagents for AI coding agents.

- `skills/<category>/<skill>/SKILL.md`: skills, linked into `~/.agents/skills/`
  by the developer-only `dev-install.sh`. `skills-lock.json` is the `npx skills`
  lock file.
- `agents/<name>/AGENT.md`: subagents, installed by symlinking each directory
  into `~/.claude/agents/`.
- `packages/<name>/`: Python packages the skills call through `uvx`, each kept
  in sync with its own repository by `git subtree`. Bump the version pinned in
  the skills when releasing one.
- `dev-install.sh`: links every skill and agent for local development. Run it
  when developing skills; links make changes take effect immediately.

Never add new skills or agents unless explicitly asked.

Validation fixtures, ground truth, and test methodology for the skills live in
the separate, private `skills-validation` repository
(<https://github.com/fabiommendes/skills-validation>, cloned at
`../skills-validation`).
