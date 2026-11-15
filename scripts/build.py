"""Build a study guide PDF from its part files and check the result.

Usage: python3 -I build.py CONFIG.json

CONFIG (paths relative to the config file):
  title, footer            text for the heading and the page footer
  paper_url                URL of the paper PDF; every "p. N" becomes a link to URL#page=N (omit to leave pages unlinked).
                           Bracketed markers, [p. N] and [§ N], are then hidden: they stay in the HTML for the checks only
  web_source               for a web article: the fetch_web.py output folder; every "§ N" links to section N's anchor
                           on the article's URL, and paper_url defaults to that URL
  parts                    list of HTML fragments, each a <section class="part" id="..."> with one <h2>
  out_html, out_pdf        where to write the joined HTML and the PDF
  works                    cited works the guide quotes, as {"key": "URL of the exact PDF read"}. In a part, write
                           {key page 3} or {key pages 1 and 8} for a page of that work, and {key|Text} for the work
                           itself; each becomes a link (URL#page=N). An unknown key stops the build
  page_cap                 maximum page count (optional)
  new_page_sections        section ids that start on a new page (optional)
  compact_sections         section ids printed in the compact reference style (optional)
  css, chrome              optional overrides for the stylesheet and the Chrome binary

Exit code 1 when the page cap or the true-size check fails.
"""
import html, json, os, re, statistics, subprocess, sys, tempfile

