"""Audit every internal link and cross-reference in a built study guide against the guide and the source paper.

Usage: python3 -I audit_links.py GUIDE.html PAPER.pdf PAGES_DIR [--partial]
       python3 -I audit_links.py GUIDE.html WEB/source.html WEB/pages      (a web article from fetch_web.py: [§ N])
Checks: anchors; Part, section, Math and M-entry references; paper figure, table, section and appendix names;
lettered appendix items cited with a page; that every figure or table the guide cites is shown with its caption;
every [p. N] or [§ N] reference (quote, numbers, caption, or shared distinctive words);
in a web guide, each "Image N [§ M]:" label against images.json; that every cited-work page, Code N, Image N and key
reference is a link, and that a "Key references" section exists; that the overview diagram opens Part 1 and each intuition
diagram comes before its subsection's math, both with no math or section labels; and banned
labels (card headings such as "How to read this table", meta labels, self-labels such as "(my calculation)").
Exit code 1 on any FAIL. WEAK lines share too few words with the cited page and need a person to read them. READ lines
need a person too: number wording that may overstate a result, and an absolute word ("fails", "cannot") where the
closest sentence of the cited page hedges ("in practice", "may", "unclear"). Only sentences that carry a reference are read.
"""
import bisect, html, os, re, subprocess, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from labels import LABEL, caption_after

guide_path, pdf, pages_dir = sys.argv[1:4]
# --partial: the guide is built a few parts at a time. A reference to a part or metric entry not built yet, and the missing
# "Key references" section, are listed as PENDING instead of FAIL. Every other check runs as usual.
partial = '--partial' in sys.argv[4:]
import hashlib as _h, json as _j, os as _o
def _pin(pdf, pages_dir):
    pin = _o.path.join(pages_dir, 'paper.json')
    if _o.path.exists(pin) and _h.sha256(open(pdf, 'rb').read()).hexdigest() != _j.load(open(pin))['sha256']:
        sys.exit(f'{pdf} is not the pinned paper in {pin}: a different version changes every page number')
_pin(pdf, pages_dir)
src = open(guide_path, encoding='utf-8').read()
def norm(t):
    t = unicodedata.normalize('NFC', t).replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
    return re.sub(r'\s+', ' ', t)
squash = lambda t: re.sub(r'[\s,]+', '', norm(t).lower())
body = re.sub(r'</?a\b[^>]*>', '', re.sub(r'<sup>(.*?)</sup>', r'\1', src))
body = re.sub(r'</(p|li|td|th|h2|h3|h4|div|figure)>', ' ¶ ', body)
text = norm(html.unescape(re.sub(r'<[^>]+>', ' ', body)))
fails, weak, pending = [], [], []
unbuilt = lambda msg: (pending if partial else fails).append(msg)
cache = {}
def page_text(n):
    if n not in cache:
        try:
            plain = open(f'{pages_dir}/{n}.txt', encoding='utf-8').read()
        except FileNotFoundError:
            plain = ''
        layout = '' if web else subprocess.run(['pdftotext', '-f', str(n), '-l', str(n), '-layout', pdf, '-'], capture_output=True, text=True).stdout
        cache[n] = norm(plain + ' ' + layout)
    return cache[n]
# A web article (fetch_web.py) has numbered sections in place of pages: [§ N] in place of [p. N].
web = pdf.endswith('.html')
anchors = _j.load(open(_o.path.join(pages_dir, 'paper.json')))['anchors'] if web else []
# The article's own images, labelled "Image N [§ M]:" in the guide: image N must sit in section M (images.json).
image_sections = {im['n']: im['section'] for im in _j.load(open(_o.path.join(pages_dir, '..', 'images.json')))} if web else {}
n_pages = len(anchors) if web else int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout)[1])
paper_all = ' '.join(page_text(n) for n in range(1, n_pages + 1))

