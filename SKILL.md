---
name: research-paper-distilled
description: Use when the user wants a structured, source-verified study guide or course paper review from a research-paper PDF, an arXiv link or a technical web article such as a blog post, and the output must teach the figures, tables, metrics, math, datasets or references. Not for a brief summary of a paper or a citation lookup.
---

# Research paper distilled

## Overview

Turn one research paper into a study guide that a junior AI engineer can learn from without opening the paper: the claim, the setup, the evidence with the paper's own figures and tables, the metrics and math worked by hand, real dataset items, the limits and the key references. Every number, quote, page reference and link is checked against the paper before delivery.

A technical web article (a blog post, an online explainer) goes through the same workflow: `references/web.md` says how it is fetched, pinned and cited as `[§ N]`.

The user decides the size and the depth. The plan and the pilot are approved before the full build. Nothing is delivered until the scripts pass. The independent review runs before delivery at full review depth, and is offered at delivery at lean depth.

## Workflow

Each phase ends at its gate. Do not start the next phase before the gate passes.

**Keep the main conversation short.** Every call re-reads the whole conversation, so its length multiplies the cost of every later step. Start a guide in a fresh session. When the session is already long at the plan gate, hand steps 4 and 5 to one orchestrator agent with the plan, the brief and the hand-back file, and wait for its report. The main conversation does intake, the plan, the hand-off and delivery.

1. **Intake.** Read `references/intake.md`. On the first run (no local config), do its setup first. Ask its four questions in one round (the third covers the pilot and fetching cited works, the fourth the review depth), with the computed length options and a recommended default for each. State the other defaults in one line. Use only the user's answers and the defaults: do not carry over limits from an earlier guide unless the user says so. *Gate: answers received or defaults accepted.*
2. **Map and plan.** Run `python3 -I scripts/extract_pages.py PAPER.pdf WORK/pages`. It pins the file and stops on a scanned PDF. For a web article, run `python3 -I scripts/fetch_web.py URL WORK/web` instead, and follow `references/web.md`. For an arXiv paper, also run `scripts/fetch_source.py` for the exact equations and table cells, and `scripts/key_refs.py` to rank the references. From the pages and `captions.json`, list every section, appendix, figure, table, equation, dataset and metric. Write the plan: the parts in order with a page budget for each, the paper pages each part covers, the critical sections that get an intuition diagram, and every paper section marked cover, summarize or omit with its reason. Pick the paper mode in `references/modes.md`; for a web article that is an engineering post, use that file's last section instead. From here on, read only the pages of sections the plan covers; to find a number, a quote or a caption, search the page files instead of reading whole pages. Add the reader questions from four lenses, each mapped to the subsection that will answer it (`references/reader-questions.md`). *Gate: the user approves the plan.*
3. **Pilot** (when intake turned it on). Build two or three parts that together hold one figure with its reading card, one math box or metric entry, one dataset example and one limitation. For an engineering post, the pilot holds one mechanism step with its diagram and the running example, one claim from the claim-evidence table, and one item from "What the post does not say". Run the full check list on them. *Gate: the user approves the format.*
4. **Full build, one part per subagent.** Write `WORK/brief.md` once, with what every part writer shares: the files to read, the reader and maths assumed, the toolkit facts so far, the notation, the running example, the figures and tables already shown with their ids, the output contract and the hand-back. Point each part writer to it, and append each hand-back to `WORK/handbacks.md`. Write each part in its own subagent, so the main conversation stays short; parts that do not depend on each other may run in parallel. **Each part writer works within about 20 tool calls:** it reads the brief's files and its pages in one or two calls, writes the part in one Write, and runs `scripts/check_part.py`, again only after a fix. It views each crop once, searches pages instead of rereading them, never reads back its own files, and never builds or audits the guide. The budget limits overhead, not content: never drop a derivation, a figure or a check to stay inside it. Brief each subagent with the reader level and its assumed-knowledge and maths columns from intake, its part's plan entry and page list, its first Math and Code numbers (numbering runs across the whole guide; the plan gives a range to each part that runs in parallel), the running example's values and the toolkit facts so far, and the previous part's note on what this part uses. It reads `references/writing.md`, `references/voice.md` and `assets/part_skeleton.md`, plus `references/layout.md` when it crops a figure or draws a diagram, and `references/evidence.md` when its pages hold datasets, benchmarks or code, or the part prints code. It reads only its own pages, finds crop boxes with `scripts/page_map.py`, and writes `WORK/parts/partN.md`, `WORK/ledger-partN.json` and, for a paper figure, `WORK/crops-partN.json`. It hands back those paths and one paragraph: the toolkit facts it added, the running example's values, the next free Math and Code numbers, and what the next part uses. (A part can still be written as HTML from `assets/part_skeleton.html`.) In the main conversation, or in the orchestrator when one runs, generate the scoreboard for empirical papers with `scripts/scoreboard.py`, select the key references with `references/key-references.md`, and build with `python3 -I scripts/build.py WORK/guide.json`. Until every part exists, run the link audit with `--partial`. At full review depth, then run the grounded follow-up pass on each critical section, and add what it finds (`references/reader-questions.md`).
5. **Verify.** Read `references/common-mistakes.md`, then run every check in `references/verification.md`: the claims ledger of each part, the link audit, the build checks, the coverage check against the plan, and a look at each rendered spread. Fix, rebuild, and run them all again; after a rebuild, look again only at the spreads whose pages changed. The link audit runs last: every cited-work page, Code, Image and key reference must be a link, so add each missing one before delivery.
6. **Independent review.** Use the reviewer saved in the local config (`references/intake.md`, setup), then its `second_reviewer` when one is set. When no reviewer is saved, or a saved one cannot run, use a fresh agent of the same model. When the reviewer kind is `none`, skip this step and say so at delivery. At full depth, review the whole guide before delivery. At lean depth, deliver first, then offer one review of the critical sections, and run it only if the user accepts. Send the guide, the paper and the user's requirements with the prompt in `references/verification.md`, its scope set to the whole guide or the critical sections. Confirm each finding in the paper before applying it. For each confirmed finding that no script caught, add the general rule it teaches to the user's own `~/.config/research-paper-distilled/review-findings.md`, never to the shipped `references/review-findings.md`. Rebuild and repeat step 5, link audit last.
7. **Deliver.** Give the absolute path of the PDF and its HTML source. Report what each check found, which reviewer ran (and whether it was the fallback), or that the review was offered and declined, and anything only spot-checked. Do not commit unless asked.

