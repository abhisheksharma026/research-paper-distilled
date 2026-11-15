"""Convert one guide part written in Markdown into the HTML fragment that build.py joins.

Usage: python3 -I md_part.py PART.md PART.html
The Markdown conventions are in assets/part_skeleton.md: "# Part N. Title", a "Question:" line, "##" numbered sections,
"###" box headings ("Math 2."), "::: classes #id" blocks closed by ":::", an image alone on its line as a figure, and
LaTeX in $...$ and $$...$$, which becomes MathML. Page markers, {work page N} markers and "Part N" references pass
through for build.py to link.
Needs Node.js. The first run installs katex 0.16.11 and marked 12.0.2 into ~/.cache/research-paper-distilled.
"""
import os, re, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
deps = os.path.expanduser('~/.cache/research-paper-distilled')
if not all(os.path.exists(os.path.join(deps, 'node_modules', p)) for p in ('katex', 'marked')):
    os.makedirs(deps, exist_ok=True)
    run = subprocess.run(['npm', 'install', '--prefix', deps, '--no-audit', '--no-fund', 'katex@0.16.11', 'marked@12.0.2'],
                         capture_output=True, text=True)
    if run.returncode != 0: sys.exit(f'npm install failed: {run.stderr[-600:]}')
here = os.path.dirname(os.path.abspath(__file__))
run = subprocess.run(['node', os.path.join(here, 'md_part.mjs'), src, out, deps], capture_output=True, text=True)
# On failure, print the error line Node puts above its stack trace; the trace itself only costs the reader tokens.
err = re.search(r'^\w*Error\b.*$', run.stderr, re.M)
print(run.stdout.strip() or (err[0] if err else run.stderr.strip()[-800:]))
sys.exit(run.returncode)
