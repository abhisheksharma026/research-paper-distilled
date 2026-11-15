"""Check every number, quote and derived value in a guide against its exact source in the paper.

Usage: python3 -I check_claims.py LEDGER.json PAPER.pdf PAGES_DIR
LEDGER is a list of claims, each one of:
  {"phrase": "achieves 28.4 BLEU", "page": 1}                               the words are on that page
                                                                               (for a web article, "section": N)
  {"cell": {"caption": "Table 2:", "row": "Transformer (big)", "col": 0, "nth": 0}, "value": "28.4"}
                                                                               the table cell holds the value
                                                                               (optional "side": "above" or "below")
  {"calc": "round(28.4 - 26.36, 2)", "value": 2.04}                           a derived number recomputes
                                     (numbers, + - * / ** %, round abs min max sqrt log log10 exp sin cos tan, pi e; nothing else runs)
PAGES_DIR is the output of extract_pages.py. Phrases match after Unicode NFC and whitespace normalization, in either
the plain or the layout text. A cell is read from the layout text next to its caption, above it first and then below it: "row"
starts the line, cells are split on runs of 2+ spaces, "nth" picks among matching rows (0 = nearest the caption). Exit code 1 on a failure.
"""
import json, math, re, sys, unicodedata
import ast, operator
# A calculation is arithmetic on numbers only: no names except the functions below, no attributes, no subscripts.
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {'round': round, 'abs': abs, 'min': min, 'max': max, 'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10, 'exp': math.exp,
          'sin': math.sin, 'cos': math.cos, 'tan': math.tan}
_CONSTS = {'pi': math.pi, 'e': math.e}
def safe_calc(expr):
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool): return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS: return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS: return _OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Name) and n.id in _CONSTS: return _CONSTS[n.id]
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and not n.keywords:
            return _FUNCS[n.func.id](*[ev(a) for a in n.args])
        raise ValueError(f'not allowed in a calculation: {ast.dump(n)[:60]}')
    return ev(ast.parse(expr.replace('math.', ''), mode='eval'))
ledger, pdf, pages = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
import hashlib as _h, json as _j, os as _o
def _pin(pdf, pages_dir):
    pin = _o.path.join(pages_dir, 'paper.json')
    if _o.path.exists(pin) and _h.sha256(open(pdf, 'rb').read()).hexdigest() != _j.load(open(pin))['sha256']:
        sys.exit(f'{pdf} is not the pinned paper in {pin}: a different version changes every page number')
_pin(pdf, pages)
norm = lambda t: unicodedata.normalize('NFC', re.sub(r'\s+', ' ', t))
def page(p, layout=False):
    return open(f'{pages}/{p}{".layout" if layout else ""}.txt', encoding='utf-8').read()
layout_all = [(p, page(p, True).split('\n')) for p in sorted(int(f.split('.')[0]) for f in __import__('os').listdir(pages) if f.endswith('.layout.txt'))]
ok = bad = 0
for c in ledger:
    if 'phrase' in c:
        pg = c.get('page', c.get('section'))   # a web article's sections stand in for pages ("section": N)
        hay = norm(page(pg) + ' ' + page(pg, True)); good = norm(c['phrase']) in hay; what = ('§ ' if 'section' in c else 'p. ') + f'{pg} has "{c["phrase"][:60]}"'
    elif 'cell' in c:
        cell = c['cell']; good, found = False, None
        for p, lines in layout_all:
            idx = [i for i, l in enumerate(lines) if l.strip().startswith(cell['caption'])]
            if not idx: continue
            # Captions sit above or below their table: search above first (nearest line first), then below.
            above = [l for l in reversed(lines[max(0, idx[0] - 25):idx[0]]) if l.strip().startswith(cell['row'])]
            below = [l for l in lines[idx[0] + 1:idx[0] + 41] if l.strip().startswith(cell['row'])]
            rows = {'above': above, 'below': below}.get(cell.get('side'), above if len(above) > cell.get('nth', 0) else below)
            if len(rows) > cell.get('nth', 0):
                cells = re.split(r'\s{2,}', rows[cell.get('nth', 0)].strip())[1:]
                found = re.sub(r'[a-z+*]+$', '', cells[cell['col']]) if cell['col'] < len(cells) else None
                good = found == c['value']; break
        what = f'{cell["caption"]} row "{cell["row"]}" col {cell["col"]}: want {c["value"]}, found {found}'
    else:
        try:
            value = safe_calc(c['calc']); good = value == c['value']; what = f'calc {c["calc"]} = {value}, want {c["value"]}'
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as e:
            good, what = False, f'calc refused: {c["calc"][:60]} ({e})'
    ok += good; bad += not good
    if not good: print('FAIL', what)
print(f'{ok} ok, {bad} failed'); sys.exit(1 if bad else 0)
