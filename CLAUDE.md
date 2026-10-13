This project is a collection of skills and subagents for AI coding agents.

- `pt-BR/<category>/<skill>/` and `pt-BR/agents/<name>/`: the source of every
  skill and agent, in Portuguese. `npx skills` does not search this directory,
  so it is not published.
- `skills/<category>/<skill>/SKILL.md`: the published English skills.
  `skills-lock.json` is the `npx skills` lock file.
- `agents/<name>/AGENT.md`: the published English subagents.
- `packages/<name>/`: Python packages the skills call through `uvx`, each kept
  in sync with its own repository by `git subtree`. Bump the version pinned in
  the skills when releasing one.
- `dev-install.sh [--lang pt|en]`: links every skill and agent into
  `~/.agents/skills/` and `~/.claude/agents/` for local development. `--lang`
  picks the version to link when both exist (default `pt`). Run it after you
  add a skill or agent.
- `check-translations.sh`: lists English skills and agents whose pt-BR source
  changed after the translation.

Never add new skills or agents unless explicitly asked.

## Language

Level 3 (general-use library), as defined in
`~/git/tools/tooling-root/dev/adr/0002-idioma-dos-repositorios.md`: everything
in English, except `pt-BR/` and issues. Talk to the human in Portuguese.

Translation workflow:

1. Edit the pt-BR source. Never edit an English skill that has
   `metadata.translatedFrom` by hand.
2. Commit the pt-BR change.
3. When the skill is mature, translate it to English under `skills/` and set
   `metadata.translatedFrom` to the commit from step 2.
4. `check-translations.sh` shows the stale translations and the `git diff` to
   apply.

English skills without `translatedFrom` are frozen older versions. Do not
update them; translate the pt-BR source when the skill is mature.

Do not rebase or squash commits on `main`: `translatedFrom` cites them.

Writing rules: `skills/generic/skill-review/reference/writing-en.md` for
English (ASD-STE100) and `escrita-pt-br.md` in the same directory for
Portuguese.

Validation fixtures, ground truth, and test methodology for the skills live in
the separate, private `skills-validation` repository
(<https://github.com/fabiommendes/skills-validation>, cloned at
`../skills-validation`).
