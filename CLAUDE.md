This project is a collection of skills and subagents for AI coding agents.

- `skills/<category>/<skill>/SKILL.md`: skills, installed with `npx skills add`.
  `skills-lock.json` is the `npx skills` lock file.
- `agents/<name>/AGENT.md`: subagents, installed by symlinking each directory
  into `~/.claude/agents/`.
- `packages/<name>/`: Python packages the skills call through `uvx`, each kept
  in sync with its own repository by `git subtree`. Bump the version pinned in
  the skills when releasing one.
- `install.sh`: installs every skill and agent for the current user. Run it
  after changing a skill; agents are symlinks and need no reinstall.

Never add new skills or agents unless explicitly asked.

Validation fixtures, ground truth, and test methodology for the skills live in
the separate, private `skills-validation` repository
(<https://github.com/fabiommendes/skills-validation>, cloned at
`../skills-validation`).
