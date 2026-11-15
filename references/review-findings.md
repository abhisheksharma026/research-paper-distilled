# Review findings

What independent reviews caught that the scripts did not. Each entry is a general rule, not the instance. The review prompt in `verification.md` asks the reviewer to check every class here and in the user's own file, `~/.config/research-paper-distilled/review-findings.md`, and a writer checks both before the review. A new rule goes in the user's own file, never in this one, so a shared copy of the skill carries no one's review history; merge a new rule into an old one when they share a cause.

## Math

- A displayed equality that holds only on one path, in one case or approximately must say so in the formula ("direct", "≈", "no bias"). A reader takes a displayed equality as exact.
- Every function in a worked example is defined by its formula before its first number, so each number can be redone by hand.
- A ratio, rate or "gap closed" needs a stated floor and denominator; give the chance level or the zero point it is measured from.
- A conversion between two conventions (a gate and one minus the gate, two bias forms) covers every term: weights and biases.
- A rounded number is written with ≈, and a worked row that uses rounded inputs says its result comes from the unrounded values. "5 × (−0.664 + 0.956) = 1.461" is false as written; the shown operands give 1.460.
- Every equation the text discusses by number is displayed, and equations that leave out terms (biases) say so beside them; the worked example states the value it uses for those terms.
- A toy example with sizes different from the paper says so and gives the paper's sizes.
- A value solved from an approximate balance keeps the ≈ and names its assumptions. When the exact solution is short, show it beside the approximation: |g| = ελ|θ|/(1 − λ|θ|), which the paper approximates as ελ|θ|.
- A statement about which values lie between two others is checked at its own endpoints. "Nothing can be stored between the fp32 neighbours of 1" forgets 1 itself.
- Every function or norm that a figure axis or a setting uses (a temperature, a max norm) is defined by its formula where it first appears.
- A steady-state formula is not the value right after a change. Say which one a worked number is, and use a run for the transient: Adam's steady step for a gradient is not its first step after that gradient returns.
- A chart that draws a negative quantity as positive labels its axis as a size, |x|.

## Claims

- Keep the source's qualifier ("in theory", "in practice", "some", "may"). Dropping it turns a hedged claim into a false one.
- A condition stated as enough ("only while", "as long as") lists every condition it needs.
- An interpretation the source does not state reads as the guide's, in a plain sentence ("The paper does not say. One likely reason is ..."), never as the source's.
- A comparison that changes two parts of a system measures the whole system. Name every difference between the compared systems before saying what a gap shows; a model that adds both a bidirectional encoder and attention does not isolate attention.
- One reported score does not show one run. Write "one reported score per model", not "one run".
- A claim about what a method cannot do names the condition: a hard choice blocks the ordinary gradient through the choice; it does not make learning impossible.
- A range quoted from a table spans every row it summarizes, its minimum and its maximum.
- A number keeps the metric the source attaches to it. A drop in test accuracy is not a drop in the loss.
- An "every" or "all" in a reading card is checked against each panel and setting that the caption separates, and the exceptions stay.
- An accuracy match is not evidence of equal cost. Write "at the same cost" only when the source measures runtime.
- A bug's trigger is the input the user's code receives, not an intermediate value inside the fix: a logit row with one finite entry, not "an all −∞ vector".

## Code

- A snippet's text matches what it computes. A gradient read at the input includes every path; it does not isolate one path of the math.
- A comparison changes one setting only, on the same seed and weights.
- Setting one library parameter can leave a second one that the library adds to it: set both (PyTorch's `bias_ih` and `bias_hh`).
- A number from running code is printed by a snippet in the guide, never taken from a side run.
- A sentence that says a snippet reproduces a result names exactly which values it reproduces, and what it does not run.

## Sources

- Every equation in a source image is transcribed, one formula line for each line in the image.
- A cited work's page is opened and checked for the item it is cited for. A figure cited as "page 2" of a work sat on page 3; a link to the page shows such a slip at once.
- A dataset example is a real item from the paper's own appendix when it has one, not a made-up one.
- A figure shown in part must match its caption. When the caption describes every panel, show the whole figure.

## Diagrams and layout

- An intuition diagram's causal chain holds in the boundary case it names. Identical inputs through identical arithmetic round identically, so a residual at equal inputs needs its real cause in the diagram (two different orders of operations).
- When added text pushes a guide over its cap, remove repetition across parts first (limitations against weaknesses, a reflection question asked twice), before shrinking figures or type.