# 1. Anchors
all_ids = re.findall(r'id="([^"]+)"', src); ids = set(all_ids)
# Parts written separately can both number a box "Math 1."; a repeated id sends every link to the first one.
for i in sorted({i for i in all_ids if all_ids.count(i) > 1}):
    fails.append(f'id "{i}" appears {all_ids.count(i)} times: number Math boxes, Code snippets and figures across parts')
for target in re.findall(r'href="#([^"]+)"', src):
    if target not in ids:
        fails.append(f'link #{target}: no element has this id')

# 2. Guide structure
parts = set(re.findall(r'<h2[^>]*>Part (\d+)\.', src)); sections = set(re.findall(r'<h3[^>]*>(\d+\.\d+) ', src))
maths = set(re.findall(r'<h4[^>]*>Math (\d+)\.', src)); metrics = set(re.findall(r'<h4[^>]*>M(\d+)\.', src))
for m in re.finditer(r'\bParts? (\d+)(?:\.(\d+))?(?: (?:to|and) (\d+))?', text):
    for n in [m[1]] + ([m[3]] if m[3] else []):
        if n not in parts: unbuilt(f'"{m[0]}": the guide has no Part {n}')
    if m[2] and f'{m[1]}.{m[2]}' not in sections:
        (unbuilt if m[1] not in parts else fails.append)(f'"{m[0]}": the guide has no section {m[1]}.{m[2]}')
for n in re.findall(r'\bMath (\d+)\b', text):
    if n not in maths: fails.append(f'"Math {n}": no such math box')
for a, b in re.findall(r'\bM(\d+)(?: to M(\d+))?\b', text):
    for n in [a] + ([b] if b else []):
        if n not in metrics: unbuilt(f'"M{n}": no such metric entry')

# 2b. References a reader would click: a cited work's page, a code snippet, an image, a key reference. Each one must be
# a link. The text below keeps only what sits outside links, code and snippet headings.
outside = re.sub(r'<a\b[^>]*>[\s\S]*?</a>|<pre[\s\S]*?</pre>|<div class="codeh">[\s\S]*?</div>|<style[\s\S]*?</style>', ' ', src)
outside = norm(html.unescape(re.sub(r'<[^>]+>', ' ', outside)))
for m in re.finditer(r'\bpages? \d+', outside):
    fails.append(f'"{m[0]}" is not a link: write {{work page N}} with the work in the config\'s "works"')
for m in re.finditer(r'\{[a-z][\w-]*(?:\|[^{}]*|\s+pages?\s[^{}]*)\}', outside):
    fails.append(f'"{m[0]}": a work marker the build did not convert')
for m in re.finditer(r'\b(Code|Image) (\d+)\b(?! \[)', outside):
    fails.append(f'"{m[0]}" is not a link' + ('' if f'{m[1].lower()}-{m[2]}' in ids else f': no element has id {m[1].lower()}-{m[2]}'))
# A key reference is a table row (the work in its first cell) or a list item (the work in its bold lead).
keyrefs = re.search(r'<h3[^>]*>(?:[\d.]+ )?Key references</h3>[\s\S]*?(<table[\s\S]*?</table>|<ul[\s\S]*?</ul>)', src)
leads = re.findall(r'<tr>\s*<td>([\s\S]*?)</td>|<li>\s*<(?:b|strong)>([\s\S]*?)</(?:b|strong)>', keyrefs[1] if keyrefs else '')
# A web article that links to no other work has nothing to list, so only then may the section be absent.
no_works = web and not _j.load(open(_o.path.join(pages_dir, '..', 'links.json')))
if not keyrefs and not no_works: unbuilt('no section titled "Key references": the guide contract requires one, and the link check reads it')
elif keyrefs and not leads: fails.append('the key references hold no table rows or bold-led list items to check')
for lead in (a or b for a, b in leads):
    if '<a ' not in lead: fails.append(f'key reference "{re.sub(r"<[^>]+>", "", lead)[:40]}" does not link to the work')

