"""Rank a paper's references by how much the paper itself relies on them, to choose the key references.

Usage: python3 -I key_refs.py PAGES_DIR [TOP]
PAGES_DIR is the output of extract_pages.py. Detects the citation style (numbered brackets such as [38], author keys
such as [RWC+ 19], or author-year such as (Devlin et al., 2019) and Devlin et al. (2019)), counts each cited work in the
text outside the reference list, records the pages it appears on, takes its entry from the paper's own reference list,
and prints the TOP candidates (default 20) with one citing sentence each. This only ranks: decide each reference's
role, then read the chosen work before writing its bullet. Exit code 2 when the style cannot be ranked automatically.
"""
import json, os, re, sys, unicodedata
pages_dir = sys.argv[1]; top = int(sys.argv[2]) if len(sys.argv) > 2 else 20
def stop(msg): print(msg); sys.exit(2)
try:
    n = json.load(open(os.path.join(pages_dir, 'paper.json')))['pages']
except (OSError, KeyError, ValueError):
    stop('run extract_pages.py first: PAGES_DIR has no paper.json')
text = {p: unicodedata.normalize('NFC', open(os.path.join(pages_dir, f'{p}.txt'), encoding='utf-8').read()) for p in range(1, n + 1)}
flat = {p: re.sub(r'\s+', ' ', t) for p, t in text.items()}

KEY = r'[A-Z][A-Za-z]{1,6}\+?\s?\d{2}[a-z]?'
NAME = r"[A-Z][A-Za-z'’\-]+(?: (?:et al\.|and [A-Z][A-Za-z'’\-]+))?"
styles = {
    'numbered': re.compile(r'\[(\d+(?:\s*[,–-]\s*\d+)*)\]'),
    'author key': re.compile(rf'\[((?:{KEY})(?:\s*,\s*(?:{KEY}))*)\]'),
    'author-year': re.compile(rf'\(((?:{NAME},? \d{{4}}[a-z]?)(?:\s*;\s*{NAME},? \d{{4}}[a-z]?)*)\)|({NAME}) \((\d{{4}}[a-z]?)\)'),
}
# The reference list starts at its heading, which may carry a section number or print in split small caps
# ("V. R EFERENCES"), and runs over the following pages where most lines look like entries. The heading page is
# split at the heading, because the text often ends on the page where the list starts.
HEAD = re.compile(r'(?m)^[ \t]*(?:[IVX\d]+\.?[ \t]+)?(?:References|R ?EFERENCES|Bibliography|B ?IBLIOGRAPHY)[ \t]*$')
head = next(((p, m.end()) for p in range(1, n + 1) for m in [HEAD.search(text[p])] if m), None)
ref_pages, ref_parts = [], []
if head:
    hp, at = head
    flat[hp], tail = re.sub(r'\s+', ' ', text[hp][:at]), re.sub(r'\s+', ' ', text[hp][at:])
    ref_pages.append(hp); ref_parts.append(tail)
    for p in range(hp + 1, n + 1):
        lines = [l for l in text[p].split('\n') if l.strip()]
        entryish = sum(bool(re.search(r'^\s*\[|\b(19|20)\d{2}[a-z]?\b', l)) for l in lines)
        if not (lines and entryish / len(lines) > 0.3): break
        ref_pages.append(p); ref_parts.append(flat[p])
body = [p for p in range(1, n + 1) if p not in ref_pages[1:]]
found = {name: sum(len(rx.findall(flat[p])) for p in body) for name, rx in styles.items()}
style = max(found, key=found.get)
if found[style] < 5:
    stop('Could not rank this citation style automatically. Rank references manually from citation locations.')

SURNAME, YEAR, SEMI = r"[A-Z][A-Za-z'’\-]+", r'\d{4}[a-z]?', r'\s*;\s*'
def keys_of(m):
    if style == 'numbered':
        out = []
        for part in re.split(r'\s*,\s*', m[1]):
            a = re.split(r'\s*[–-]\s*', part)
            out += [str(i) for i in range(int(a[0]), int(a[-1]) + 1)] if len(a) == 2 and a[0].isdigit() and a[1].isdigit() else [part]
        return out
    if style == 'author key':
        return [re.sub(r'\s', '', k) for k in re.split(r'\s*,\s*', m[1])]
    surname = lambda c: re.match(SURNAME, c.strip())[0]
    year = lambda c: re.search(YEAR, c)[0]
    if m[1]:
        return [surname(c) + ' ' + year(c) for c in re.split(SEMI, m[1])]
    return [surname(m[2]) + ' ' + m[3]]
counts, where, sample = {}, {}, {}
for p in body:
    for m in styles[style].finditer(flat[p]):
        for k in keys_of(m):
            counts[k] = counts.get(k, 0) + 1; where.setdefault(k, set()).add(p)
            if k not in sample:
                s = flat[p].rfind('. ', 0, m.start()); sample[k] = flat[p][s + 2 if s >= 0 else 0:m.end() + 60]
refs_text = ' '.join(ref_parts)
def entry(k):
    if style == 'author-year':
        surname, year = k.split(' ')
        for m in re.finditer(r'\b' + re.escape(surname) + r'\b', refs_text):
            first_year = re.search(r'\b(?:19|20)\d{2}[a-z]?\b', refs_text[m.end():m.end() + 300])
            if first_year and first_year[0] == year:
                return refs_text[m.start():m.start() + 160]
        return None
    pat = re.escape(k) if style == 'numbered' else re.escape(k).replace('\\+', '\\+\\s?')
    m = re.search(r'\[' + pat + r'\]\s*([^\[]{0,200})', refs_text)
    if not m and style == 'author key':
        m = re.search(r'\[' + re.escape(k[:-2]) + r'\s?' + re.escape(k[-2:]) + r'\]\s*([^\[]{0,200})', refs_text)
    return m[1] if m else None
ranked = sorted(counts, key=lambda k: (counts[k], len(where[k])), reverse=True)
print(f'style: {style}; {len(counts)} cited works in the text; reference list on pp. {min(ref_pages) if ref_pages else "?"}-{max(ref_pages) if ref_pages else "?"}')
for i, k in enumerate(ranked[:top], 1):
    pg = sorted(where[k]); span = f'pp. {pg[0]}-{pg[-1]}' if len(pg) > 1 else f'p. {pg[0]}'
    print(f'{i:2}. [{k}] cited {counts[k]}x on {len(pg)} pages ({span}) | {(entry(k) or "(entry not found in the reference list)")[:90]}')
    print(f'      "{sample[k][-150:]}"')
