"""Extract a paper PDF page by page and index its figure and table captions.

Usage: python3 -I extract_pages.py PAPER.pdf OUT_DIR
Writes OUT_DIR/<N>.txt (plain), OUT_DIR/<N>.layout.txt (layout-preserving), OUT_DIR/captions.json, and
OUT_DIR/paper.json, which pins the exact file (SHA-256, page count) so the checks refuse a different version.
Pages with almost no text layer are listed as low-text; when many are, the PDF is probably scanned (exit code 2).
Claims must be checked against both extractions: table rows and accented words often match only one of them.
"""
import hashlib, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from labels import LABEL, caption_after
pdf, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout)[1])
captions, low_text = [], []
for p in range(1, n + 1):
    for mode, suffix in ((None, '.txt'), ('-layout', '.layout.txt')):
        args = ['pdftotext', '-f', str(p), '-l', str(p)] + ([mode] if mode else []) + [pdf, os.path.join(out, f'{p}{suffix}')]
        subprocess.run(args, check=True)
    if len(re.sub(r'\s', '', open(os.path.join(out, f'{p}.txt'), encoding='utf-8').read())) < 200: low_text.append(p)
    page_txt = open(os.path.join(out, f'{p}.txt'), encoding='utf-8').read()
    for m in re.finditer(rf'(?m)^[ \t]*({LABEL})', page_txt):
        rest = page_txt[m.end():]
        if re.match(caption_after(m[1]), rest):
            captions.append({'label': m[1], 'page': p, 'start': rest.lstrip(':. \t\n').split('\n')[0].strip()[:160]})
json.dump(captions, open(os.path.join(out, 'captions.json'), 'w'), indent=1)
sha = hashlib.sha256(open(pdf, 'rb').read()).hexdigest()
json.dump({'pdf': os.path.abspath(pdf), 'sha256': sha, 'pages': n, 'low_text_pages': low_text}, open(os.path.join(out, 'paper.json'), 'w'), indent=1)
print(f'{n} pages; {len(captions)} captions; figures {sum(c["label"].startswith("Fig") for c in captions)}, tables {sum(c["label"].lower().startswith("table") for c in captions)}; sha256 {sha[:12]}')
if low_text:
    print(f'low-text pages (under 200 characters): {low_text}')
if len(low_text) > 0.3 * n:
    print('SCANNED: most pages have no text layer. Stop and offer OCR (for example Marker with --force_ocr); report numbers read from OCR as spot-checked.')
    sys.exit(2)
