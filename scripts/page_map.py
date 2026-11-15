"""Print a compact layout map of one PDF page, to choose crop boxes for figures and tables.

Usage: python3 -I page_map.py PAPER.pdf PAGE
Runs of full-width body text collapse to one BODY line; other lines print with their box in PDF points (top-left origin).
Uses pdftotext -tsv, because -bbox crashes on some poppler versions.
"""
import csv, io, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from labels import LABEL, caption_after
pdf, page = sys.argv[1], sys.argv[2]
tsv = subprocess.run(['pdftotext', '-f', page, '-l', page, '-tsv', pdf, '-'], capture_output=True, text=True).stdout
lines = {}
for r in csv.DictReader(io.StringIO(tsv), delimiter='\t', quoting=csv.QUOTE_NONE):
    if r['level'] != '5': continue
    k = (r['block_num'], r['par_num'], r['line_num'])
    x0, y0 = float(r['left']), float(r['top']); x1, y1 = x0 + float(r['width']), y0 + float(r['height'])
    ln = lines.setdefault(k, [x0, y0, x1, y1, []])
    ln[0], ln[1], ln[2], ln[3] = min(ln[0], x0), min(ln[1], y0), max(ln[2], x1), max(ln[3], y1); ln[4].append(r['text'])
merged = []
for l in sorted(lines.values(), key=lambda l: (round(l[1]), l[0])):
    if merged and abs(merged[-1][1] - l[1]) < 3:
        m = merged[-1]; m[0] = min(m[0], l[0]); m[2] = max(m[2], l[2]); m[3] = max(m[3], l[3]); m[4] += l[4]
    else:
        merged.append(l[:4] + [list(l[4])])
xs = [l[2] for l in merged] or [1]; full = max(xs)
run = None
for x0, y0, x1, y1, ws in merged:
    t = ' '.join(ws)
    if x1 - x0 > 0.8 * (full - min(l[0] for l in merged)) and not re.match(LABEL, t):
        run = [y0, y1] if run is None else [run[0], y1]; continue
    if run: print(f'  BODY {run[0]:.0f}-{run[1]:.0f}'); run = None
    print(f'  {y0:5.0f}-{y1:3.0f} x{x0:3.0f}-{x1:3.0f} {t[:50]}')
if run: print(f'  BODY {run[0]:.0f}-{run[1]:.0f}')
