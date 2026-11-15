"""Render a Mermaid diagram to SVG for a guide, using the installed Chrome.

Usage: python3 -I diagram.py DIAGRAM.mmd OUT.svg
Runs @mermaid-js/mermaid-cli 12.0.0 through npx (fetched once into the npm cache; Puppeteer's own browser download is
skipped). Labels are plain SVG text, so the file renders inside an <img>, in the guide's font. Needs Node and Chrome.
It supplies the guide's shared classes (kept, changed, problem, new, part, ext, boundary): see CLASSES below.
Exit code 1 when rendering fails, the SVG has no text labels, or its labels print below 7 pt at full column width.
"""
import json, os, re, shutil, subprocess, sys, tempfile
src, out = sys.argv[1], sys.argv[2]
def find_chrome():
    """Chrome or Chromium: $CHROME_PATH, then the macOS app, then common command names."""
    for c in (os.environ.get('CHROME_PATH'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        if c and os.path.exists(c): return c
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        if shutil.which(name): return shutil.which(name)
    sys.exit('Chrome or Chromium not found: install Google Chrome, or set CHROME_PATH')
if not shutil.which('npx'): sys.exit('npx not found: install Node.js')
config = {'theme': 'neutral', 'htmlLabels': False, 'flowchart': {'htmlLabels': False, 'curve': 'linear'},
          'themeVariables': {'fontFamily': 'Helvetica, Arial, sans-serif', 'fontSize': '14px'}}
# The guide's shared colours, so every diagram names a class instead of restating its colours. The overview uses kept,
# changed, problem and new; an architecture diagram uses part (inside the method), ext (outside it) and boundary (the
# dotted line around the method). A classDef in the diagram's own source wins over these.
CLASSES = {'kept': 'fill:#e5e7eb,stroke:#6b7280,color:#111827', 'changed': 'fill:#fde68a,stroke:#d97706,color:#111827',
           'problem': 'fill:#fecaca,stroke:#dc2626,color:#111827', 'new': 'fill:#bfdbfe,stroke:#2563eb,color:#111827',
           'part': 'fill:#6fcf73,stroke:#3f9f45,stroke-width:1.5px,color:#0b1220,font-weight:bold',
           'ext': 'fill:#5cc8f7,stroke:#2b9ad1,stroke-width:1.5px,color:#0b1220,font-weight:bold',
           'boundary': 'fill:#ffffff,stroke:#111827,stroke-width:2px,stroke-dasharray:3 5'}
text = open(src, encoding='utf-8').read()
used = set(re.findall(r'^\s*class\s+\S+\s+(\w+)', text, re.M)) | set(re.findall(r':::(\w+)', text))
add = [f'    classDef {c} {CLASSES[c]}' for c in sorted(used & CLASSES.keys()) if not re.search(rf'^\s*classDef\s+{c}\b', text, re.M)]
with tempfile.TemporaryDirectory() as tmp:
    cfg, pup, mmd = os.path.join(tmp, 'mermaid.json'), os.path.join(tmp, 'puppeteer.json'), os.path.join(tmp, 'diagram.mmd')
    json.dump(config, open(cfg, 'w')); json.dump({'executablePath': find_chrome()}, open(pup, 'w'))
    open(mmd, 'w', encoding='utf-8').write(text.rstrip('\n') + '\n' + ''.join(l + '\n' for l in add))
    run = subprocess.run(['npx', '-y', '@mermaid-js/mermaid-cli@12.0.0', '-i', mmd, '-o', out, '-b', 'transparent', '-c', cfg, '-p', pup],
                         env={**os.environ, 'PUPPETEER_SKIP_DOWNLOAD': '1'}, capture_output=True, text=True)
if run.returncode != 0 or not os.path.exists(out):
    # Mermaid's own message ("Error: Parse error on line 2" and the lines that point at it) sits above a long stack trace.
    err = re.search(r'^.*Error\b.*(?:\n.*){0,3}', run.stderr, re.M)
    sys.exit(err[0] if err else (run.stdout[-800:] + run.stderr[-800:]))
svg = open(out, encoding='utf-8').read()
# An HTML label (foreignObject) does not render inside an <img>, so every label must be SVG text.
if '<foreignObject' in svg or '<text' not in svg:
    sys.exit(f'{out}: {svg.count("<foreignObject")} HTML labels, {svg.count("<text")} SVG text labels; every label must be SVG text')
print(f'{out}: {len(svg):,} bytes, {svg.count("<text")} text labels')
# The guide scales the SVG to at most its column, 527 pt on A4 with 12 mm margins: labels must still print near body size.
import re
width = float(re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+)', svg)[1]); px = float(re.search(r'font-size:\s*([\d.]+)px', svg)[1])
if px * 527 / width < 7:
    sys.exit(f'{out}: labels print at {px * 527 / width:.1f} pt even at full column width; need 7 pt or more. '
             'Raise "fontSize" in the %%{init}%% line, or use fewer boxes per row')
