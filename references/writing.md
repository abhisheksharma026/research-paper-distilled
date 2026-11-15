# Writing the guide

## The reader

Write for the reader chosen at intake, at the maths level the intake table assumes for that reader. The guide itself never describes its reader, its maths level or its own method: it opens on the paper. For the default reader, a junior developer or junior AI engineer, explain the paper's own concepts, its metrics, its math and its datasets. Leave out definitions of tokens, prompts, parameters, benchmarks, accuracy, gradient descent and other ML basics.

- **A term the derivations depend on is defined by what it does, at first use,** even when the field takes it for granted: "a Markov chain: each step looks only at the step before it"; "the approximate posterior: the map from an image to its noisy versions".
- **The maths toolkit.** Part 1 ends with a short section titled "The maths this guide uses". It lists every maths fact that a derivation in the guide uses and that the reader's assumed maths does not cover, as "Fact A", "Fact B" and so on. Each fact has its name, its formula, one plain sentence on what it means, and an everyday instance where one helps ("a GPS fix and a step counter combine this way"). List only facts that a derivation uses, and use each one at least once. Typical facts: drawing a normal variable as mean plus standard deviation times noise; the sum of independent normal variables; combining two normal estimates of one quantity; the KL divergence between two normal distributions; the gradient of a log-density.
- **A derivation step that uses a toolkit fact names it:** "by Fact B, the two variances add".
- **A concept the paper's argument depends on gets a structural explainer, sized to the concept.** When the paper builds on a concept that the reader may not know and that the paper does not teach, explain it in the toolkit as one more fact. A concept with one idea takes two or three paragraphs. A concept with several parts that interact takes more, up to two pages (about 1,000 words) for that one concept. Two pages is a cap, not a target: stop when the reader can follow every later step that uses the concept. The plan gives each explainer its length, and Part 1's page budget includes it. Example: min max for a GAN, where the order of play explains both the equilibrium and mode collapse. Cover what the concept is, then why it behaves as it does (with a short derivation, every step shown), then how the paper uses it. Add whichever of these makes the concept easiest to follow: a tiny worked example with numbers, a small flowchart, or an equation broken down term by term. Point back to the explainer where the concept appears later.

## Style

- Follow `references/voice.md`: the order of every explanation, and the voice of each sentence.
- Short sentences in active voice, with common words. One idea per sentence. One name for one thing throughout.
- Each part opens with the one question it answers, in an italic line (`<p class="question">`).
- Mark each claim from the paper with its page marker, `[p. 12]` or `[pp. 3–4]`, right after the claim. The build hides every marker, so the reader sees no page references to the paper, while the checks still read each one in the HTML. Write a page of the paper only as a marker, never as visible text such as "(p. 5)" or "on page 5": `audit_links.py` fails on a page reference the reader can see. Show each derived number with its arithmetic, as in "+2.04 BLEU (28.4 − 26.36)", and state an untested explanation as untested ("the paper does not test this"). Use no self-labels, source tags or meta labels, in parentheses or anywhere else: not "(my calculation)", "(my calculation from the fitted line, not a number in the paper)", "(my reading, not stated in the paper)", "(illustrative)", "(external: ...)", "(standard)", "(the paper's)" or "in hindsight". Say the same thing as a plain sentence ("The paper does not say. One likely reason is ...") or show the arithmetic.
- Link every cited work you quote or cite by page. Add it to the build config's `works` as `"key": "URL"`, where the URL serves the exact PDF you read (compare checksums; for arXiv, name the version). Write `{key page 6}` or `{key pages 1 and 8}` for its pages, and `{key|Name, year}` for the work itself. Never write "p. 6" for a cited work: the build links every "p. N" to this paper.
- Name a code snippet as "Code 5" and a web article's image as "Image 7": the build links both to their place in the guide.
- Keep each claim beside its limit. Report the authors' conjectures as conjectures and their caveats in their words.
- Keep the source's qualifier: "in theory", "in practice", "some", "may", "on these tasks". The post says plain RNNs are "absolutely capable" in theory but do not learn long gaps in practice, so "plain RNNs fail" is wrong. `audit_links.py` lists absolute words beside a hedged source sentence for you to read.
- A condition stated as "only while", "as long as" or "is enough" names every condition. "A value lasts while the forget gate stays near 1" leaves out the second one: the added amount must also stay near 0.
- Later work goes in its own section of critical reading, with each work's year, and is checked in the cited paper.

## Building intuition

- **Each critical section climbs the same ladder:**
  1. The problem the section solves, in one or two sentences.
  2. The answer in one plain sentence.
  3. The intuition diagram.
  4. The formula, then its derivation (see "Derivations" under Math).
  5. What the result means, in one sentence: "Read it as: a weighted mix of the clean image and one draw of noise."
  6. The running example's numbers, as a table, a number line or a worked-example diagram. Each number comes from a formula the section has already shown.
  7. A "Check yourself" box with one question and its answer.
  8. The paper's figure.
  9. What the next section uses from this one, in one or two sentences: "The reverse process needs this jump twice: to build training inputs, and to estimate the clean image."
