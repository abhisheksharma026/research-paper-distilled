"""Fetch a web article (a blog post or an online explainer) as the source of a guide, in the same shape as a paper.

Usage: python3 -I fetch_web.py URL OUT_DIR [--last "Heading"]
Writes, in OUT_DIR:
  source.html              the fetched page, unchanged: the pinned version
  pages/<N>.txt            the text of article section N, cited in the guide as [§ N]; also <N>.layout.txt, so every
                           check that reads pages reads sections. pages/paper.json pins source.html (SHA-256) and
                           records the URL, the fetch date and each section's anchor
  sections.json            one entry per section: number, heading, anchor (the heading's id or a text fragment), words
  images/, images.json     the article's figures in order, numbered 1, 2, ... after inline lazy-load placeholders
                           (data: URIs under 2 KB) and icons (48 px or less, or a raster under 2 KB) are dropped;
                           each with its section and the sentences around it
  math.json                every TeX expression written in the text: \\( \\), \\[ \\], $$ $$
  links.json               every outbound link in the article, with its text and section: the post's reference list
  page.pdf                 the live page printed by Chrome, for reading
The article's sections are the heading level that carries its prose. Trailing headings with no prose (related posts,
comments) are cut. When the page has a <main> element, the text after it is dropped. An <aside> followed by more of the
post's prose is kept as a callout; one with no prose after it is a sidebar and is dropped; both word counts are printed.
Check the printed list of kept sections, and pass --last to end at a given heading.
Limits: 10 MB page, 60 images of 10 MB each, http and https only. Exit code 1 when no article text is found.
"""
import base64, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request
from html.parser import HTMLParser

args = sys.argv[1:]
last = args[args.index('--last') + 1] if '--last' in args else None
url, out = [a for i, a in enumerate(args) if a != '--last' and (i == 0 or args[i - 1] != '--last')][:2]
if urllib.parse.urlparse(url).scheme not in ('http', 'https'): sys.exit('only http and https URLs are fetched')
MAX_PAGE, MAX_IMAGES, MAX_IMAGE = 10 << 20, 60, 10 << 20
os.makedirs(os.path.join(out, 'pages'), exist_ok=True); os.makedirs(os.path.join(out, 'images'), exist_ok=True)

