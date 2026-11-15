"""Render a built guide as two-page spreads for a visual check of every page.

Usage: python3 -I render_spreads.py GUIDE.pdf OUT_DIR [DPI]
Writes OUT_DIR/spread-01.png, spread-02.png, ... Look at each for clipped formulas, overflow, blank space and headings
left alone at the bottom of a page.
"""
import glob, os, subprocess, sys
pdf, out = sys.argv[1], sys.argv[2]; dpi = sys.argv[3] if len(sys.argv) > 3 else '80'
def find_chrome(configured=None):
    """Chrome or Chromium: the config value, then $CHROME_PATH, then the macOS app, then common command names."""
    import shutil
    for c in (configured, os.environ.get('CHROME_PATH'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        if c and os.path.exists(c): return c
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        if shutil.which(name): return shutil.which(name)
    sys.exit('Chrome or Chromium not found: install Google Chrome, or set CHROME_PATH')
chrome = find_chrome()
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, 'pg-*.png')) + glob.glob(os.path.join(out, 'spread-*')): os.remove(f)
subprocess.run(['pdftoppm', '-r', dpi, '-png', pdf, os.path.join(out, 'pg')], check=True)
pages = sorted(glob.glob(os.path.join(out, 'pg-*.png')))
for i in range(0, len(pages), 2):
    imgs = ''.join(f'<img src="file://{p}" style="width:740px;background:#fff">' for p in pages[i:i + 2])
    h = os.path.join(out, f'spread-{i // 2 + 1:02d}.html'); png = h[:-5] + '.png'
    try:
        open(h, 'w').write(f'<html><body style="margin:0;background:#777;display:flex;gap:10px;width:1500px">{imgs}</body></html>')
        subprocess.run([chrome, '--headless', f'--screenshot={png}', '--window-size=1500,1050', 'file://' + h], check=True, capture_output=True)
    finally:
        if os.path.exists(h): os.remove(h)
    if not os.path.exists(png) or os.path.getsize(png) == 0: sys.exit(f'Chrome did not write {png}')
print(f'{len(pages)} pages in {(len(pages) + 1) // 2} spreads in {out}')