# 3. Paper items named in the guide must exist in the paper. A plural citation ("Tables 1 and 2", "Figures 3 to 5") names
# each item in it.
# "Fig. 4", "Fig 4", "FIG. 4" and "Figure 4" name one item, as do "TABLE II" and "Table II": every comparison below uses
# this canonical form. A citation may also be a list or a range: "Tables 1 and 2", "Table II and III", "Figures A.1–A.3".
ITEM_ID = r'(?:[0-9A-Z]+\.)?(?:\d+|[IVXL]+)\b'
KIND = r'(?:Figures?|Fig\.?|Figs\.?|FIG\.|Tables?|TABLES?)'
def canon(label):
    kind, ident = label.rsplit(' ', 1)
    k = kind.lower()
    return ('Figure ' if k.startswith('fig') else 'Table ' if k.startswith('table') else kind + ' ') + ident
ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50}
def roman(r):
    n = [ROMAN[c] for c in r]
    return sum(-v if i + 1 < len(n) and v < n[i + 1] else v for i, v in enumerate(n))
def to_roman(n):
    out = ''
    for v, r in ((50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')):
        while n >= v: out += r; n -= v
    return out
def expand(a, b):
    """Every item from a to b: numbers, Roman numerals, or numbers that share a prefix such as "A."."""
    pa, na = re.match(r'((?:[0-9A-Z]+\.)?)(.*)', a).groups(); pb, nb = re.match(r'((?:[0-9A-Z]+\.)?)(.*)', b).groups()
    if pa != pb: return None
    if na.isdigit() and nb.isdigit(): return [f'{pa}{n}' for n in range(int(na), int(nb) + 1)] or None
    if re.fullmatch(r'[IVXL]+', na) and re.fullmatch(r'[IVXL]+', nb): return [f'{pa}{to_roman(n)}' for n in range(roman(na), roman(nb) + 1)] or None
    return None
def cited_items(t):
    # Roman numbers count only in a paper whose own captions use them, so "Table I think" or "Figure 1 to X" in an
    # Arabic-numbered paper is prose, not a citation.
    item_id = ITEM_ID if ROMAN_PAPER else r'(?:[0-9A-Z]+\.)?\d+\b'
    found = set()
    sep = r'\s*(?:,\s*and|,|and|&|to|&ndash;|–|-)\s*'
    for m in re.finditer(rf'\b({KIND}) ({item_id}(?:{sep}{item_id})*)(?!\.\d)', t):
        kind = canon(m[1] + ' 0').split()[0]
        for a, rng, b in re.findall(rf'({item_id})(?:\s*(to|&ndash;|–|-)\s*({item_id}))?', m[2]):
            items = expand(a, b) if rng else [a]
            if items is None:
                fails.append(f'"{m[0]}": a range this audit cannot expand; list its items one by one'); items = [a, b]
            found |= {f'{kind} {x}' for x in items}
    return found
paper_items = {canon(m[0]) for m in re.finditer(LABEL, paper_all) if re.match(caption_after(m[0]), paper_all[m.end():])}
ROMAN_PAPER = any(re.fullmatch(r'(?:[0-9A-Z]+\.)?[IVXL]+', i.split(' ', 1)[1]) for i in paper_items)
for item in sorted(cited_items(text)):
    if item not in paper_items: fails.append(f'"{item}": the paper has no item with this caption')
# 3b. The reader does not have the paper open, so every figure or table the guide cites is shown in it, as a crop with
# its caption "<b>Label [p. N]:</b>". A cited item with no such caption is a defect, in a partial build too.
# A caption counts only inside a <figure> whose image file exists.
shown = set()
for fig in re.findall(r'<figure\b[^>]*>([\s\S]*?)</figure>', src):
    cap = re.search(rf'<div class="cap"[^>]*>\s*<b>({LABEL}|Image \d+)', fig)
    img = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', fig)
    if not cap: continue
    if img and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(guide_path)), img[1])): shown.add(canon(cap[1]))
    else: fails.append(f'"{cap[1]}": its caption has no image' + (f' (file not found: {img[1]})' if img else ''))