- **A critical section follows one thread: its main result.** Its body holds at most two **Why:** run-ins, one for the main result and one for its main design choice. Every other design choice goes in a bulleted list after the "Check yourself" box; each bullet opens with the choice in bold and gives its reason. A side check, such as the size of a bound or the error of an approximation, goes in that list as one bullet.
- **One running example travels across the parts.** Carry the same input from the first formula to the last consequence, so the reader follows one number through the whole mechanism.
- **Build up a standard method the argument depends on.** When the paper's reasoning turns on how an optimizer, a metric or a numeric format works, start from the simpler thing it extends, give its full update with every symbol, and work a table with the paper's settings.
- **Tell a process that unfolds over time as a timeline:** its phases in order, a toy run that prints them (a numbered Code snippet), and the paper's figure read phase by phase.
- **Part 1 may hold a short notation table:** each symbol, what it stands for, and where it first appears. It lists symbols, not terms, so it is not a glossary.

## The claim-evidence table

In Part 1, after the claim, give one row per main claim: the claim, the result that supports it, the direction and size of the effect, and the uncertainty or caveat, which ends with the claim's `[p. N]` marker. There is no page column, because the build hides the marker. Three to six rows. A claim with no supporting result is labelled as the authors' hypothesis.

## The "Why:" rule

Give every method, metric, baseline, dataset and design choice a bold "**Why:**" run-in. Say what problem the choice solves and what it gives up. Add a small worked example when the reason is quantitative. When the paper gives no reason, say so, and label a standard reason as standard.

## Reading cards

Each figure and table sits beside a card (see `assets/part_skeleton.html`). A card is a bullet list with no heading; each bullet opens with its bold label:

- **Graph:** the axes and their scale, each series, the reference lines, the pattern, the takeaway, the caution.
- **Table:** the rows and columns, the abbreviations and footnote letters, and which comparisons are fair.
- **Diagram:** the order to read it in, and the idea it shows.
- **Generated example:** which text is the prompt and which is the model's, and the claim it supports.

## Math

- **Mechanism math** (the model, compute, training, data processing, scaling fits) stays in its part as a numbered box: "Math 1", "Math 2". Say what the formula is for, give the formula and its derivation, name each symbol, work one example with real numbers, and give the "Why".
- **Metric math** goes only in the final section, as entries "M1", "M2", each with the formula, a worked example, the "Why" and the trap.
- One home for each explanation. Where a metric is already explained in a part, its final entry is a one-line pointer.
- A formula that holds only on one path, in one case or approximately says so in the formula itself, not only in the text: a subscript such as "direct", the sign "≈", or "(no bias)". Then name in one sentence what it leaves out. A displayed equality is read as exact.
- Write a rounded number with ≈. In a worked row whose inputs are rounded, say once that each result comes from the unrounded values, so the last digit can differ.
- Define each function in a worked example by its formula before its first number, so a reader can redo every number by hand: σ(a) = 1/(1 + e<sup>−a</sup>), so σ(2) = 0.881.
- Name each formula's source in plain words: its equation number, the work it comes from, or a sentence such as "The paper names no BLEU script". Recompute every worked number in the claims ledger.
- When `fetch_source.py` has the TeX, copy each equation from `equations.json` and each table cell from `tables.json` instead of retyping it. The ledger still checks the values against the PDF.

### Derivations

Derive every result that a later section builds on, whether the paper derives it, states it, or takes it from a cited work.

- **One move per line.** Each displayed line follows from the line above by one move. The sentence between the two lines names the move: substitute equation N, expand, apply Fact B, or simplify with an identity written out in that sentence.
- **No skipped middle steps.** Never jump from the starting expression to the result. Show each substitution, expansion, cancellation and rearrangement on its own line. This also covers a formula the guide states as a fact (a closed-form KL divergence, the derivative of the sigmoid, an inverse function), the arithmetic of a worked example, and a claim such as "so the radius never changes". Show where each one comes from, or work one case of it in full.
- **The smallest case in full, then the general case.** When the general result repeats one step, derive the smallest case in full (two steps, two terms). Then show the one line that carries any case to the next, and state the general result.
- **A route the toolkit supports.** When the paper's own route needs maths above the reader's level, take an equivalent route that the toolkit facts support, and say that it gives the paper's equation N. For example, combine two normal estimates (a toolkit fact) where the paper completes the square.
- **The result set apart, then read in words.** End the derivation on the result, displayed on its own line: later parts cite this form. Follow it with the "Read it as" sentence from the ladder.

## Reflection questions

End each part with two or three questions about a trade-off, an assumption, or what would change under other conditions, each with an answer that ends with its `[p. N]` marker. An answer that gives a number or a direction ("a larger gradient") is checked like any claim: in the ledger, or by a run. Avoid questions a reader answers by looking a fact up. Critical reading always asks what a re-implementation would need, and which detail the paper leaves out (the third pass of Keshav's "How to Read a Paper").
