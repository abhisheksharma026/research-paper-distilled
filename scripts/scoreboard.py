"""Turn a benchmark results table (JSON) into the scoreboard HTML and a one-line count of the groups.

Usage: python3 -I scoreboard.py RESULTS.json OUT_TABLE.html OUT_COUNT.html

RESULTS.json is a list. A family heading is {"family": "Closed-book QA"}. A benchmark row is
{"name", "metric", "zero", "one", "few", "comparison", "label", "chance", "note"}, or "score" in place of zero, one and
few for a paper without those settings. chance is the chance level
in percent, 0 for an open answer with no chance level (the floor is then 0), or null for no rating.
Optional "kind": "lower_is_better" (for example perplexity) or "mixed" (an average with no single chance level).
Gap closed = (few - floor) / (comparison - floor). Groups: beats or matches (few >= comparison), within 1 point below
(comparison - 1 <= few < comparison), competitive (gap >= 80%), behind. Lower-is-better rows only beat, match or trail.
"""
import html as _h, json, sys
esc = lambda v: _h.escape(str(v)) if v is not None else ''
rows, out_table, out_count = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
# A paper without zero-, one- and few-shot settings gives one "score" per row, and the table shows one column for it.
shots = any('zero' in r or 'one' in r for r in rows if 'family' not in r)
for r in rows:
    if 'score' in r and 'few' not in r: r['few'] = r['score']
html = ['<table class="t sb">', f'<tr><th>Benchmark</th><th>Metric</th><th>{"Zero / one / few" if shots else "Score"}</th><th>Compared with</th><th>Chance or floor</th><th>Gap closed</th><th>Group</th><th>Note</th></tr>']
groups = {'beat': 0, 'near': 0, 'comp': 0, 'behind': 0, 'other': 0}
beat_label = lambda d: 'Beats' if d > 0 else 'Matches'
fmt = lambda v: '–' if v is None else (f'{v:.1f}' if isinstance(v, (int, float)) else str(v))
for r in rows:
    if 'family' in r:
        html.append(f'<tr class="fam"><td colspan="8">{esc(r["family"])}</td></tr>'); continue
    few, comp, chance, kind = r.get('few'), r['comparison'], r.get('chance'), r.get('kind')
    if kind == 'lower_is_better':
        best = r.get('zero') if few is None else few
        if best is None: sys.exit(f'{r["name"]}: a lower-is-better row needs a score')
        d = round(comp - best, 6)
        gap, group = '–', (f'<span class="g-beat">{beat_label(d)}</span>' if d >= 0 else '<span class="g-behind">Behind</span>')
        groups['beat' if d >= 0 else 'behind'] += 1
    elif kind == 'mixed' or chance is None or few is None:
        gap, group = '–', esc(r.get('group_text', 'No rating')); groups['other'] += 1
    else:
        if comp <= chance: sys.exit(f'{r["name"]}: the comparison ({comp}) must be above the chance level or floor ({chance})')
        g = (few - chance) / (comp - chance) * 100
        # One decimal when whole-number rounding would hide the direction (99.6% printed as 100%).
        gap = f'{g:.1f}%' if round(g) == 100 and round(g, 6) != 100 else f'{g:.0f}%'
        # Round before comparing, so a value exactly on a threshold (2.8 against 3, floor 2) is not lost to float error.
        d = round(few - comp, 6)
        key = 'beat' if d >= 0 else 'near' if round(d + 1, 6) >= 0 else 'comp' if round(g, 6) >= 80 else 'behind'
        groups[key] += 1
        group = {'beat': f'<span class="g-beat">{beat_label(d)}</span>', 'near': '<span class="g-comp">Within 1 point below</span>',
                 'comp': '<span class="g-comp">Competitive</span>', 'behind': '<span class="g-behind">Behind</span>'}[key]
    ch = '–' if chance is None else ('none (floor 0)' if chance == 0 else f'{chance:g}%')
    score_cell = ' / '.join(fmt(v) for v in (r.get('zero'), r.get('one'), few)) if shots else fmt(few)
    html.append(f'<tr><td>{esc(r["name"])}</td><td>{esc(r["metric"])}</td><td style="white-space:nowrap">{score_cell}</td>'
                f'<td>{fmt(comp)}, {esc(r["label"])}</td><td>{ch}</td><td>{gap}</td><td>{group}</td><td>{esc(r.get("note", ""))}</td></tr>')
html.append('</table>')
open(out_table, 'w', encoding='utf-8').write('\n'.join(html) + '\n')
g = groups; one = lambda n, sing, plur: f'{n} {sing if n == 1 else plur}'
open(out_count, 'w', encoding='utf-8').write(f'<p class="small">On the scoreboard, {one(g["beat"], "benchmark beats or matches", "benchmarks beat or match")} the comparison, '
                                             f'{one(g["near"], "is", "are")} within 1 point below it, {one(g["comp"], "is", "are")} competitive, '
                                             f'{one(g["behind"], "is", "are")} behind, and {one(g["other"], "has", "have")} no single rating.</p>\n')
print(groups)