for item in sorted(cited_items(text) - shown):
    fails.append(f'"{item}": cited but not shown; place its crop, caption and card where the guide first cites it')
for sec in sorted(set(re.findall(r'\bSections? (\d+(?:\.\d+)*)', text))):
    if not re.search(rf'(^| ){re.escape(sec)} +[A-Z]', paper_all): fails.append(f'"Section {sec}": no such heading in the paper')
for app in sorted(set(re.findall(r'\bAppendix ([A-Z])\b', text))):
    # A heading such as "C Translations", or in small caps as the PDF text gives it, "C T RANSLATIONS".
    if not re.search(rf'(^|\s){app}\s+[A-Z](?:[a-z]+|\s[A-Z]{{2,}})', paper_all): fails.append(f'"Appendix {app}": no such appendix heading')
# An appendix item cited with its page ("G.18, p. 55", "A.3, p. 21") must be a figure or table on that page.
for m in re.finditer(r'\b([A-Z])\.(\d+)[^)\]]{0,12}?p\. (\d+)', text):
    if re.search(r'(?:Section|Appendix|Sections)\s*$', text[max(0, m.start() - 12):m.start()]): continue
    item = f'{m[1]}.{m[2]}'
    if not re.search(rf'(?:Figure|Fig\.|Table|TABLE) {re.escape(item)}\b', page_text(int(m[3]))):
        fails.append(f'"{item}, p. {m[3]}": no figure or table {item} on page {m[3]}')

# 4a. Links: a paper link must open the page its text names; a guide link must land on the matching heading.
heads = {i: norm(html.unescape(re.sub(r'<[^>]+>', ' ', t))).strip() for i, t in re.findall(r'<h[234] id="([^"]+)">(.*?)</h[234]>', src, re.S)}
heads.update({i: f'Part {n}' for i, n in re.findall(r'<section class="part[^"]*" id="([^"]+)">\s*<h2>Part (\d+)\.', src)})
heads.update({i: f'Code {n}.' for i, n in re.findall(r'id="(code-\d+)"><div class="codeh">Code (\d+)\.', src)})
heads.update({i: f'Image {n} ' for i, n in re.findall(r'<div class="cap" id="(image-\d+)"[^>]*><b>Image (\d+) ', src)})
for href, label in re.findall(r'<a class="pg" href="[^"#]*#([^"]+)">(§ \d+)</a>', src):
    n = int(label.split()[1])
    if not web or not 1 <= n <= n_pages or href != anchors[n - 1]: fails.append(f'section link "{label}" opens #{href[:40]}')
for href, label in re.findall(r'<a class="pg" href="[^"#]*#page=(\d+)">([^<]*)</a>', src):
    first = re.search(r'\d+', label)
    if not first or first[0] != href: fails.append(f'paper link "{label}" opens page {href}')
    if int(href) > n_pages: fails.append(f'paper link "{label}" points past the last page ({n_pages})')
kind = 'Part'
for target, label in re.findall(r'<a class="ref" href="#([^"]+)">([^<]*)</a>', src):
    h = heads.get(target, '')
    # A range endpoint ("Parts 3 to 6") is linked as a bare number: it takes the kind of the range start.
    if re.fullmatch(r'\d+(?:\.\d+)?', label): label = f'{kind} {label}'
    kind = 'Math' if label.startswith('Math') else 'Part'
    item = re.fullmatch(r'(Code|Image) (\d+)', label)
    if item:
        if not h.startswith(f'{label}.' if item[1] == 'Code' else f'{label} '): fails.append(f'guide link "{label}" lands on "{h[:40]}"')
        continue
    want = re.search(r'Parts? (\d+)(?:\.(\d+))?|Math (\d+)|M(\d+)', label)
    ok_ = want and ((want[2] and h.startswith(f'{want[1]}.{want[2]} ')) or (want[1] and not want[2] and h.startswith(f'Part {want[1]}')) or
                    (want[3] and h.startswith(f'Math {want[3]}.')) or (want[4] and h.startswith(f'M{want[4]}.')))
    if not ok_: fails.append(f'guide link "{label}" lands on "{h[:40]}"')
