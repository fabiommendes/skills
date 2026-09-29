---
name: do
description: Run prompts created externally by the user.
disable-model-invocation: true
argument-hint: Path to the prompt file to execute.
---

# Do Skill

Users sometimes prefer to author complex prompts in a text editor before typing
them to the agent. This simple skill finds and executes those externally 
authored prompts.

## Prompt location

Search for a prompt file in this order:

1. The argument specified by the user when invoking the skill.
2. A `prompt.txt` or `prompt.md` file in the current working directory.
3. A file in a `prompts` directory within the current working directory. If
   there is more than one file, display a enumerated list of options and ask the
   human to select one.

If all those attempts fail, suggest human to use the `/prompt` skill to create 
a new prompt file and finish.

## Execution

Read the whole contents of the prompt file and confirm with the human. Human
already knows the contents of the prompt, so just give some keywords for
confirmation. Example: `Should I write the Login component?`

If the human confirms, proceed to execute the prompt as if the prompt had been
typed directly to the agent.
