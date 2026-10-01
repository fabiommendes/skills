# References

Sources behind the `research-paper` skill. This file is for human readers; the
skill does not load it.

## Sources

- Simon Peyton Jones. _How to write a great research paper: seven simple
  suggestions_. Talk and slides, Microsoft Research.
  <https://simon.peytonjones.org/great-research-paper/>,
  slides: <https://www.microsoft.com/en-us/research/wp-content/uploads/2014/02/simon-peyton-jones_paper.pdf>.
  Primary source. The seven suggestions: don't wait, write; identify your key
  idea; tell a story; nail your contributions; related work later; put your
  readers first; listen to your readers. The four-sentence abstract comes from
  Kent Beck, via these slides.
- Jennifer Widom. _Tips for Writing Technical Papers_. Stanford InfoLab, 2006,
  revised 2009. <https://cs.stanford.edu/people/widom/paper-writing.html>.
  The five questions of the introduction, contribution by page 3, running
  examples, definitions before use.
- Brett Mensh and Konrad Kording. _Ten simple rules for structuring papers_.
  PLOS Computational Biology 13(9): e1005619, 2017.
  <https://doi.org/10.1371/journal.pcbi.1005619>.
  One central contribution, context-content-conclusion at every scale,
  one-sentence-per-paragraph outlines, feedback as iteration.
- George D. Gopen and Judith A. Swan. _The Science of Scientific Writing_.
  American Scientist 78, 1990.
  <https://www.gatsby.ucl.ac.uk/~pel/misc/gopen_swan.pdf>.
  Reader expectations: topic and stress positions, old before new information,
  subject close to verb, action in the verb.
- Zachary C. Lipton. _Heuristics for Scientific Writing (a Machine Learning
  Perspective)_. Approximately Correct, 2018.
  <https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/>.
  Delete generic openings, don't tease the reader, cut intensifiers, defensible
  claims, cite throughout.
- George M. Whitesides. _Whitesides' Group: Writing a Paper_. Advanced
  Materials 16(15): 1375–1377, 2004.
  <https://doi.org/10.1002/adma.200400767>.
  Outline the paper at the start of the research and rework it as the research
  evolves; build the outline around figures, tables, and schemes.

## Where the sources disagree

The skill takes Peyton Jones's side in each case, with the exceptions noted.

- **Where related work goes.** Peyton Jones puts it at the end, after the
  idea. Widom accepts either place: early when it is short or essential
  context, late when comparison needs the technical content. Widom's
  introduction also asks "why hasn't it been solved before?", which pulls some
  prior work forward, and Mensh and Kording frame the introduction around the
  gap in the literature. Many computer science venues habitually use section 2
  for it. Lipton adds that citations belong throughout the text, not only in
  one section. _Skill:_ end by default, cite at the point of use, move it
  earlier only when the problem cannot be understood without it.
- **The "rest of this paper" paragraph.** Peyton Jones rejects it in favour of
  forward references from the contributions. Widom's summary of contributions
  also points to sections, but many venues and advisors expect the roadmap
  paragraph. _Skill:_ forward references, no roadmap paragraph.
- **Passive voice.** Peyton Jones: "avoid it at all costs". Gopen and Swan
  argue that a rigid rule fails: the passive is the better sentence when it
  keeps the paragraph's subject in the topic position. Some fields still write
  methods sections in the passive by convention. _Skill:_ active by default,
  passive when it serves the topic position (this follows Gopen and Swan).
- **The abstract.** Peyton Jones (after Kent Beck): four sentences — problem,
  why interesting, what the solution achieves, what follows. Mensh and
  Kording: context and gap, then methods and key results, then conclusion and
  broader significance. Lipton: include the quantitative results. These are
  compatible in spirit; the skill uses the four sentences and adds numbers.
- **When to write.** Peyton Jones writes the paper before the research is done,
  to drive it. Whitesides agrees in substance: outline at the start of the
  project and rework the outline as the research evolves. The traditional
  model — research first, write last — has no advocate among these sources.