## The guide contract

Every guide has this shared core, in this order:

1. **The central idea**: an overview diagram of what the paper changes, then the central question, the claim and its stated limits, a claim-evidence table, the paper's own concepts that the rest depends on, and "The maths this guide uses": the toolkit of facts the derivations need (`references/writing.md`).
2. **The substance**, in the structure of the paper's mode (`references/modes.md`): empirical, theory, survey, explainer, systems or method.
3. **Limitations**, and broader impacts when the paper discusses them, with how sure the authors are.
4. **Critical reading**: related work, strengths, weaknesses, the key references (at most 10, in a section titled "Key references", each linked to the work), later work in its own section, and what a re-implementation would need.
5. **Every metric in the paper**, when the paper reports metrics: each metric's formula, a worked example, its "Why" and its trap. A metric already explained in a part gets a one-line pointer.

Include datasets, compute, metrics and broader impacts only when the paper has them. Never write an empty section. Each part ends with "Questions to reflect on", with answers. Each figure and table appears once, at the first place the guide cites it, with its caption word for word; later mentions link back to it. The reader does not have the paper, so the guide never cites a figure or table it does not show.

## Quick reference

| Need | Run |
|---|---|
| A web article as the source: sections as pages, images, math, links, pin | `python3 -I scripts/fetch_web.py URL OUT [--last "Heading"]` |
| Page text, caption list, version pin, scanned check | `python3 -I scripts/extract_pages.py PAPER.pdf OUT` |
| Exact equations and table cells from the TeX | `python3 -I scripts/fetch_source.py ARXIV_ID_vN OUT` |
| References ranked by how the paper uses them | `python3 -I scripts/key_refs.py PAGES [TOP]` |
| Line positions on a page, for a crop box | `python3 -I scripts/page_map.py PAPER.pdf PAGE` |
| Figure and table crops | `python3 -I scripts/crop.py PAPER.pdf MANIFEST.json OUT [DPI]` |
| Scoreboard from results | `python3 -I scripts/scoreboard.py RESULTS.json TABLE.html COUNT.html` |
| One part: crops, changed diagrams, Markdown to HTML, claims ledger; prints only failures | `python3 -I scripts/check_part.py WORK/parts/NAME.md PAPER.pdf` |
| Build, links, page cap, true size | `python3 -I scripts/build.py GUIDE.json` |
| Reader questions: every lens asked, placed in the guide, answered on its page | `python3 -I scripts/check_questions.py GUIDE.html QUESTIONS.json PAGES` |
| Numbers, quotes, calculations | `python3 -I scripts/check_claims.py LEDGER.json PAPER.pdf PAGES` |
| Links, cross-references, number wording, every cited figure shown | `python3 -I scripts/audit_links.py GUIDE.html PAPER.pdf PAGES`; add `--partial` while only some parts are built |
| Spreads for the visual check | `python3 -I scripts/render_spreads.py GUIDE.pdf OUT` |
| Restyle a finished guide without changing its content | `references/rewrite.md`; each part checked with `python3 -I scripts/check_rewrite.py OLD.html NEW.html` |
| An overview or intuition diagram the paper does not draw | `python3 -I scripts/diagram.py DIAGRAM.mmd OUT.svg` |

Each script documents its inputs at the top. The tools need poppler (`pdftotext`, `pdftoppm`, `pdfinfo`) and Google Chrome; diagrams also need Node.js.

## Common mistakes

`references/common-mistakes.md` lists the mistakes seen before and the fix for each. Read it at the verify step.