pieces, skip = [], []
for chunk in re.split(r'(<[^>]+>)', src):
    t = re.match(r'<(/?)([a-zA-Z0-9]+)', chunk)
    if t:
        tag = t[2].lower()
        if tag in ('a', 'math', 'h2', 'h3', 'h4', 'title', 'style', 'nav') and not chunk.endswith('/>'):
            (skip.pop() if t[1] and skip and skip[-1] == tag else None) if t[1] else skip.append(tag)
    elif not skip:
        for u in re.findall(r'(?<![\w])(?:pp?\. \d+|Parts? \d+(?:\.\d+)?|Math \d+\b|M\d+\b)|§ \d+', html.unescape(chunk)):
            target = re.fullmatch(r'Parts? (\d+)(?:\.\d+)?|M(\d+)', u)
            missing = target and ((target[1] and target[1] not in parts) or (target[2] and target[2] not in metrics))
            (unbuilt if missing else fails.append)(f'reference "{u}" is not a link')

# Labels the guide must not use: card headings (capitalized, so a sentence such as "shows how to read it" passes),
# meta labels, self-labels and source tags. Show the arithmetic or say it in a plain sentence instead.
HEADING = r'\bHow to read (?:this|these|it)\b'
LABELS = (r"\bIn plain words\b|\bPaper says\b|\bLater work:|\bMetric card:"
          r"|\bmy (?:calculations?|readings?|wording|numbers|assessments?|estimates?|measures?|checks?|choices?|own|inferences?)\b"
          r"|\b(?:is|are) mine\b|\bI (?:read|calculated|computed|estimated|derived|inferred|fill|filled)\b|\bin hindsight\b"
          r"|\bnot (?:stated|a number|given|printed|from) in (?:the|this) paper\b|\bnot from (?:the|this) paper\b"
          r"|\((?:illustrative|standard|external)\b[^)]*\)|\(the paper's\b[^)]*\)|\([^()]*\bnot\b[^()]*\b(?:the|this) paper\b[^()]*\)")
for m in list(re.finditer(HEADING, text)) + list(re.finditer(LABELS, text, re.I)):
    fails.append(f'label "{m[0]}" in "{text[max(0, m.start() - 30):m.end() + 20].strip()}"')
# A cited work's page written "p. N" is linked by the build to this paper's page N.
for m in re.finditer(r'\b(?:their|its) pp?\. \d+|\bSection [\d.]+ \(pp?\. \d+\)', text):
    fails.append(f'cited-work page "{m[0]}" is linked to this paper; write "page N"')

for m in re.finditer(r'<a class="ref" href="#[^"]+">(?:Parts?|Math|M) ?[\d.]+</a>\s*(?:to|and|&ndash;|–)\s*(?!<a)(?:M)?(\d+(?:\.\d+)?)\b', src):
    fails.append(f'range endpoint "{m[1]}" after "{re.sub(r"<[^>]+>", "", m[0])[:30]}" is not a link')

