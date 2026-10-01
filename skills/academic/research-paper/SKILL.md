---
name: research-paper
description: Write, restructure, or review an academic research paper — its key idea, abstract, introduction, contributions, related work, and prose. Use when the user drafts or revises a paper, article, or thesis chapter, or asks for feedback on one.
---

# Research paper

A paper exists to convey one useful, reusable idea to its reader. Everything
below serves that goal. The approach follows Simon Peyton Jones's "How to write
a great research paper"; where other guides disagree with him, his position is
the default.

Write in the paper's language. The principles hold in any language.

## The key idea

A paper has one **ping**: one clear, sharp idea. Before drafting or reviewing
anything, state it in one or two sentences.

- If you cannot state it, that is the first problem. Ask the author.
- If there are several ideas, there are several papers. Say so.
- The paper states the idea explicitly: "The main idea of this paper is...".
  Never leave the reader to guess it.

## The story

Tell the story you would tell at a whiteboard: here is a problem; it is
interesting; it is unsolved; here is my idea; it works (details, evidence);
here is how it compares to other approaches.

Default outline for a conference paper, with page budgets:

| Part | Budget | Content |
|---|---|---|
| Title | | The idea, not the topic. |
| Abstract | 4 sentences | State the problem. Say why it is interesting. Say what the solution achieves. Say what follows from it. Give numbers when results are quantitative. |
| Introduction | 1 page | The problem, then the contributions. Nothing else. |
| The problem | 1 page | |
| The idea | 2 pages | |
| The details | 5 pages | Evidence for every contribution. |
| Related work | 1–2 pages | |
| Conclusions and further work | ½ page | |

Scale the budgets to the venue's page limit, and keep the order. In fields with
a mandatory structure, such as IMRaD, keep the required section names and tell
the same story inside them.

## Introduction

- Introduce the problem with a concrete **example**. Show a molehill, not a
  mountain: "Consider this program, which has an interesting bug" beats
  "Programs have bugs. Eliminating bugs is very important [1–5]." Cut every
  opening sentence that would fit any paper in the field.
- End it with the contributions as a **bulleted list**. Write this list first:
  it drives the whole paper, and the body exists to substantiate it.
- Every contribution is **refutable**: a claim that could turn out false. "We
  prove that type checking is decidable (Section 4)", not "We study its
  properties".
- Every contribution forward-references the section that holds its evidence.
  These forward references replace the "The rest of this paper is organized as
  follows" paragraph; leave that paragraph out.

## Evidence

Each claim in the introduction has evidence in the body: a theorem, a
measurement, a comparison, or a case study. Map claims to evidence. A claim
with no evidence gets evidence or gets cut; evidence no claim needs gets cut
or becomes a claim.

Claim what the evidence supports, and no more. Prefer "many" to "most" unless
you counted. Mark opinions as opinions.

## Related work

Put related work near the end, after the idea. Before the reader knows the
problem, compressed comparisons with other work are incomprehensible, and they
stand between the reader and the idea.

- Still cite at the point of use: when you adopt someone's definition,
  method, or result, cite it there.
- Be generous. Credit is not like money: giving it away does not reduce yours.
  Describe others' work so that its authors would agree with the description.
- Acknowledge the weaknesses of your own approach.

Move related work earlier only when the reader cannot understand the problem
without it, or the venue requires it. Tell the author why.

## Presenting the idea

- Intuition first, details second. A reader with the intuition can follow the
  details, and one who skips them still takes something away; the reverse does
  not work.
- Examples first, then the general case.
- Take the most direct route to the idea. Leave out the history of how you
  found it, however hard-won.
- Use a running example when the paper has several technical parts.
- Define every term and every piece of notation once, before its first use.
- Give the paper visual structure: sections, bullets, italics, laid-out code,
  figures. Figures carry the argument; each caption states the figure's point.

## Sentences

- Use the active voice. "We" is the authors, or the authors and the reader;
  "you" is the reader. "We ran 34 tests", not "34 tests were run".
- Choose each sentence's subject for the paragraph, not by rule: begin with the
  old information that links back to what came before, and end with the new
  information you want stressed. The passive voice is right when it keeps the
  paragraph's subject in front — "Pollen is dispersed by bees" in a paragraph
  about pollen. (Gopen and Swan)
- Keep the subject close to its verb. Put the action in the verb: "the
  collector was slow", not "the speed of storage reclamation left something to
  be desired".
- Use plain words: "find out", not "endeavour to ascertain".
- Cut intensifiers: "very", "extremely", "clearly", "novel".
- Build paragraphs as context, content, conclusion: the first sentence sets up
  the point and the last one lands it. (Mensh and Kording)

## Drafting

1. Write the key idea and the contributions list. Show them to the author and
   get agreement before writing more.
2. Outline the story in one sentence per paragraph.
3. Draft the body, then the introduction, then the abstract.
4. Review your own draft with the steps below.

Writing early exposes what is not yet understood. Mark missing results,
proofs, or data as `TODO` and list them for the author. Never invent results,
data, or citations; mark a needed citation as `[CITE: what it supports]`.

## Reviewing

Read as a first-time reader. "I got lost here" matters more than a typo.
Report findings in this order, each with its location, the problem, and a
suggested rewrite:

1. **Key idea:** can you state it? Does the paper state it explicitly?
2. **Contributions:** listed, refutable, forward-referenced, and each backed
   by evidence.
3. **Story:** where the reader gets lost; detours through the history of
   discovery; related work before the idea.
4. **Presentation:** general cases before examples; terms used before their
   definition.
5. **Sentences:** the rules above.
6. **Typos and mechanics:** grouped at the end.

Report without editing, unless the author asks for edits.

## Responding to reviewers

Read every criticism as a pointer to something the paper failed to explain.
Fix the paper so the point is clear even to a hasty reader, rather than
arguing in the response. Thank the reviewers.
