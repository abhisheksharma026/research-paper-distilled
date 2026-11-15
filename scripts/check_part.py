"""Check one guide part in a single call: crops, diagrams, Markdown conversion, images and the claims ledger.

Usage: python3 -I check_part.py WORK/parts/NAME.md PAPER.pdf
       python3 -I check_part.py WORK/parts/NAME.md WORK/web/source.html   (a web article: its pages are WORK/web/pages)
It converts the part to WORK/parts/NAME.html and takes the images it shows from that HTML, so every image syntax counts.
Each figures/X.png must be an entry in some WORK/crops*.json, and every manifest holding one passes crop.py's clip check:
WORK/crops-NAME.json crops into figures/, any other manifest into a temporary folder. Each diagrams/X.svg is rendered
again from WORK/diagrams/X.mmd and checked by diagram.py on every run. Then WORK/ledger-NAME.json runs through
check_claims.py. Every step runs even after a failure; it prints only the failures, then one summary line. Exit 1 on any
failure, including a child script that stops without a message.
"""
import glob, html, json, os, re, subprocess, sys, tempfile
part, pdf = os.path.abspath(sys.argv[1]), sys.argv[2]
name = os.path.splitext(os.path.basename(part))[0]
work = os.path.dirname(os.path.dirname(part)); guide = os.path.dirname(work); here = os.path.dirname(os.path.abspath(__file__))
fails, done = [], []
def run(script, *args):
    """Run a skill script; a nonzero exit is always a failure, with its exit code when it printed nothing."""
    r = subprocess.run([sys.executable, '-I', os.path.join(here, script), *args], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    return r.returncode, out or (f'{script} exited {r.returncode} with no message' if r.returncode else '')

code, out = run('md_part.py', part, part[:-3] + '.html')
if code: fails.append(f'conversion: {out}'); shown = []
else:
    # Raw HTML passes through the converter unchanged, so a src may be double-quoted, single-quoted or bare.
    srcs = [a or b or c for a, b, c in re.findall(r'''<img\b[^>]*?\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''',
                                                  open(part[:-3] + '.html', encoding='utf-8').read())]
    shown = sorted({os.path.normpath(html.unescape(s)) for s in srcs if not re.match(r'[a-z]+:', s)})

figures = [s for s in shown if s.startswith('figures/')]
manifests = {}
for m in sorted(glob.glob(os.path.join(work, 'crops*.json'))):
    try: manifests[m] = [i['id'] for i in json.load(open(m))]
    except (ValueError, KeyError, TypeError) as e: manifests[m] = None; bad = f'{os.path.basename(m)}: not a crop manifest ({e})'
    if manifests[m] is None and m.endswith(f'crops-{name}.json'): fails.append(bad)
own = os.path.join(work, f'crops-{name}.json')
ids = {os.path.splitext(os.path.basename(f))[0] for f in figures}
for f in figures:
    if not any(ids_ and os.path.splitext(os.path.basename(f))[0] in ids_ for ids_ in manifests.values()):
        fails.append(f'{f}: no entry in any crops*.json, so its crop is unchecked')
with tempfile.TemporaryDirectory() as tmp:
    for m, ids_ in manifests.items():
        if ids_ is None or m != own and not ids & set(ids_): continue
        code, out = run('crop.py', pdf, m, os.path.join(guide, 'figures') if m == own else tmp)
        clipped = [l for l in out.splitlines() if 'TOUCHES BOX EDGE' in l and (m == own or l.split()[0] in ids)]
        fails += [f'{os.path.basename(m)}: {l}' for l in clipped]
        if code and not any('TOUCHES BOX EDGE' in l for l in out.splitlines()): fails.append(f'{os.path.basename(m)}: {out}')
done.append(f'{len(figures)} crops')

diagrams = [s for s in shown if s.startswith('diagrams/') and s.endswith('.svg')]
for svg in diagrams:
    src = os.path.join(work, 'diagrams', os.path.basename(svg)[:-4] + '.mmd')
    if not os.path.exists(src): fails.append(f'{svg}: no source {src}'); continue
    code, out = run('diagram.py', src, os.path.join(guide, svg))
    if code: fails.append(f'{svg}: {out}')
done.append(f'{len(diagrams)} diagrams')
fails += [f'{p}: shown in the part but missing' for p in shown if not os.path.exists(os.path.join(guide, p))]

ledger = os.path.join(work, f'ledger-{name}.json')
if not os.path.exists(ledger): fails.append(f'no claims ledger {ledger}')
else:
    pages = os.path.join(os.path.dirname(os.path.abspath(pdf)), 'pages') if pdf.endswith('.html') else os.path.join(work, 'pages')
    code, out = run('check_claims.py', ledger, pdf, pages)
    lines = out.splitlines()
    if code: fails += [l for l in lines if l.startswith('FAIL')] + [lines[-1]]
    done.append(lines[-1] if lines else 'ledger ran')

print('\n'.join(fails) if fails else f'{name}: ok ({", ".join(done)})')
sys.exit(1 if fails else 0)
