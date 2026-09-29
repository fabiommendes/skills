# Skill review rubric

Condensed from Anthropic's skill authoring best practices. Each item is a check
to run against the skill under review, with the failure signature to look for.

## Contents

- Frontmatter and discovery
- Conciseness
- Structure and progressive disclosure
- Workflows and feedback loops
- Content guidelines
- Scripts and executable code
- Evaluations

## Frontmatter and discovery

- **`name` is valid.** Lowercase letters, numbers, hyphens only; 64 characters
  max; no XML tags; must not contain the reserved words `anthropic` or `claude`.
- **`name` matches the directory.** A mismatch breaks loading.
- **`name` is descriptive.** Gerund (`processing-pdfs`) or noun phrase
  (`pdf-processing`) both work. Fail on `helper`, `utils`, `tools`, `data`,
  `files`.
- **`description` is non-empty and under 1,024 characters.**
- **`description` says what the skill does *and* when to use it.** One clause for
  the capability, one starting "Use when…" for the trigger.
- **`description` is third person.** Fail on "I can help you…" and "You can use
  this to…" — inconsistent point of view degrades discovery.
- **`description` carries the key terms a user would actually type.** File
  extensions, tool names, domain nouns. Fail on "Helps with documents."
- **No XML tags in `name` or `description`.**

## Conciseness

- **Every paragraph earns its tokens.** Cut anything explaining what a competent
  model already knows: what a PDF is, what a library is, what HTTP means.
- **No restating the request back to the model.** Instructions, not preamble.
- **No duplicated content** between SKILL.md and bundled files.

## Structure and progressive disclosure

- **SKILL.md body is under 500 lines.** Over the limit, content should move into
  bundled files.
- **References are one level deep.** SKILL.md may link to `reference/guide.md`;
  `reference/guide.md` must not push the reader on to a third file. Nested
  references get partially read.
- **Every bundled file is linked from SKILL.md.** An unreferenced file is dead
  weight — the model will never open it.
- **Bundled files are named for their content.** `form-validation-rules.md`, not
  `doc2.md`.
- **Reference files over 100 lines open with a table of contents**, so a partial
  read still reveals the full scope.
- **Splitting is by domain, not by size.** Separate files should map to separate
  situations so only the relevant one gets loaded.

## Workflows and feedback loops

- **Multistep procedures are numbered steps**, not prose.
- **Complex workflows provide a copyable checklist** the agent can track.
- **Steps state the action concretely** — the exact command, the exact file to
  edit — rather than describing the goal.
- **Quality-critical tasks have a validation loop:** produce → check → fix →
  recheck, with an explicit "only proceed when it passes."
- **Decision points are explicit.** "Creating new content? → creation workflow.
  Editing? → editing workflow."
- **Degrees of freedom match the task.** Fragile, order-dependent operations get
  exact commands; open-ended judgment tasks get direction and latitude. Flag
  either mismatch.

## Content guidelines

- **No time-sensitive information.** Fail on "before August 2025, use the old
  API." Deprecated material belongs in an "Old patterns" section, ideally inside
  a collapsed `<details>` block.
- **Terminology is consistent.** One term per concept throughout — not "field",
  "box", "element", and "control" for the same thing.
- **Examples are concrete.** Real input/output pairs beat descriptions of what
  good output looks like.
- **Output templates are present where format matters**, with the strictness
  stated ("use this exact structure" vs. "a sensible default").
- **One recommended approach, not a menu.** "Use pdfplumber" with a named escape
  hatch for the exception, not "you could use pypdf, or pdfplumber, or PyMuPDF."
- **MCP tools use fully qualified names** in `ServerName:tool_name` form.
- **Paths use forward slashes.** `scripts/helper.py`, never `scripts\helper.py`.

## Scripts and executable code

Skip this section for markdown-only skills.

- **Scripts solve, not defer.** They handle the error case themselves instead of
  failing and leaving the agent to work it out.
- **Error messages are actionable.** "Field 'signature_date' not found.
  Available fields: …" beats a bare traceback.
- **No voodoo constants.** Every tuned value carries a comment justifying it. If
  the author cannot explain the number, the agent cannot either.
- **Dependencies are stated** and available in the target runtime. Fail on "use
  the pdf library" with no install line.
- **Execution intent is unambiguous.** "Run `analyze_form.py`" (execute) versus
  "See `analyze_form.py` for the algorithm" (read). Ambiguity wastes context.
- **Deterministic work is a script**, not a prompt asking the agent to generate
  the same code each time.
- **Batch or destructive operations produce a verifiable intermediate artifact**
  — a plan file that a validator checks before anything is applied.

## Evaluations

- **At least three evaluation scenarios exist**, each naming the query, any input
  files, and the expected behavior.
- **Scenarios target real observed gaps**, not imagined ones.
- **The skill has been exercised on a real task**, not only read.
- **Behavior holds across the models it will run on.** Instructions tuned for a
  large model may under-specify for a small one.
