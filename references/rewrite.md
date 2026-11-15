# Restyling an existing guide

Use this when a finished guide must change its voice or the order of its explanations, and its content must not change: for example, a guide written before `voice.md` existed. The content was checked against the paper once; the rewrite must not undo that.

## The method

1. **Back up first.** Copy the guide's `src/parts/`, its stylesheet and its PDF outside the guide's folder.
2. **Rewrite each part into `src/parts_v2/`**, never in place. Parts are independent, so one agent per part (or per group of short parts) can run in parallel. Give every agent the same brief, below.
3. **Check each part** with `python3 -I scripts/check_rewrite.py src/parts/NAME.html src/parts_v2/NAME.html` until it reports 0 FAIL. For a section split across files, join the files in build order, old and new, and check the joined pair.
4. **Read every WARN.** A new number must be arithmetic on old numbers, shown as arithmetic. A page reference cited fewer times must still sit beside every claim it supports.
5. **Build the new version beside the old one** (a second config whose `parts` point at `parts_v2/`, output `NAME_v2.pdf`), run every check in `verification.md`, and give the user both PDFs.
6. **Promote only on the user's word:** replace `src/parts/` with `parts_v2/`, rebuild, confirm the new main PDF's text equals the `_v2` PDF's, then delete the `_v2` files.

A rewrite in this voice grows the prose by 6 to 10%. If the guide was near its page cap, let math boxes split after their formula (the default stylesheet does) before cutting text.

## The brief for each agent

- **Read** `references/voice.md` (the order of explanation, the sentence rules, and how the voice lands on each part of a guide) and the "Style" and "Why:" sections of `references/writing.md`.
- **Change** only the prose: the problem first, then "In short" and the cost; terms defined by role; signposts with one job each; bold opening claims in results and summaries; paired contrasts with the same shape; one to three sentences per paragraph; a short lead before each results section's figures.
- **Keep byte for byte:** every `<math>`, `<table>`, `<figure>`, `<img>`, `<pre>`, caption (`div.cap`), dataset item (`div.ex`) and include line; every `h2`, `h3` and `h4`, and every section id; the markup kinds (`box math`, `box note`, `card`, `snap`, `check`, `answer`, `question`, `a`) and the bold card labels.
- **Keep every fact:** every number, `[p. N]` reference and quoted passage in the old prose. Add no fact, number, claim or source.
- **Keep the length** within about 10% of the old prose, and each graded answer within its word limit, with every point it makes.
- **No labels:** no self-labels, source tags or meta labels, and no "I" to say where a value came from.
- **Finish** only when `check_rewrite.py` reports 0 FAIL, and report the summary line, the word counts, each WARN with its reason, and three before-and-after examples.

## What the checker does and does not catch

It fails on a changed fixed block, a changed heading sequence, a lost page reference, quote or number, unbalanced tags and the common banned labels. It does not judge meaning: a sentence can keep every number and still say something different. So read the before-and-after examples, and spot-check the parts with the most rewritten prose against the paper.
