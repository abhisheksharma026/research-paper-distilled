"""Check the reader-question map of a guide: every lens asked, every question placed, every answer on its page.

Usage: python3 -I check_questions.py GUIDE.html QUESTIONS.json PAGES_DIR
QUESTIONS is a list of {"lens", "question", "where", "status", "page", "evidence", "followup"} (references/reader-questions.md).
Fails when a lens has fewer than 3 questions, a "where" anchor is not an id in the guide, an "answered" evidence phrase is not
on its page (plain or layout text, after NFC and whitespace normalization), or the subsection of a "not in paper" question
has no sentence saying that the paper does not give it. Exit code 1 on any failure.
"""
import html, json, os, re, sys, unicodedata
guide, qpath, pages = sys.argv[1:4]
src = open(guide, encoding='utf-8').read()
LENSES = ('newcomer', 'practitioner', 're-implementer', 'reviewer')
NOT_GIVEN = (r"does not (?:say|give|state|report|explain|test|compare|describe|name)|(?:is|are|was|were) not (?:given|stated|reported|tested)"
             r"|(?:reports|gives|states|names) no\b|with no (?:spread|test)")
norm = lambda t: re.sub(r'\s+', ' ', unicodedata.normalize('NFC', t).replace('’', "'").replace('“', '"').replace('”', '"')).strip().lower()

def page(n):
    files = [os.path.join(pages, f'{n}{ext}.txt') for ext in ('', '.layout')]
    return ' '.join(norm(open(f, encoding='utf-8').read()) for f in files if os.path.exists(f))

def section(anchor):
    """The text from the element with this id to the end of its part (a section id) or to the next h2 or h3."""
    m = re.search(rf'<(\w+)[^>]*\bid="{re.escape(anchor)}"', src)
    if not m: return None
    end = src.find('</section>', m.end()) if m[1] == 'section' else (re.search(r'<h[23]\b|</section>', src[m.end():]) or re.search(r'$', src[m.end():])).start() + m.end()
    return norm(html.unescape(re.sub(r'<[^>]+>', ' ', src[m.start():end])))

items = []
for q in json.load(open(qpath, encoding='utf-8')):
    items.append(q)
    if q.get('followup'): items.append({**q['followup'], 'lens': q['lens'], 'followup_of': q['question']})
fails = []
for lens in LENSES:
    n = sum(1 for q in items if q['lens'] == lens and 'followup_of' not in q)
    if n < 3: fails.append(f'lens "{lens}" has {n} questions; ask 3 to 5')
for q in items:
    label = f'"{q["question"][:60]}"'
    text = section(q.get('where', ''))
    if text is None: fails.append(f'{label}: anchor "{q.get("where")}" is not in the guide'); continue
    if q.get('status') == 'answered':
        if not q.get('evidence') or norm(q['evidence']) not in page(q.get('page')):
            fails.append(f'{label}: evidence is not on page {q.get("page")}: "{q.get("evidence", "")[:60]}"')
    elif q.get('status') == 'not in paper':
        if not re.search(NOT_GIVEN, text): fails.append(f'{label}: {q["where"]} never says that the paper does not give this')
    else: fails.append(f'{label}: status must be "answered" or "not in paper"')
print(f'questions {sum(1 for q in items if "followup_of" not in q)} | follow-ups {sum(1 for q in items if "followup_of" in q)} | '
      f'answered {sum(1 for q in items if q.get("status") == "answered")} | not in paper {sum(1 for q in items if q.get("status") == "not in paper")}')
print(f'FAIL: {len(fails)}'); [print('  FAIL', f) for f in fails]
sys.exit(1 if fails else 0)
