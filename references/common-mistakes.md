# Common mistakes

Read at the verify step, and whenever a check fails.


| Mistake | What to do instead |
|---|---|
| Covering every section of the paper and still missing what a reader asks | Ask from four lenses in the plan, then, at full review depth, run the grounded follow-up pass on each critical section (`references/reader-questions.md`); `check_questions.py` fails on an unplaced question or an answer not on its page |
| Dense math with no picture first, or a diagram with symbols, section labels or details the paper does not give | Open Part 1 with the overview diagram and each critical section with an intuition diagram, terms only, drawn from the paper (`references/layout.md`). `audit_links.py` and `diagram.py` fail on a missing, misplaced, labelled or unreadable one |
| Choosing the length yourself, or reusing an earlier guide's limits | Offer the computed options at intake and use the answer |
| Defining tokens, prompts, accuracy or gradient descent | Define only the paper's own concepts, metrics, math and datasets, plus the maths facts the derivations use above the reader's assumed maths, in the toolkit at the end of Part 1 |
| A result stated with no derivation, or derived in one compressed line ("the variances add, so by induction ...") | Derive it one move per line, naming each move and each toolkit fact; do the smallest case in full first (`references/writing.md`, Derivations) |
| A table of numbers that uses a formula the section has not shown yet | Climb the ladder in order: problem, answer, diagram, formula and derivation, meaning, then the numbers |
| A section with three or more "Why:" paragraphs and side checks, so its main result gets lost | Two "Why:" run-ins at most in the body; the other design choices and side checks go in one bulleted list after "Check yourself" |
| Choosing empirical mode because the paper reports benchmarks | Choose by the main contribution: a proposed mechanism takes method mode, with the benchmarks as its Evidence part |
| Citing "Table 1" or "Figure 4" as if the reader had the paper open, with no crop in the guide | Crop it and place it, with its caption and reading card, at the first place the guide cites it; link every later mention to it |
| Building a guide from a long session, so every call re-reads hundreds of thousands of tokens | Start in a fresh session, or hand steps 4 and 5 to one orchestrator agent at the plan gate (SKILL.md, workflow) |
| A part writer that rereads pages, reruns its ledger after every edit, or builds and audits the whole guide (60 to 100 calls) | About 20 tool calls per part: read once, write in one Write, run `check_part.py`, fix only what it reports |
| A glossary, an index or a figure appendix | Define at first use; show each figure once; the contents page is the only index. A short notation table of symbols in Part 1 is allowed |
| Dense math with no numbers to hold on to, or a standard method (an optimizer) used without being built up | Follow the intuition ladder in `references/writing.md`: problem, answer, diagram, formula and derivation, meaning, numbers, "Check yourself", figure, what the next section uses; carry one running example across the parts; give a process over time as a timeline with a toy run |
| Repeating a metric's math in a part and in the metric section | One home for each explanation; a pointer everywhere else |
| One example per task family | One real item per dataset, from the paper's prompt appendix when it has one |
| Listing every cited work | At most 10 key references, each read in the primary work |
| A page reference the reader can see: "[p. 2]" after a sentence, "(p. 5)", a page column in a table | Write the bracketed `[p. N]` marker in the source only. The build hides it from the HTML and PDF, and the checks still read it. `audit_links.py` fails on any page reference left visible |
| A page reference checked only by eye, or a link added late | `check_claims.py` and `audit_links.py` after the last edit |
| A clean-looking PDF that Chrome shrank | `build.py` fails when the title prints below true size |
| A heading on a reading card ("How to read this table") or a meta label ("In plain words", "Metric card:") | A card is a bullet list whose bullets open with bold labels, with no heading. `audit_links.py` fails on these labels |
| Self-labels and source tags such as "(my calculation from the fitted line, not a number in the paper)", "(my reading, not stated in the paper)", "(illustrative)", "(external: ...)" or "(standard)" | Show the arithmetic, as in "+2.04 BLEU (28.4 − 26.36)"; write "The paper does not say. One likely reason is ..."; open an example with "for example"; name a source in a plain sentence. `audit_links.py` fails on these labels |
| A cited work's page written as "(their p. 6)", or as a plain "(page 6)" with no link | Add the work to the config's `works` with the URL of the exact PDF read, and write `{key page 6}`: the build links it to that page. `audit_links.py` fails on "their p. N", "Section N (p. N)" and any "page N" that is not a link |
| A reference a reader would click left as plain text: a cited page, "Code 5", "Image 7", a key reference | The build links Part, Math, M, Code and Image references; write `{key page N}` for a cited page and `{key\|Name}` for a key reference. Run `audit_links.py` last: it fails on each one left unlinked |
| Restyling a finished guide by retyping its prose freely | Rewrite each part into `parts_v2/` with the brief in `references/rewrite.md`; promote it only after `check_rewrite.py` reports 0 FAIL and the user has compared the two PDFs |
| Saving the guide inside a code repository or beside unrelated files | `<output folder from the config>/<Paper-Title>/`, one folder per paper (`references/intake.md`, setup) |
