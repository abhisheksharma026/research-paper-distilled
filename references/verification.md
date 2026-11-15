# Verification

Run all of these after the full build, again after the review fixes, and the link audit last of all. Report the results at delivery.

## The checks

| Check | How | Pass |
|---|---|---|
| Version pin | `extract_pages.py` writes `paper.json`; `check_claims.py` and `audit_links.py` refuse a different PDF; `build.py` refuses an arXiv URL without its version | the pinned file throughout |
| Scanned PDF | `extract_pages.py` lists low-text pages and exits with code 2 when most pages have no text | not scanned, or OCR offered and its numbers reported as spot-checked |
| Numbers, quotes, derived values | Record each claim in `WORK/ledger.json` while writing (format at the top of `scripts/check_claims.py`), then run it | 0 failed |
| Links and cross-references | `scripts/audit_links.py`: anchors, Part, Math, M, Code and Image references and where each one lands, paper figure, table, section and appendix names, prompt-figure pages, every `[p. N]` or `[§ N]`, a page reference the reader can see (each marker must be hidden), and links that are missing: a cited-work "page N", a "Code N" or "Image N", or a key reference with no link; and a figure or table the guide cites but does not show. While only some parts are built, run it with `--partial`: references to parts or metric entries not built yet, and the missing "Key references", move to PENDING | 0 FAIL; read every WEAK line against its page; at delivery, 0 PENDING without `--partial` |
| Cited-work links | each `works` URL serves the exact PDF read: download it into an empty folder and compare its SHA-256 with the copy the checks used | identical files, so every `#page=N` opens the cited page |
| Number wording | the READ list of `audit_links.py`: a percentage without "points" or "relative", "significant" with no test or repeated runs, "best" with no metric direction | each READ line fixed, or confirmed against the paper |
| Build | `scripts/build.py` | within the page cap; the title prints at true size; the page count is stable across both passes |
| Crops | `scripts/crop.py` | no "TOUCHES BOX EDGE"; the crop count matches the plan |
| Diagrams | `scripts/diagram.py`, then `scripts/audit_links.py` | every label is SVG text (HTML labels do not render in an image) and prints at 7 pt or more; the overview diagram opens Part 1; each intuition diagram comes before its subsection's math; no symbols or Part, Math or section labels; boxes in reading order; each box traces to the paper |
| Coverage | Compare the guide with the plan, section by section | every section covered, summarized, or omitted with its reason, including related work, the conclusion and the appendices that define data, metrics or prompts |
| Reader questions | `scripts/check_questions.py` on `WORK/questions.json` | every lens has 3 to 5 questions; each question and follow-up lands in a real subsection; each answer's phrase is on its page; each question the paper does not answer is said so where it lands |
| Visual | `scripts/render_spreads.py` at its default 80 dpi, then look at each spread; after a rebuild, only the spreads whose pages changed | no clipped formula, overflow, stranded heading or empty half page |

## Failure modes seen before, and the check that catches each

- A table row or an accented word matches only one text extraction: `check_claims.py` and `audit_links.py` search both, after Unicode NFC normalization.
- A quoted sentence crosses a page break, so its page reference is wrong: both scripts test the quote on the cited page.
- `pdftotext -bbox` crashes on some poppler versions: `page_map.py` uses `-tsv`.
- A caption sits above its item, or several items share a page: `crop.py` takes boxes from a manifest, never from the caption alone.
- One wide formula or table makes Chrome shrink every page: `build.py` fails when the title prints below true size.
- Links and references drift after edits: `audit_links.py` checks every link target and fails on any reference left unlinked.
- A review finding is wrong: confirm each one in the paper before applying it.
- A web article keeps its math inside images, so no script can read it: transcribe each equation, view the image again beside the transcription, and report it as checked by eye.
- A web guide labels an image with the wrong section ("Image 12 [§ 4]" for an image in § 5): `audit_links.py` checks each "Image N [§ M]:" label against `images.json`.
- A web article's fetch keeps the wrong sections: read the list `fetch_web.py` prints, and rerun it with `--last` when it cut too much or too little.
- A quote from a cited work shares a sentence with this paper's page marker, so the audit tests it against the wrong paper: give the cited work's quote a sentence of its own.
- A meta label, self-label or source tag slips into the text ("How to read this table", "(my calculation)", "(external: ...)"): `audit_links.py` fails on them.
- A cited work's page is written "p. 6", so the build links it to page 6 of this paper: write `{key page 6}`. `audit_links.py` fails on "their p. N" and "Section N (p. N)".
- A reference the reader would click is left as plain text: a cited work's "(page 3)", a "Code 5", an "Image 7", a key reference's name. `audit_links.py` fails on each one, and on a Code or Image link that lands on the wrong item. Run it after the last edit, and add the missing links before delivery.
- A cited work's link serves a different version from the one read, so its page numbers are wrong: compare the download's checksum with the copy read; `build.py` refuses an arXiv URL without its version.
- A value exists only inside a figure image (a fitted equation, a plotted label), so no text layer holds it: read it on the crop, and report it at delivery as spot-checked.

## The review prompt

Send this to the reviewer, filled in. Ask for a report only, with no file changes.

**A command reviewer** (`kind: command` in the local config) is run as `COMMAND PROMPT.txt GUIDE.html PAPER.pdf`: the filled prompt saved as a text file, then the guide's HTML and the paper (a web source's `source.html` in place of the PDF). It prints its report to standard output and exits with 0. Before running it, check that the command exists on the PATH and that its credential variable is set. Stop it after 20 minutes. A missing command, an unset variable, a non-zero exit, a timeout or an empty report counts as a failed review: run a fresh agent of the same model instead, and say so at delivery.

```
Review only; do not edit files. A final, one-time review of the scope below.
SCOPE: the whole guide (full depth), or only the critical sections named here (lean depth). Every check below applies within the scope.
CONTEXT: the paper (title, version, pages), the reader level, the purpose.
FILES: the guide PDF, its HTML source and parts, the crops, the paper PDF and its page texts.
REQUIREMENTS: the intake answers (page cap, level), the guide contract, the writing rules; for an engineering post, also its mode and the rules in the last section of `references/modes.md`, which win where they differ.
ALREADY CHECKED: the script results above, so the reviewer does not repeat them.
REVIEW: (a) faithfulness of every [p. N] claim (the build hides the markers, so read them in the HTML source), and whether the source's qualifiers ("in theory", "some",
"may") survive; (b) every formula and worked example: is each displayed equality exact, or true only on one
path, in one case or approximately, and does the formula say so; is every function defined before its first
number; does every condition list all its parts; (c) every code snippet: does it measure what its text says,
does a comparison change one thing only, is every library parameter that combines with a set one also set;
(d) every equation in the source's images transcribed, one line per line; (e) teaching order and important
omissions; (f) duplication, and text too dense or simplified until wrong; (g) numbering, cross-references,
labels and verbatim captions. Also check each class listed in references/review-findings.md and in ~/.config/research-paper-distilled/review-findings.md when it exists.
REPORT: verdict first (ready / ready after changes / not ready); then ranked findings, each major or minor, with
location, evidence quoted from the paper with its page, and replacement text; then what was found clean;
at most 1,500 words.
```
