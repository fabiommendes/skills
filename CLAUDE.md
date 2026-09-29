This project is a collection of skills and subagents for AI coding agents.

- `skills/<category>/<skill>/SKILL.md`: skills, installed with `npx skills add`.
  `skills-lock.json` is the `npx skills` lock file.
- `agents/<name>/AGENT.md`: subagents, installed by symlinking each directory
  into `~/.claude/agents/`.
- `install.sh`: installs every skill and agent for the current user. Run it
  after changing a skill; agents are symlinks and need no reinstall.

Never add new skills or agents unless explicitly asked.