cfg_path = os.path.abspath(sys.argv[1]); base = os.path.dirname(cfg_path); cfg = json.load(open(cfg_path))
here = os.path.dirname(os.path.abspath(__file__))
rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
css = open(rel(cfg['css']) if cfg.get('css') else os.path.join(here, '..', 'assets', 'guide.css'), encoding='utf-8').read()
css = css.replace('{{FOOTER}}', cfg.get('footer', cfg['title']))
def find_chrome(configured=None):
    """Chrome or Chromium: the config value, then $CHROME_PATH, then the macOS app, then common command names."""
    import shutil
    for c in (configured, os.environ.get('CHROME_PATH'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        if c and os.path.exists(c): return c
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        if shutil.which(name): return shutil.which(name)
    sys.exit('Chrome or Chromium not found: install Google Chrome, or set CHROME_PATH or the "chrome" config key')
chrome = find_chrome(cfg.get('chrome'))
out_html, out_pdf = rel(cfg['out_html']), rel(cfg['out_pdf'])
anchors = []
if cfg.get('web_source'):
    pin = json.load(open(os.path.join(rel(cfg['web_source']), 'pages', 'paper.json')))
    anchors = pin['anchors']; cfg.setdefault('paper_url', pin['url'])
if 'arxiv.org' in cfg.get('paper_url', '') and not re.search(r'v\d+$', cfg['paper_url']):
    sys.exit('paper_url must name the arXiv version (for example .../2005.14165v4): page numbers differ between versions')
body = '\n'.join(open(rel(p), encoding='utf-8').read() for p in cfg['parts'])
# Includes: <!--include: file.html--> pulls in a generated fragment, such as the scoreboard.
body = re.sub(r'<!--include: ([^>]+?)-->', lambda m: open(rel(m[1].strip()), encoding='utf-8').read(), body)

# Cited works: {key page N} and {key pages N and M} link to those pages of the work's PDF, {key|Text} to the work.
works = cfg.get('works', {})
for key, url in works.items():
    if 'arxiv.org' in url and not re.search(r'v\d+(?:\.pdf)?$', url): sys.exit(f'works "{key}" must name the arXiv version')
def work_link(m):
    if m[1] not in works: sys.exit(f'"{m[0]}": no work "{m[1]}" in the config\'s "works"')
    url = works[m[1]]
    if m[2]: return f'<a class="pg wk" href="{url}">{m[2]}</a>'
    if m[3] == 'page': return f'<a class="pg wk" href="{url}#page={m[4]}">page {m[4]}</a>'
    return 'pages ' + re.sub(r'\d+', lambda n: f'<a class="pg wk" href="{url}#page={n[0]}">{n[0]}</a>', m[4])
work_re = re.compile(r'\{([a-z][\w-]*)(?:\|([^{}<>]+)|\s+(pages?)\s+(\d+(?:\s*(?:,|and|to|&ndash;|–)\s*\d+)*))\}')
body = ''.join(c if c.startswith('<pre') else work_re.sub(work_link, c) for c in re.split(r'(<pre[\s\S]*?</pre>)', body))
left = re.search(r'\{[a-z][\w-]*(?:\||\s+pages?\s)[^{}]*\}', re.sub(r'<pre[\s\S]*?</pre>', '', body))
if left: sys.exit(f'"{left[0][:60]}": a work marker the build cannot convert (no tags inside the text; write ² not <sup>2</sup>)')

for sid in cfg.get('new_page_sections', []) + cfg.get('compact_sections', []):
    if f'id="{sid}"' not in body: sys.exit(f'config names section "{sid}", but no part has that id')
for sid in cfg.get('new_page_sections', []):
    body = re.sub(rf'<section class="part" id="{sid}">', f'<section class="part newpage" id="{sid}">', body)
for sid in cfg.get('compact_sections', []):
    body = re.sub(rf'<section class="part( newpage)?" id="{sid}">', lambda m: f'<section class="part{m[1] or ""} compact" id="{sid}">', body)

# Targets: numbered sections, math boxes and metric entries get ids.
body = re.sub(r'<h3>(\d+)\.(\d+) ', lambda m: f'<h3 id="sec-{m[1]}-{m[2]}">{m[1]}.{m[2]} ', body)
body = re.sub(r'<h4>Math (\d+)\.', lambda m: f'<h4 id="math-{m[1]}">Math {m[1]}.', body)
body = re.sub(r'<h4>M(\d+)\. ', lambda m: f'<h4 id="m-{m[1]}">M{m[1]}. ', body)
body = re.sub(r'<div class="cap"([^>]*)><b>Image (\d+) ', lambda m: f'<div class="cap" id="image-{m[2]}"{m[1]}><b>Image {m[2]} ', body)
part_ids = {n: i for i, n in re.findall(r'<section class="part[^"]*" id="([^"]+)">\s*<h2>Part (\d+)\.', body)}
ids = set(re.findall(r'id="([^"]+)"', body))

# Links: page references open the paper; Part, Math, M, Code and Image references jump inside the guide.
ref_re = re.compile(r'(?<![\w])(?:(pp?)\. (\d+)((?:(?:&ndash;|–)\d+)|(?:, \d+)+)?|Parts? (\d+)(?:\.(\d+))?|Math (\d+)\b|M(\d+)\b)|§ (\d+)\b|Code (\d+)\b|Image (\d+)\b(?! \[)')
def link(m):
    if m[8]:
        n = int(m[8])
        if not 1 <= n <= len(anchors): sys.exit(f'"§ {n}": the web source has sections 1 to {len(anchors)}')
        return f'<a class="pg" href="{cfg["paper_url"]}#{anchors[n - 1]}">{m[0]}</a>'
    if m[1]:
        return f'<a class="pg" href="{cfg["paper_url"]}#page={m[2]}">{m[0]}</a>' if cfg.get('paper_url') else m[0]
    if m[9] or m[10]:
        target = f'code-{m[9]}' if m[9] else f'image-{m[10]}'
    elif m[4]:
        target = f'sec-{m[4]}-{m[5]}' if m[5] else part_ids.get(m[4])
    elif m[6]:
        target = f'math-{m[6]}'
    else:
        target = f'm-{m[7]}'
    return f'<a class="ref" href="#{target}">{m[0]}</a>' if target in ids else m[0]
pieces, skip = [], []
for chunk in re.split(r'(<[^>]+>)', body):
    t = re.match(r'<(/?)([a-zA-Z0-9]+)', chunk)
    if t:
        tag = t[2].lower()
        if chunk.startswith('<div class="codeh"'): tag = 'codeh'   # a snippet's own heading is not a reference
        if t[1] and tag == 'div' and skip and skip[-1] == 'codeh': tag = 'codeh'   # the end of that heading
        if tag in ('a', 'math', 'h1', 'h2', 'h3', 'h4', 'title', 'style', 'nav', 'pre', 'codeh') and not chunk.endswith('/>'):
            if t[1]:
                if skip and skip[-1] == tag: skip.pop()
            else:
                skip.append(tag)
        pieces.append(chunk)
    else:
        pieces.append(chunk if skip else ref_re.sub(link, chunk))
body = ''.join(pieces)
# Ranges: "Parts 3 to 6", "Math 1–6", "Part 3.1 and 3.2" link their second endpoint too.
def link_end(m):
    first, sep, num = m[1], m[3], m[4]
    kind = 'math' if '>Math ' in first else 'part'
    if kind == 'math': target = f'math-{num}'
    elif '.' in num: target = 'sec-' + num.replace('.', '-')
    else: target = part_ids.get(num)
    return first + sep + (f'<a class="ref" href="#{target}">{num}</a>' if target in ids else num)
body = re.sub(r'(<a class="ref" href="#[^"]+">(?:Parts?|Math) [\d.]+</a>)((\s*(?:to|and|&ndash;|–)\s*))(\d+(?:\.\d+)?)\b', lambda m: link_end(m), body)

# Page markers: every bracketed [p. N] or [§ N], with the space before it, stays in the HTML for the checks but is
# hidden from the reader, who sees no page references to the source.
body = re.sub(r'\s*\[(?:<a class="pg"[^>]*>)?(?:pp?\.|§) [^\[\]]*\]', lambda m: f'<span class="srcref">{m[0]}</span>', body)
css += '\n.srcref { display: none; }\n'

# Contents: one entry per part heading; page numbers come from a first print.
heads = re.findall(r'<section class="part[^"]*" id="([^"]+)">\s*<h2>(.*?)</h2>', body, re.S)
def toc(numbers):
    rows = ''.join(f'<li><a href="#{i}">{t}</a><span class="dots"></span><span>{numbers.get(i, "")}</span></li>\n' for i, t in heads)
    return f'<h1>{cfg["title"]}</h1>\n<nav class="toc">\n<h4>Contents</h4>\n<ol>\n{rows}</ol>\n</nav>\n'
def page(doc):
    return f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>{cfg["title"]}</title>\n<style>\n{css}</style>\n</head>\n<body>\n{doc}\n</body>\n</html>\n'
def render(doc):
    with tempfile.NamedTemporaryFile('w', suffix='.html', dir=os.path.dirname(out_html), delete=False, encoding='utf-8') as f:
        f.write(doc); tmp = f.name
    subprocess.run([chrome, '--headless', '--no-pdf-header-footer', '--generate-pdf-document-outline', f'--print-to-pdf={out_pdf}', 'file://' + tmp], check=True, capture_output=True)
    os.remove(tmp)
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', out_pdf], capture_output=True, text=True).stdout)[1])
    return [re.sub(r'\s+', ' ', subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), out_pdf, '-'], capture_output=True, text=True).stdout) for p in range(1, n + 1)]

