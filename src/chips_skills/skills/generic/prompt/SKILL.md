---
name: prompt
description: Effective prompts workflow. Define more assertive jobs before firing the agent.
disable-model-invocation: true
argument-hint: "What should I do now?"
---

# Claude Prompting

This is a workflow that helps better prepare effective prompts when using Claude.

1. You produce template prompt file (which can be generic or based on the conversation context).
2. A human edit this file with the necessary details.
3. You or another agent use the updated prompt file to continue with the task.
 

## File location

The prompt file destination is chosen from one of the following options (in order). 

1. `prompts/<title>.md` if human provided some context. Title is a slug summarizing the human request. Do not overwrite any existing files.
2. A `prompt.md` file in the project root, if it does not exist.
3. If file exists, ask the human for context and apply the first rule.


## Template

The basic structure of a prompt file is as follows:

```md
<instructions>
  Describe the final outcome of what you want Claude to do.
</instructions>

<why>
  Explain the reasons for the job, since it helps guide reasoning and 
  decision-making for Claude.
</why>

<examples>
  Examples help guide desired behavior and expectations.

  Put each <example> tag under a <examples> block if there is more than one example.
</examples>

<document>
  If there are any relevant documents or references, include them here.

  Put each <document> tag under a <document> block if there is more than one document.
</document>

<strategy>
  Include any reasoning or thought process that Claude should follow.
</strategy>

<constraints>
  Specify any rules, constraints, or guidelines that Claude should follow during 
  the task. E.g, "only modify some specific file(s)". "do not change backend code".
</constraints>

<done_means>
  Tell the acceptance criteria for the task.
</done_means>
```

If human provided any context, you can replace the placeholder content text by
some single phrase sentences more relevant to the specific task in hand.

## What to report?

Once file is created, simply report the location like this:

```
Prompt file created at `<full_path_to_prompt_file>`.
```

The human will probably edit the prompt file with details. Display a
confirmation message asking if the human wants to continue with the task. If
re-read the file with the updated content and proceed as if it was the
first prompt given in the conversation.

When the task is done, confirm with the human if the `<prompt_file>` should be
deleted and remove it if the human confirms.