# 4. Page references: each claim runs from the previous sentence end or page reference to its own marker.
bounds = [m.end() for m in re.finditer(r'[.!?:¶](?=\s+[A-Z"(¶])|¶', text)]
stop = set('which their there these those about after before would could should paper model models guide shows other first using'.split())
checked = 0
last_end = 0
# A dropped qualifier: an absolute word in the guide where the closest source sentence hedges. Quoted words are skipped.
ABSOLUTE = r"\b(?:fails?|failed|never|always|cannot|can't|impossible|none|guarantees?|proves?|every|all)\b"
HEDGE = r"\b(?:in theory|in practice|may|might|seems?|some|often|usually|likely|suggests?|appears?|could|tends?|roughly|unclear)\b"
qualifiers = []
for m in re.finditer(r'\[(?:(?:p|pp)\.|§) ([\d–\-, ]+)\]', text):
    if web != m[0].startswith('[§'):
        fails.append(f'{m[0]}: ' + ('a web article has sections, not pages; cite [§ N]' if web else 'a paper has pages; cite [p. N]')); continue
    pages = set()
    for part in re.split(r',\s*', m[1]):
        r = [x.strip() for x in re.split(r'[–-]', part) if x.strip()]
        if r and all(x.isdigit() for x in r): pages.update(range(int(r[0]), int(r[-1]) + 1))
    if not pages: continue
    i = bisect.bisect_right(bounds, m.start()) - 1
    start = max(last_end, bounds[i] if i >= 0 else 0)
    seg = text[start:m.start()]; last_end = m.end(); checked += 1
    hay = ' '.join(page_text(p) for p in pages); hs = squash(hay)
    absolute = re.findall(ABSOLUTE, re.sub(r'"[^"]*"', ' ', seg), re.I)
    if absolute:
        seg_words = {w for w in re.findall(r'[a-z]{6,}', seg.lower()) if w not in stop}
        overlap = lambda s_: len(seg_words & set(re.findall(r'[a-z]{6,}', s_.lower())))
        best = max(re.split(r'(?<=[.!?])\s+', norm(hay)), key=overlap, default='')
        hedges = {h.lower() for h in re.findall(HEDGE, best, re.I)}
        kept = any(re.search(rf'\b{re.escape(h)}\b', seg, re.I) for h in hedges)   # the guide keeps the hedge, quoted or not
        if overlap(best) >= 2 and hedges and not kept and not any(re.search(rf'\b{re.escape(w)}\b', best, re.I) for w in absolute):
            qualifiers.append(f'{m[0]}: "{absolute[0]}" in "{seg.strip()[-70:]}", where the source hedges: "{best[:80]}"')
    where = ('§ ' if web else 'p. ') + str(min(pages)) + (f'-{max(pages)}' if len(pages) > 1 else '')
    img = re.search(r'\bImage (\d+)\s*$', seg) if web and text[m.end():m.end() + 1] == ':' else None
    if img:
        if image_sections.get(int(img[1])) not in pages: fails.append(f'Image {img[1]} is not in {where}')
        continue
    cap = re.search(rf'({LABEL})\s*$', seg) if text[m.end():m.end() + 1] == ':' else None
    if cap:
        if not re.search(re.escape(cap[1]) + caption_after(cap[1]), hay): fails.append(f'caption {cap[1]} is not on {where}')
        continue
    quotes = [q for q in re.findall(r'"([^"]{4,})"', seg)]
    if quotes:
        bad = [q for q in quotes if squash(q).strip('.') not in hs and squash(q)[:24] not in hs]
        if bad: fails.append(f'quote not on {where}: "{bad[0][:70]}"')
        continue
    nums = [n.replace(',', '') for n in re.findall(r'(?<![\w.])\d[\d,]*(?:\.\d+)?', seg) if n not in {str(p) for p in pages}]
    nums = [n for n in nums if len(n) > 1]
    if nums:
        hay_nums = set(x.replace(',', '') for x in re.findall(r'\d[\d,]*(?:\.\d+)?', hay))
        if not any(n in hay_nums for n in nums): fails.append(f'none of {nums[:4]} are on {where}: "{seg.strip()[-90:]}"')
        continue
    words = {w for w in re.findall(r'[a-z]{6,}', seg.lower()) if w not in stop}
    if words:
        found = sum(1 for w in words if w in hay.lower())
        if found / len(words) < 0.5: weak.append(f'{where} ({found}/{len(words)} words): "{seg.strip()[-90:]}"')

