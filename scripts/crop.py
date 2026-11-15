"""Crop figures and tables from a paper PDF, trimmed to their ink.

Usage: python3 -I crop.py PAPER.pdf MANIFEST.json OUT_DIR [DPI]
MANIFEST is a list of {"id": "fig3_1", "page": 11, "box": [x0, y0, x1, y1]} in PDF points, top-left origin.
Make each box loose: below or above the caption (captions sit on either side), clear of body text.
A crop whose ink touches its box edge is probably clipped; widen that box and run again. Exit code 1 if any does.
"""
import json, re, subprocess, sys, tempfile, os
pdf, manifest, out_dir = sys.argv[1:4]; dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 400
PAD, INK, s = 14, 235, dpi / 72
os.makedirs(out_dir, exist_ok=True); clipped = []
with tempfile.TemporaryDirectory() as tmp:
    for item in json.load(open(manifest)):
        x0, y0, x1, y1 = [round(v * s) for v in item['box']]
        base = [str(a) for a in ('-f', item['page'], '-l', item['page'], '-r', dpi, '-x', x0, '-y', y0, '-W', x1 - x0, '-H', y1 - y0)]
        subprocess.run(['pdftoppm', *base, '-gray', '-singlefile', pdf, f'{tmp}/g'], check=True)
        raw = open(f'{tmp}/g.pgm', 'rb').read(); m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+\d+\s', raw)
        w, h = int(m[1]), int(m[2]); px = raw[m.end():]; dark = re.compile(rb'[\x00-' + bytes([INK]) + rb']')
        top = bot = None; left, right = w, -1
        for r in range(h):
            row = px[r * w:(r + 1) * w]; f = dark.search(row)
            if not f: continue
            top = r if top is None else top; bot = r; left = min(left, f.start()); right = max(right, w - 1 - dark.search(row[::-1]).start())
        if top is None: sys.exit(f"{item['id']}: no ink in its box")
        cx, cy = max(0, left - PAD), max(0, top - PAD); cw, ch = min(w, right + PAD) - cx, min(h, bot + PAD) - cy
        subprocess.run(['pdftoppm', '-png', '-singlefile', '-f', str(item['page']), '-l', str(item['page']), '-r', str(dpi), '-x', str(x0 + cx), '-y', str(y0 + cy),
                        '-W', str(cw), '-H', str(ch), pdf, os.path.join(out_dir, item['id'])], check=True)
        edge = top == 0 or bot == h - 1 or left == 0 or right == w - 1
        if edge: clipped.append(item['id'])
        print(f"{item['id']:9} p{item['page']:<3} {cw}x{ch}px  {'TOUCHES BOX EDGE' if edge else 'ok'}")
sys.exit(1 if clipped else 0)
