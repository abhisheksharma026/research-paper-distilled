# Key references

The guide does not reproduce the reference list. It explains the references a reader needs to understand the paper, at most 10.

## Selecting them

1. Run `python3 -I scripts/key_refs.py WORK/pages 20`. For a web article, use `WORK/web/links.json` instead: every outbound link with its section. It counts each citation in the text, lists the pages it appears on, gives one citing sentence, and takes the title from the paper's reference list. When it exits with code 2 (footnote citations or another style it cannot read), build the same list by hand from the reference list and the pages that cite each work.
2. Give each candidate a role: foundation, borrowed method, dataset or metric, baseline, competing result, direct precursor.
3. Rank by how much the paper's argument depends on it. The citation count is a starting point, not the answer: a dataset cited once can matter more than a background work cited often.
4. Keep at most 10. Prefer what the reader needs (the method borrowed, the baseline beaten, the dataset used) over frequent background citations.

## Checking them

Read each selected work: its abstract, and the section that the paper relies on. Do not rely on the paper's paraphrase or on memory. If a work is not available, mark its bullet as unverified, or ask the user whether to leave it out.

Split the work in two, so that a cheaper model never decides what a bullet says:

1. **Locate.** One agent, started with the config's `models.cited_reader` when one is set (`references/intake.md`, setup) and otherwise with the session's model, downloads every selected work and runs `python3 -I scripts/extract_pages.py WORK.pdf WORK/cited/KEY/pages` on each, all in one call. For each work it returns the pages of the abstract and of each section that this paper relies on, next to the citing sentence from this paper. It returns pages, not summaries.
2. **Read and write.** The session's model reads those pages in full, the qualifications and limits included, and writes each bullet with the sentence that supports it, word for word. When a located page does not hold what this paper cites the work for, it searches the work's pages itself.

Put the supporting sentences in `WORK/ledger-cited-KEY.json` and run `check_claims.py` against that work and its pages.

## The bullet

> **Author, year, short title.** What it introduced or found. How this paper builds on it, borrows from it or compares with it [p. N]. One important difference or limit. Checked in: its section, figure or page, written as `{key page N}`. Link the work's name in the key-references table with `{key|Name, year}`; `audit_links.py` fails on a row without a link. Leave out a work whose only link is dead, and say so.

The section sits in "Critical reading", after related work.