# 5. Number-reading rules: lines a person must read, because the wording may overstate a result. Quoted text is skipped.
reads = []
cap_free = re.sub(r'</(p|li|td|th|h2|h3|h4|div|figure)>', ' ¶ ', re.sub(r'</?a\b[^>]*>', '', re.sub(r'<div class="cap">.*?</div>', ' ', src, flags=re.S)))
rule_text = norm(html.unescape(re.sub(r'<[^>]+>', ' ', cap_free)))   # captions are the paper's words, copied verbatim
for raw in re.split(r'(?<=[.!?¶])\s+', rule_text):
    sent = re.sub(r'"[^"]*"', ' ', raw) if raw.count('"') % 2 == 0 else raw
    if re.search(r'\b\d+(?:\.\d+)?% (?:improvement|increase|gain|better|worse|drop|decrease)\b|\b(?:improves?|increases?|gains?) by (?:about |over )?\d+(?:\.\d+)?%', sent) and not re.search(r'points?|relative', sent):
        reads.append(f'percentage without "points" or "relative": "{sent.strip()[:90]}"')
    if re.search(r'\bsignificant(?:ly)?\b', sent, re.I) and not re.search(r't-test|p-value|p =|confidence interval|runs|standard deviation', sent, re.I):
        reads.append(f'"significant" with no test or repeated runs named: "{sent.strip()[:90]}"')
    if re.search(r'\bbest (?:score|result|value|model)\b', sent) and not re.search(r'higher is better|lower is better|bold', sent, re.I):
        reads.append(f'"best" with no metric direction: "{sent.strip()[:90]}"')

# 6. The overview diagram opens Part 1, and an intuition diagram comes before the math of its subsection. Both are
# images, so they cannot carry links or math: terms only.
ov = re.search(r'<img[^>]*src="([^"]*diagrams/gist\.svg)"', src)
p1 = re.search(r'id="p1"[^>]*>(.*?)(?:<h3|</section>)', src, re.S)
if not ov: fails.append('no overview diagram: draw diagrams/gist.svg and place it at the top of Part 1')
elif not p1 or ov[0] not in p1[1]: fails.append('the overview diagram is not at the top of Part 1, before its first subsection')
for d in re.finditer(r'<img[^>]*src="([^"]*diagrams/(?:gist|intuition-[\w-]+)\.svg)"', src):
    svg = os.path.join(os.path.dirname(os.path.abspath(guide_path)), d[1])
    labels = ' '.join(re.findall(r'<tspan[^>]*>([^<]*)</tspan>', open(svg, encoding='utf-8').read())) if os.path.exists(svg) else ''
    bad = re.findall(r'\b(?:Math|Part|Section|Figure|Table|Eq\.?|Appendix)\s?\d+|[α-ωΣ∑_^]', labels)
    if not labels: fails.append(f'{d[1]} has no text labels')
    elif bad: fails.append(f'{d[1]} has math or section labels, which an image cannot link: {sorted(set(bad))[:5]}')
    if 'intuition-' in d[1] and re.search(r'<h4[^>]*>\s*Math \d', src[src.rfind('<h3', 0, d.start()):d.start()]):
        fails.append(f'{d[1]} comes after the math of its subsection; place it before the first Math box')

# 7. The reader sees no page reference to the source: every link to a source page sits inside a hidden page marker.
for m in re.finditer(r'<a class="pg" href="[^"]*">([^<]*)</a>', re.sub(r'<span class="srcref">[\s\S]*?</span>', '', src)):
    fails.append(f'"{m[1]}": a page reference the reader can see; write it as a bracketed [p. N] or [§ N] marker, which the build hides')

print(f'anchors {len(ids)} | parts {sorted(parts, key=int)} | sections {len(sections)} | Math {sorted(maths, key=int)} | M1-M{max(map(int, metrics)) if metrics else 0} | page refs checked {checked}')
print(f'FAIL: {len(fails)}'); [print('  FAIL', f) for f in fails]
print(f'WEAK: {len(weak)}'); [print('  WEAK', w) for w in weak]
if partial: print(f'PENDING (parts not built yet): {len(pending)}'); [print('  PENDING', p_) for p_ in pending]
reads += [f'dropped qualifier? {q}' for q in qualifiers]
print(f'READ (number wording and qualifiers to confirm by hand): {len(reads)}'); [print('  READ', r) for r in reads]
sys.exit(1 if fails else 0)
