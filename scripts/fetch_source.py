"""Fetch a paper's arXiv TeX source and list its displayed equations and its tables, in full.

Usage: python3 -I fetch_source.py ARXIV_ID_WITH_VERSION OUT_DIR
For example 1706.03762v7. Downloads arxiv.org/e-print/<id> into OUT_DIR/src and writes OUT_DIR/equations.json and
OUT_DIR/tables.json (every item complete, with its file, line, environment and \\label, and for a table its caption),
in document order, plus OUT_DIR/review.txt with math or table-like environments this script does not parse and the
files the main document does not include, for a person to check. Only included files are parsed. Nothing is truncated.
Limits: 50 MB download, 2,000 archive members, 20 MB per member, 200 MB unpacked. Members that would land outside
OUT_DIR/src (absolute paths, "..", links, devices) or that repeat a path are refused. The PDF stays the authority for
page numbers. Exit code 3 when arXiv has no TeX source, 4 when a limit is exceeded.
"""
import gzip, io, json, os, re, sys, tarfile, urllib.request
MAX_DOWNLOAD, MAX_MEMBERS, MAX_MEMBER, MAX_TOTAL = 50 << 20, 2000, 20 << 20, 200 << 20
arxiv, out = sys.argv[1], sys.argv[2]
if not re.search(r'v\d+$', arxiv): sys.exit('give the arXiv ID with its version, for example 1706.03762v7')
src_dir = os.path.join(out, 'src'); os.makedirs(src_dir, exist_ok=True); root = os.path.realpath(src_dir)
def capped_read(f, cap, what):
    chunks, size = [], 0
    while True:
        b = f.read(1 << 20)
        if not b: return b''.join(chunks)
        size += len(b)
        if size > cap: print(f'limit exceeded: {what} is over {cap >> 20} MB'); sys.exit(4)
        chunks.append(b)
with urllib.request.urlopen(urllib.request.Request(f'https://arxiv.org/e-print/{arxiv}', headers={'User-Agent': 'research-paper-distilled'}), timeout=120) as r:
    raw = capped_read(r, MAX_DOWNLOAD, 'the download')
if raw[:4] == b'%PDF': print('arXiv has no TeX source for this paper (it serves only the PDF)'); sys.exit(3)
data = capped_read(gzip.GzipFile(fileobj=io.BytesIO(raw)), MAX_TOTAL, 'the unpacked archive') if raw[:2] == b'\x1f\x8b' else raw
seen, total = set(), 0
try:
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        members = tar.getmembers()
        if len(members) > MAX_MEMBERS: print(f'limit exceeded: {len(members)} archive members'); sys.exit(4)
        for m in members:
            target = os.path.realpath(os.path.join(src_dir, m.name))
            if not target.startswith(root + os.sep) or m.issym() or m.islnk() or m.isdev() or target in seen:
                print(f'refused: {m.name}'); continue
            if not m.isfile(): continue
            if m.size > MAX_MEMBER: print(f'refused (over {MAX_MEMBER >> 20} MB): {m.name}'); continue
            total += m.size
            if total > MAX_TOTAL: print('limit exceeded: unpacked size'); sys.exit(4)
            seen.add(target); os.makedirs(os.path.dirname(target), exist_ok=True)
            with tar.extractfile(m) as f, open(target, 'wb') as g: g.write(capped_read(f, MAX_MEMBER, m.name))
except tarfile.ReadError:
    open(os.path.join(src_dir, 'main.tex'), 'wb').write(data)   # a single gzipped .tex file
EQ_ENVS = r'equation\*?|align\*?|alignat\*?|flalign\*?|eqnarray\*?|gather\*?|multline\*?|displaymath|split'
TAB_ENVS = r'tabular\*?|tabularx|tabulary|longtable|array'
eq_re = re.compile(rf'\\begin\{{({EQ_ENVS})\}}(.*?)\\end\{{\1\}}|\\\[(.*?)\\\]|\$\$(.*?)\$\$', re.S)
tab_re = re.compile(rf'\\begin\{{({TAB_ENVS})\}}(.*?)\\end\{{\1\}}', re.S)
other_re = re.compile(r'\\begin\{([A-Za-z*]+)\}(.*?)\\end\{\1\}', re.S)
eqs, tabs, review = [], [], []
inc_re = re.compile(r'\\(?:input|include|subfile)\{([^}]+)\}')
blank = lambda m: '\n' * m[0].count('\n')   # keep line numbers when a block is removed
def load(rel):
    tex = re.sub(r'(?<!\\)%.*', '', open(os.path.join(src_dir, rel), encoding='utf-8', errors='replace').read())
    tex = re.sub(r'\\iffalse\b.*?\\fi\b', blank, tex, flags=re.S)
    return re.sub(r'\\begin\{comment\}.*?\\end\{comment\}', blank, tex, flags=re.S)
