# Writing rules for English skills

These rules adapt ASD-STE100 Simplified Technical English (Issue 8, 2021) to
skills and agent prompts. The specification is free from ASD
(<https://www.asd-ste100.org>), but it is copyrighted, so this file summarizes
its writing rules and does not copy its dictionary.

## Words

- Use one word for one meaning, and one meaning for one word. When a skill
  says "finding", it never says "issue" or "problem" for the same thing.
- Use the simplest common word. Write "use", not "utilize"; "start", not
  "initiate"; "show", not "demonstrate".
- Technical names are allowed: tool names, file names, code identifiers, terms
  from the project glossary. Put code and paths in backticks.
- Do not use a word as a different part of speech. "Test" is a noun or a verb;
  "a run" is a noun only when the skill defines it.
- Keep noun clusters to three words or fewer. Write "the timeout of the
  request handler", not "request handler timeout value".

## Verbs

- Use the active voice. Write "The agent reads the file", not "The file is
  read".
- Use the simple tenses: present, past, future. Avoid "-ing" forms, except in
  technical names.
- Use the imperative for instructions: "Read the file.", not "You should read
  the file." or "The file should be read."
- Do not hide the action in a noun. Write "check the config", not "perform a
  check of the config".

## Sentences

- Instructions: 20 words or fewer per sentence. One instruction per sentence,
  unless two actions happen at the same time.
- Descriptions: 25 words or fewer per sentence. One topic per sentence.
- Paragraphs: 6 sentences or fewer, one topic per paragraph.
- Put the condition first: "If the test fails, stop.", not "Stop if the test
  fails."
- Put a warning before the instruction it applies to, never after.
- Use "do not" for prohibitions. Say what to do instead when it is not obvious.

## Structure

- Use numbered steps for procedures and bullets for unordered items.
- Use tables for data with more than two attributes.
- Use a vertical list instead of a long sentence with many commas.

## Not covered by STE

These rules come from skill authoring, not from STE:

- Write for an agent that knows the domain. Do not explain common knowledge.
- Give the reason for a rule when the reason changes how the agent applies it.
- Use examples to show a pattern, and say which part of the example matters.