first = render(page(toc({}) + body))
numbers = {}
for i, t in heads:
    key = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', t)).split()[:4])
    hits = [p + 1 for p, txt in enumerate(first) for _ in range(txt.count(key))]
    if len(hits) >= 2: numbers[i] = hits[1]
final_doc = page(toc(numbers) + body)
final = render(final_doc)
open(out_html, 'w', encoding='utf-8').write(final_doc)

# Checks: page cap and true size (Chrome shrinks the whole PDF when any element is wider than the page).
fails = []
if cfg.get('page_cap') and len(final) > cfg['page_cap']: fails.append(f'{len(final)} pages, over the cap of {cfg["page_cap"]}')
if len(final) != len(first): fails.append('the page count changed between the two passes; check the contents page')
h1_pt = float(re.search(r'h1 \{[^}]*font-size: ([\d.]+)pt', css)[1])
tsv = subprocess.run(['pdftotext', '-f', '1', '-l', '1', '-tsv', out_pdf, '-'], capture_output=True, text=True).stdout
rows = [r.split('\t') for r in tsv.splitlines()[1:]]
words = [(float(r[7]), float(r[9])) for r in rows if len(r) > 11 and r[0] == '5' and r[11].strip()]
first_top = min((t for t, _ in words), default=0)
heights = [h for t, h in words if t < first_top + 4]   # the first line of page 1 is the title
ratio = statistics.median(heights) / h1_pt if heights else 0
if not heights: fails.append('the title was not found on page 1, so the true-size check could not run')
elif ratio < 1.10: fails.append(f'the title prints at {ratio:.2f} of its size: some element is wider than the page, so Chrome shrank the PDF')
# A page other than the last that ends above its middle: a forced page break or a block too tall to fit left it half empty.
tsv_all = [r.split('\t') for r in subprocess.run(['pdftotext', '-tsv', out_pdf, '-'], capture_output=True, text=True).stdout.splitlines()[1:]]
page_h = {int(r[1]): float(r[9]) for r in tsv_all if len(r) > 9 and r[0] == '1'}
bottom = {}
for r in tsv_all:
    if len(r) > 11 and r[0] == '5' and r[11].strip() and float(r[7]) < page_h[int(r[1])] - 45:   # the footer sits in the last 45 pt
        bottom[int(r[1])] = max(bottom.get(int(r[1]), 0), float(r[7]) + float(r[9]))
for p in range(1, len(final)):
    if bottom.get(p, 0) < 0.5 * page_h.get(p, 1):
        fails.append(f'page {p} is more than half empty: check new_page_sections and any block too tall to fit')
print(f'pages: {len(final)} | title size ratio: {ratio:.3f} (true size is about 1.16)')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)
