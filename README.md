# chips-skills

`chips-skill` is a very simple tool that helps managing your skills for coding
agents. It provides some pre-built skills, but you can also tweak them and add 
your own. It is mainly designed to be used with [Claude](https://claude.ai), but
it should probably work with other agents with minimum adjustments.


## Usage

Once installed, you will probably want to get a list of all skills available:

```bash
chips-skills list
```

Select anyone that looks interesting and install it in your project:

```bash
chips-skills add <skill_name> 
```

This will scan your current project and install the selected skills in the proper
folder (e.g., `.claude/skills` or `.codex/skills`).

The skills live in a global user repository under
`~/.local/share/skills/<category>/<skill>`. This tool pre-populates this folder with
some skills, but you can also add your own. For those who like CLI's,
`chips-skills` provides a command for that, `chips-skills new <category/skill>`,
but you can also just fire your prefered text editor at that folder and create
them manually.


## Installation

My preferred way is to use uv:

```bash
uv tool install chips-skills
```

(but of course you can adapt it to use pip, poetry, etc).


## Contributing

This is a young project, and contributions to the CLI tool are welcome. I am
very particular about the pre-shipped skills, though: I want to test them, and I
want them to reflect my coding standards, philosophy, and taste.