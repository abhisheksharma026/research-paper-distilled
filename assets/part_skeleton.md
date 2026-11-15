# Part 3. The results

Question: The one question this part answers. This part covers Section 3 [pp. 10–30].

Markdown authoring for one part: `python3 -I scripts/check_part.py WORK/parts/part3.md PAPER.pdf` checks it and writes
the fragment build.py joins. Delete this paragraph. The HTML skeleton (part_skeleton.html) shows the same blocks as HTML.

## 3.4 A task family (Section 3.3)

Body text. Inline math such as $C \approx 6ND$ and display math become MathML:

$$
C \approx 6 N D
$$

A claim from the paper ends with its page marker, which the build hides. [p. 12]

<!-- A diagram the guide draws: render it with diagram.py first. Its caption names where it is drawn from. -->
::: snap wide

![Recurrence against self-attention, drawn from Section 1 [p. 2]](diagrams/intuition-attention.svg)

::: card

- **Diagram:** the order to read it in, and the idea it shows.

:::

:::

<!-- A figure or table from the paper, cropped with crop.py: "Label [p. N]: caption word for word". Use "snap wide"
     for a wide item (card below) and "snap" for a tall one (card beside). The id lets the text link to it. -->
::: snap wide #table-2

![Table 2 [p. 15]: The caption, word for word.](figures/table-2.png)

::: card

- **Table:** the rows and columns, and which comparisons are fair.
- **Takeaway:** one sentence. **Caution:** the trap, if any.

:::

:::

The text links to it as [Table 2](#table-2).

::: box math

### Math 3. What the formula computes

What the formula is for, the formula, its derivation one move per line, each symbol, and a worked example.

$$
C \approx 6 N D
$$

**Why:** why the authors chose this, and what it gains.

:::

::: box note

### Check yourself

One question.

**Answer.** Its answer.

:::

| Claim | Supporting result | Direction and size | Caveat |
|---|---|---|---|
| The main claim | [Table 2](#table-2) | The effect, with its numbers. | The authors' own limit. [p. 5] |

A cited work's page: {ho2020 page 4}. The work itself: {ho2020|DDPM}.

::: check

### Questions to reflect on

1. **A question about a trade-off or an assumption?** The answer, ending with its page. [p. 14]

:::
