"""Compare a rewritten guide part with its original: what a voice or structure rewrite must keep.

Usage: python3 -I check_rewrite.py OLD.html NEW.html   (see references/rewrite.md)
A part split across files (a section that opens in one file and closes in the next) reports an unbalanced tag; check
the joined files instead (cat the parts in build order, old and new, and compare the two joined files).
FAIL (exit 1) when the new part:
  - drops or changes any formula (<math>), table, figure, image, <pre>, include marker, caption (div.cap) or
    dataset item (div.ex), or changes the sequence of h2/h3/h4 headings or section ids;
  - loses any [p. N] reference, any quoted passage, or any number that the old prose states;
  - has unbalanced div, ul, ol, section or table tags, or contains a banned label ("my calculation", "How to read").
WARN for numbers or page references that only the new part has, and for page references cited fewer times.
"""
import collections, html, re, sys

old_src, new_src = (open(p, encoding='utf-8').read() for p in sys.argv[1:3])
fails, warns = [], []
FIXED = [r'<math\b.*?</math>', r'<table\b.*?</table>', r'<figure\b.*?</figure>', r'<img\b[^>]*>', r'<pre\b.*?</pre>',
         r'<!--include:[^>]*-->', r'<div class="cap"[^>]*>.*?</div>', r'<div class="ex"[^>]*>.*?</div>']

def blocks(src, rx):
    return collections.Counter(re.findall(rx, src, re.S))

for rx in FIXED:
    lost = blocks(old_src, rx) - blocks(new_src, rx)
    for b in lost.elements():
        fails.append(f'fixed block changed or dropped: {re.sub(r"<[^>]+>", " ", b)[:90].strip() or b[:90]}')

heads = lambda s: re.findall(r'<h[234][^>]*>.*?</h[234]>', s, re.S)
if heads(old_src) != heads(new_src):
    o, n = heads(old_src), heads(new_src)
    diff = [x for x in o if x not in n] + [f'(new) {x}' for x in n if x not in o]
    fails.append(f'heading sequence changed: {diff[:4]}')
if re.findall(r'<section[^>]*id="([^"]+)"', old_src) != re.findall(r'<section[^>]*id="([^"]+)"', new_src):
    fails.append('section ids changed')

def prose(src):
    for rx in FIXED:
        src = re.sub(rx, ' ', src, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', src))

old_t, new_t = prose(old_src), prose(new_src)
pref = lambda t: collections.Counter(re.findall(r'\[pp?\. [^\]]+\]', t))
op, np_ = pref(old_t), pref(new_t)
for r in sorted(set(op) - set(np_)):
    fails.append(f'page reference lost: {r}')
for r in sorted(k for k in op if k in np_ and np_[k] < op[k]):
    warns.append(f'page reference {r} cited {np_[r]} times, was {op[r]}')
for r in sorted(set(np_) - set(op)):
    warns.append(f'new page reference: {r}')

norm_q = lambda t: t.replace('“', '"').replace('”', '"')
# Pair every quote mark first, then drop the short ones: a minimum length inside the pattern mis-pairs every later mark.
quotes = lambda t: set(q.strip() for q in re.findall(r'"([^"]*)"', norm_q(t)) if len(q.strip()) >= 4)
for q in sorted(quotes(old_t) - quotes(new_t)):
    if norm_q(q) not in norm_q(new_t):
        fails.append(f'quote lost or altered: "{q[:80]}"')

nums = lambda t: collections.Counter(re.findall(r'(?<![\w.])\d+(?:[.,]\d+)*%?', t))
on, nn = nums(old_t), nums(new_t)
for n in sorted(set(on) - set(nn)):
    fails.append(f'number lost from the prose: {n}')
for n in sorted(set(nn) - set(on)):
    warns.append(f'number only in the new prose: {n}')

for tag in ('div', 'ul', 'ol', 'section', 'table', 'p'):
    a, b = len(re.findall(rf'<{tag}\b', new_src)), len(re.findall(rf'</{tag}>', new_src))
    if a != b: fails.append(f'unbalanced <{tag}>: {a} opened, {b} closed')
for m in re.finditer(r'\bmy (?:calculation|reading|wording|assessment)\b|\bHow to read (?:this|these|it)\b|\b(?:is|are) mine\b|not stated in the paper|\(illustrative\)', new_t):
    fails.append(f'banned label: "{m[0]}"')

wc = lambda t: len(t.split())
for name, src in (('old', old_src), ('new', new_src)):
    for m in re.finditer(r'<div class="answer"[^>]*>(.*?)<p class="wc"', src, re.S):
        print(f'{name} answer words: {len(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<h4>.*?</h4>", " ", m[1], flags=re.S))).split())}')
print(f'prose words: old {wc(old_t)}, new {wc(new_t)} ({(wc(new_t) - wc(old_t)) / max(wc(old_t), 1):+.0%})')
for w in warns: print('WARN', w)
for f in fails: print('FAIL', f)
print(f'{len(fails)} FAIL, {len(warns)} WARN'); sys.exit(1 if fails else 0)
