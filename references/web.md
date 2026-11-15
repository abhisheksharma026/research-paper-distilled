# A web article as the source

Use this when the source is a technical web article (a blog post, an online explainer, lecture notes on one page) rather than a paper PDF. The workflow, the guide contract, the voice and the checks stay the same. Only the source handling changes.

## Fetch and pin

Run `python3 -I scripts/fetch_web.py URL WORK/web`. Read the list of sections it prints: these are the article's sections, numbered §1, §2 and so on. Check that it kept every section of the article and cut only what follows it (related posts, comments). When it cut too much or too little, run it again with `--last "Heading"`, naming the article's last heading.

The script pins the fetched page by its SHA-256 and the fetch date (`WORK/web/pages/paper.json`). Report both at delivery. A web page can change, so the checks refuse any other copy; when the live page has changed, fetch it again and run every check again.

## Citing the article

- Cite a section as `[§ N]`, where N is the section's number from the fetch. The build turns it into a hidden link to that section's anchor on the live page; give the build config `"web_source": "WORK/web"`.
- Part 1 lists the sections once, so a reader can map the numbers: "The post's sections: §1 Recurrent Neural Networks, §2 ...".
- A web guide has no `[p. N]`; the link audit fails on one. Wherever another reference file names a `[p. N]` marker or a paper page, a web guide uses `[§ N]` and the section; the plan gives each part its sections in place of pages.
- The checks read the sections as pages: run `check_claims.py` and `audit_links.py` with `WORK/web/source.html` in place of the paper and `WORK/web/pages` as the pages. In the claims ledger, write `"section": N`.

## Images and math

- **Use the article's own images** from `WORK/web/images/` (listed in `images.json` with their section and the sentences around them), copied into the guide's `snapshots/`. Do not crop the printout. Leave out a decorative banner, and say so in the plan.
- **Captions:** most posts give their images no caption. Label each one by its order and section, then say in one plain sentence what it shows: `<b>Image 9 [§ 5]:</b> The forget gate's step, with its equation.` View each image before writing about it.
- **Math that lives only in images** is common in blog posts. Transcribe each such equation into MathML beside its image, then view the image again to confirm the transcription. Write one formula line for each equation line in the image, and count both: an equation described in words in place of its formula is a missing transcription. Report these at delivery as checked by eye, because no script can read them.
- **Math written in the text** is in `math.json` as TeX; copy it exactly.

## Length, mode and references

- **Length at intake:** count the article's prose words (the fetch prints them) and divide by 500 to get its pages for the length table in `intake.md`.
- **Mode:** usually "Explainer" in `modes.md`: the author's concepts in order, the math mapped step by step through one worked example, and a build in code. An engineering post, which describes the author's own system, product, outage or practice, takes the modes in the last section of `modes.md` instead.
- **References:** `links.json` lists every outbound link with its section. Its URLs go into the build config's `works` for each cited work the guide quotes, after the checksum check in `verification.md`. That is the article's reference list for `key-references.md`; most of its key references are the papers the author links to.
- **Rights:** the images are the author's. Keep the personal-study notice, and warn before the user publishes the guide.