def get(u, cap):
    req = urllib.request.Request(u, headers={'User-Agent': 'research-paper-distilled'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read(cap + 1)
        if len(data) > cap: raise ValueError(f'over {cap >> 20} MB: {u}')
        return data, r.headers.get('Content-Type', '')

raw, _ = get(url, MAX_PAGE)
open(os.path.join(out, 'source.html'), 'wb').write(raw)
page = raw.decode('utf-8', errors='replace')

class Blocks(HTMLParser):
    """The page as a flat list of blocks: headings, prose, images and links, in reading order."""
    # An <aside> is read but flagged; once the article's end is known, a sidebar aside is dropped (see below).
    # A <header> inside an <article> holds the post's own title and date, so every other header is skipped.
    SKIP = {'script', 'style', 'nav', 'footer', 'noscript', 'form', 'button', 'svg', 'select'}
    TEXT = {'p', 'li', 'blockquote', 'figcaption', 'pre', 'td', 'th', 'dd', 'dt'}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.blocks, self.buf, self.skip, self.head, self.kind = [], [], 0, None, None
        self.main, self.aside, self.article, self.headers = 0, 0, 0, []
    def flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip(); self.buf = []
        if not t: return
        if self.head: self.blocks.append({'type': 'h', 'level': self.head[0], 'id': self.head[1], 'text': t, 'main': self.main > 0})
        else: self.blocks.append({'type': 'p', 'text': t, 'main': self.main > 0, 'aside': self.aside > 0})
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main': self.flush(); self.main += 1
        if tag == 'aside': self.aside += 1
        if tag == 'article': self.article += 1
        if tag == 'header':
            site = not self.article; self.headers.append(site)
            if site: self.skip += 1; return
        if tag in self.SKIP: self.skip += 1; return
        if self.skip: return
        if re.fullmatch(r'h[1-6]', tag): self.flush(); self.head = (int(tag[1]), a.get('id') or ''); return
        if tag in self.TEXT or tag in ('div', 'section', 'br', 'tr', 'table', 'ul', 'ol', 'figure'): self.flush()
        if tag == 'img' and a.get('src'): self.flush(); self.blocks.append({'type': 'img', 'src': a['src'], 'alt': a.get('alt') or '', 'main': self.main > 0, 'aside': self.aside > 0})
        if tag == 'a' and a.get('href'): self.blocks.append({'type': 'a', 'href': a['href'], 'start': len(''.join(self.buf)), 'main': self.main > 0, 'aside': self.aside > 0})
    def handle_endtag(self, tag):
        if tag == 'main': self.flush(); self.main = max(0, self.main - 1)
        if tag == 'aside': self.aside = max(0, self.aside - 1)
        if tag == 'article': self.article = max(0, self.article - 1)
        if tag == 'header' and self.headers and self.headers.pop(): self.skip = max(0, self.skip - 1); return
        if tag in self.SKIP: self.skip = max(0, self.skip - 1); return
        if self.skip: return
        if re.fullmatch(r'h[1-6]', tag): self.flush(); self.head = None; return
        if tag in self.TEXT or tag in ('div', 'section', 'table', 'ul', 'ol', 'figure'): self.flush()
        if tag == 'a':
            for b in reversed(self.blocks):
                if b['type'] == 'a' and 'text' not in b:
                    b['text'] = re.sub(r'\s+', ' ', ''.join(self.buf)[b.pop('start'):]).strip(); break
    def handle_data(self, d):
        if not self.skip: self.buf.append(d)

p = Blocks(); p.feed(page); p.flush()
blocks = [b for b in p.blocks if not (b['type'] == 'a' and 'text' not in b)]
# On a page with a <main> element, what follows it is site content (subscribe boxes, site links). What precedes it
# stays, because some sites put the post's title and introduction before <main>.
first_main = next((i for i, b in enumerate(blocks) if b['main'] and b['type'] == 'h'), None)
if first_main is not None: blocks = [b for i, b in enumerate(blocks) if b['main'] or i < first_main]
heads = [i for i, b in enumerate(blocks) if b['type'] == 'h']
if not heads: sys.exit('no headings found: this page does not look like an article')
title_i = next((i for i in heads if blocks[i]['level'] == 1), heads[0])
words_after = lambda i: sum(len(b['text'].split()) for b in blocks[i + 1:next((j for j in heads if j > i), len(blocks))] if b['type'] == 'p' and not b.get('aside'))
body_heads = [i for i in heads if i > title_i]
# The article ends after the last heading whose own prose is substantial; --last overrides.
prose_heads = [i for i in body_heads if words_after(i) >= 30]
if last:
    hit = [i for i in body_heads if blocks[i]['text'].strip().lower() == last.strip().lower()]
    if not hit: sys.exit(f'--last "{last}" is not a heading; headings are: {[blocks[i]["text"] for i in body_heads]}')
    end_head = hit[0]
else:
    end_head = prose_heads[-1] if prose_heads else title_i
end = next((j for j in heads if j > end_head), len(blocks))
levels = {}
for i in body_heads:
    if i <= end_head: levels[blocks[i]['level']] = levels.get(blocks[i]['level'], 0) + words_after(i)
level = min(levels, key=lambda l: (-levels[l], l)) if levels else None

sections = []
def start(heading, anchor):
    sections.append({'n': len(sections) + 1, 'heading': heading, 'anchor': anchor, 'blocks': []})
# An aside with more of the post's prose after it is a callout and stays; one after the last paragraph is a sidebar.
last_prose = max((i for i in range(title_i + 1, end) if blocks[i]['type'] == 'p' and not blocks[i].get('aside')), default=title_i)
sidebar = lambda i: blocks[i].get('aside') and i > last_prose
aside_words = lambda keep: sum(len(blocks[i]['text'].split()) for i in range(title_i + 1, end)
                               if blocks[i]['type'] == 'p' and blocks[i].get('aside') and sidebar(i) != keep)
intro = [b for b in blocks[title_i + 1:(body_heads[0] if body_heads else end)] if b['type'] != 'h' and not b.get('aside')]
if sum(len(b['text'].split()) for b in intro if b['type'] == 'p') >= 30: start('Introduction', '')
for i in range(title_i + 1, end):
    b = blocks[i]
    if sidebar(i): continue
    if b['type'] == 'h' and b['level'] == level:
        start(b['text'], b['id'] or ':~:text=' + urllib.parse.quote(b['text']))
    elif sections:
        sections[-1]['blocks'].append(b)
if not sections: sys.exit('no article sections found; pass --last, or check the page')

images, links, math, total = [], [], [], 0
for s in sections:
    prose = [b['text'] for b in s['blocks'] if b['type'] == 'p']
    text = s['heading'] + '\n' + '\n'.join(prose) + '\n'
    s['words'] = len(' '.join(prose).split()); total += s['words']
    for suffix in ('.txt', '.layout.txt'):
        open(os.path.join(out, 'pages', f'{s["n"]}{suffix}'), 'w', encoding='utf-8').write(text)
    for rx, kind in ((r'\\\((.+?)\\\)', 'inline'), (r'\\\[(.+?)\\\]', 'display'), (r'\$\$(.+?)\$\$', 'display')):
        for m in re.finditer(rx, ' '.join(prose), re.S): math.append({'section': s['n'], 'kind': kind, 'tex': m[1].strip()})
    for k, b in enumerate(s['blocks']):
        if b['type'] == 'a' and not b['href'].startswith('#'):
            links.append({'section': s['n'], 'text': b['text'], 'href': urllib.parse.urljoin(url, b['href'])})
        if b['type'] == 'img':
            before = next((x['text'] for x in reversed(s['blocks'][:k]) if x['type'] == 'p'), '')
            after = next((x['text'] for x in s['blocks'][k + 1:] if x['type'] == 'p'), '')
            images.append({'section': s['n'], 'src': urllib.parse.urljoin(url, b['src']), 'alt': b['alt'],
                           'before': before[-240:], 'after': after[:240]})

EXT = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/gif': '.gif', 'image/svg+xml': '.svg', 'image/webp': '.webp'}
# A lazy-load placeholder is an inline data: URI under 2 KB. An icon is a PNG or GIF of 48 by 48 pixels or less, or
# another raster file under 2 KB. A small SVG, or a small PNG wider than 48 pixels (an equation), is kept. Only saved
# images are numbered, so the guide's "Image N" matches the reader's count of figures on the page.
MIN_IMAGE, ICON, kept, dropped = 2048, 48, [], []
def pixels(blob):
    if blob[:8] == b'\x89PNG\r\n\x1a\n': return int.from_bytes(blob[16:20], 'big'), int.from_bytes(blob[20:24], 'big')
    if blob[:4] == b'GIF8': return int.from_bytes(blob[6:8], 'little'), int.from_bytes(blob[8:10], 'little')
    return None
for im in images[:MAX_IMAGES]:
    try:
        if im['src'].startswith('data:image/'):
            head, data = im['src'].split(',', 1); ctype = head[5:].split(';')[0]
            blob = base64.b64decode(data) if ';base64' in head else urllib.parse.unquote_to_bytes(data)
        elif urllib.parse.urlparse(im['src']).scheme in ('http', 'https'):
            blob, ctype = get(im['src'], MAX_IMAGE); ctype = ctype.split(';')[0].strip()
        else:
            dropped.append((im['section'], 'not http, https or data')); continue
        if ctype not in EXT: dropped.append((im['section'], f'not an image ({ctype})')); continue
        if im['src'].startswith('data:') and len(blob) < MIN_IMAGE: dropped.append((im['section'], f'placeholder ({len(blob)} bytes)')); continue
        size = pixels(blob)
        if size and max(size) <= ICON: dropped.append((im['section'], f'icon ({size[0]}x{size[1]} px)')); continue
        if not size and ctype != 'image/svg+xml' and len(blob) < MIN_IMAGE: dropped.append((im['section'], f'icon ({len(blob)} bytes)')); continue
        im['n'] = len(kept) + 1; im['file'] = f'images/{im["n"]:02d}{EXT[ctype]}'
        open(os.path.join(out, im['file']), 'wb').write(blob); kept.append(im)
    except Exception as e:
        dropped.append((im['section'], str(e)[:120]))
images = kept

def find_chrome():
    for c in (os.environ.get('CHROME_PATH'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        if c and os.path.exists(c): return c
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        if shutil.which(name): return shutil.which(name)
    return None
chrome, pdf_note = find_chrome(), 'not printed: Chrome not found'
if chrome:
    with tempfile.TemporaryDirectory() as prof:
        r = subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--user-data-dir={prof}',
                            '--virtual-time-budget=8000', f'--print-to-pdf={os.path.join(out, "page.pdf")}', url], capture_output=True, text=True, timeout=180)
    pdf_note = 'page.pdf' if os.path.exists(os.path.join(out, 'page.pdf')) else 'not printed: ' + r.stderr[-160:]

title = re.sub(r'\s+', ' ', blocks[title_i]['text']).strip()
for s in sections: s.pop('blocks')
sha = hashlib.sha256(raw).hexdigest()
fetched = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump(sections, open(os.path.join(out, 'sections.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(images, open(os.path.join(out, 'images.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(math, open(os.path.join(out, 'math.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(links, open(os.path.join(out, 'links.json'), 'w'), indent=1, ensure_ascii=False)
json.dump([], open(os.path.join(out, 'pages', 'captions.json'), 'w'))
json.dump({'kind': 'web', 'pdf': os.path.abspath(os.path.join(out, 'source.html')), 'sha256': sha, 'pages': len(sections),
           'url': url, 'fetched': fetched, 'title': title, 'anchors': [s['anchor'] for s in sections], 'low_text_pages': []},
          open(os.path.join(out, 'pages', 'paper.json'), 'w'), indent=1, ensure_ascii=False)

print(f'{title} | {total:,} words in {len(sections)} sections | sha256 {sha[:12]} | fetched {fetched}')
for s in sections: print(f'  §{s["n"]} {s["heading"]} ({s["words"]} words) #{s["anchor"][:40]}')
cut = [blocks[i]['text'] for i in heads if i > end_head]
if cut: print(f'cut after the article: {cut[:6]}{" ..." if len(cut) > 6 else ""}')
print(f'images: {len(images)} saved' + (f', {len(dropped)} dropped: ' + '; '.join(f'§{n} {why}' for n, why in dropped) if dropped else '') +
      (f' | asides: {aside_words(True)} words kept as callouts, {aside_words(False)} dropped as sidebars' if aside_words(True) or aside_words(False) else '') + f' | math: {len(math)} TeX expressions | links: {len(links)} | {pdf_note}')