def resolve(name, frm):
    name = name.strip() if name.strip().endswith('.tex') else name.strip() + '.tex'
    for base in (src_dir, os.path.join(src_dir, os.path.dirname(frm))):
        path = os.path.realpath(os.path.join(base, name))
        if path.startswith(root + os.sep) and os.path.isfile(path): return os.path.relpath(path, src_dir)
    return None
def caption_of(tex, pos):
    """The caption and label of the table or figure float around a tabular, so it can be matched to the PDF."""
    b = tex.rfind('\\begin{table', 0, pos)
    if b < 0 or tex.rfind('\\end{table', 0, pos) > b: return None, None
    e = tex.find('\\end{table', pos); float_tex = tex[b:e if e > 0 else len(tex)]
    cap, lab = re.search(r'\\caption\{(.{0,140})', float_tex, re.S), re.search(r'\\label\{([^}]*)\}', float_tex)
    return (re.sub(r'\s+', ' ', cap[1]).strip() if cap else None), (lab[1] if lab else None)
def parse(rel, visited):
    """Read one file in document order, descending into each \input where it appears."""
    if rel in visited: return
    visited.add(rel); tex = load(rel)
    line = lambda pos: tex.count('\n', 0, pos) + 1
    events = sorted([(m.start(), 'inc', m) for m in inc_re.finditer(tex)] + [(m.start(), 'eq', m) for m in eq_re.finditer(tex)] +
                    [(m.start(), 'tab', m) for m in tab_re.finditer(tex)] + [(m.start(), 'other', m) for m in other_re.finditer(tex)], key=lambda e: e[0])
    for pos, kind, m in events:
        if kind == 'inc':
            child = resolve(m[1], rel)
            if child: parse(child, visited)
            else: review.append(f'{rel}:{line(pos)} includes "{m[1]}", which is not in the source archive')
        elif kind == 'eq':
            body = (m[2] or m[3] or m[4] or '').strip(); label = re.search(r'\\label\{([^}]*)\}', body)
            eqs.append({'file': rel, 'line': line(pos), 'env': m[1] or ('\\[' if m[3] is not None else '$$'), 'label': label[1] if label else None, 'tex': body})
        elif kind == 'tab':
            rows = [re.sub(r'\s+', ' ', r).strip() for r in re.split(r'\\\\', m[2]) if r.strip()]
            cap, lab = caption_of(tex, pos)
            tabs.append({'file': rel, 'line': line(pos), 'env': m[1], 'caption': cap, 'label': lab, 'rows': rows})
        elif not re.fullmatch(rf'{EQ_ENVS}|{TAB_ENVS}|table\*?|figure\*?|document|abstract|itemize|enumerate|center|minipage|description|quote', m[1]):
            if '&' in m[2] and '\\\\' in m[2]: review.append(f'{rel}:{line(pos)} unparsed environment "{m[1]}" with table- or math-like rows')
# Only the files the main document includes reach the PDF: an archive often keeps drafts and commented-out sections.
all_tex = sorted(os.path.relpath(os.path.join(d, f), src_dir) for d, _, fs in os.walk(src_dir) for f in fs if f.endswith('.tex'))
mains = [r for r in all_tex if re.search(r'\\documentclass', load(r))]
visited = set()
if mains:
    parse(sorted(mains, key=lambda r: ('\\begin{document}' not in load(r), r))[0], visited)
    for r in all_tex:
        if r not in visited: review.append(f'{r}: not included by the main document, so not in the PDF; not parsed')
else:
    review.append('no file has \\documentclass; parsed every .tex file, so some items may not be in the PDF')
    for r in all_tex: parse(r, visited)
json.dump(eqs, open(os.path.join(out, 'equations.json'), 'w'), indent=1)
json.dump(tabs, open(os.path.join(out, 'tables.json'), 'w'), indent=1)
open(os.path.join(out, 'review.txt'), 'w').write('\n'.join(review) + ('\n' if review else ''))
print(f'{arxiv}: {len(eqs)} displayed equations, {len(tabs)} tables, {len(review)} environments to review by hand')
