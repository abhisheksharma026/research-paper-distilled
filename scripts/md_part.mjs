// Converts one guide part from Markdown to the HTML fragment build.py joins. Run it through md_part.py, which installs
// the pinned katex and marked packages and passes their folder as the third argument.
// The Markdown conventions are shown in assets/part_skeleton.md. Math, ::: blocks, figures and the question line are
// parser extensions, so code and comments are told apart by the Markdown parser itself, wherever they appear.
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const [, , input, output, deps] = process.argv;
const require = createRequire(`${deps}/package.json`);
const katex = require('katex');
const { Marked } = require('marked');
const LABEL = String.raw`(?:Figure|Fig\.|FIG\.|Table|TABLE|Image) (?:[0-9A-Z]+\.)?(?:\d+|[IVXL]+)`;
const tex = (t, display) => katex.renderToString(t.trim(), { output: 'mathml', displayMode: display, throwOnError: true })
  .replace(/^<span class="katex">|<\/span>$/g, '');
const attr = s => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
// The first "$" that is not escaped with a backslash.
const dollar = s => { const m = /(?<!\\)\$/.exec(s); return m ? m.index : undefined; };

// The body of a "::: classes #id" block up to its matching bare ":::", skipping fenced code and nested blocks.
function blockBody(src) {
  const lines = src.split('\n');
  let depth = 0, fence = null, comment = false;
  for (let i = 1; i < lines.length; i++) {
    const l = lines[i], f = l.match(/^ {0,3}(`{3,}|~{3,})/);
    if (comment) { if (l.includes('-->')) comment = false; continue; }
    if (!fence && /<!--/.test(l) && !/<!--[\s\S]*-->/.test(l)) { comment = true; continue; }
    if (fence) { if (f && f[1][0] === fence[0] && f[1].length >= fence.length && !l.trim().slice(f[1].length)) fence = null; continue; }
    if (f) { fence = f[1]; continue; }
    if (/^:::\s*\S/.test(l)) depth++;
    else if (/^:::\s*$/.test(l)) {
      if (depth === 0) return { inner: lines.slice(1, i).join('\n'), raw: lines.slice(0, i + 1).join('\n') };
      depth--;
    }
  }
  return null;
}

// Where a block may begin inside the remaining text: only after a newline. Marked passes the text from one character
// past the current position, so a match at index 0 would turn mid-line text into a block.
const lineStart = re => s => { const m = new RegExp(`\\n(?=${re.source})`).exec(s); return m ? m.index + 1 : undefined; };
// In a "::: check" block, a list item that opens with a bold question puts the rest of its first line in the answer
// span; any further blocks in the item (a nested list) follow the span.
function checkBody(parser, tokens) {
  return tokens.map(tok => {
    if (tok.type !== 'list') return parser.parse([tok]);
    const items = tok.items.map(item => {
      const [head, ...rest] = item.tokens;
      const inline = head && (head.type === 'text' || head.type === 'paragraph') ? head.tokens || [] : [];
      if (inline[0]?.type !== 'strong') return `<li>${parser.parse(item.tokens)}</li>\n`;
      const answer = parser.parseInline(inline.slice(1)).replace(/^\s+/, '');
      return `<li>${parser.parseInline(inline[0].tokens)} <span class="a">${answer}</span>${rest.length ? parser.parse(rest) : ''}</li>\n`;
    }).join('');
    const tag = tok.ordered ? 'ol' : 'ul', start = tok.ordered && tok.start !== 1 && tok.start !== '' ? ` start="${tok.start}"` : '';
    return `<${tag}${start}>\n${items}</${tag}>\n`;
  }).join('');
}
const md = new Marked({ gfm: true });
md.use({
  // Inside a part, "##" is a numbered section (h3) and "###" a box heading such as "Math 2." (h4).
  renderer: { heading: (text, level) => `<h${level + 1}>${text}</h${level + 1}>\n` },
  extensions: [
    { name: 'mathBlock', level: 'block', start: lineStart(/\$\$/),
      tokenizer(s) { const m = /^\$\$([\s\S]+?)\$\$[ \t]*(?:\n|$)/.exec(s); if (m) return { type: 'mathBlock', raw: m[0], text: m[1] }; },
      renderer: t => tex(t.text, true) + '\n' },
    // Inline math opens on a non-space and closes on a non-space not followed by a digit, so "$100 versus $200" stays text.
    { name: 'mathInline', level: 'inline', start: dollar,
      tokenizer(s) { const m = /^\$(?=\S)([^$\n]*?\S)\$(?!\d)/.exec(s); if (m) return { type: 'mathInline', raw: m[0], text: m[1] }; },
      renderer: t => tex(t.text, false) },
    { name: 'block', level: 'block', start: lineStart(/:::/),
      tokenizer(s) {
        const head = /^::: *(\S[^\n]*)\n/.exec(s); if (!head) return;
        const body = blockBody(s); if (!body) throw new Error(`a ::: block is not closed: "${head[0].trim()}"`);
        const id = (head[1].match(/#([\w-]+)/) || [])[1];
        const raw = body.raw + (s.slice(body.raw.length).startsWith('\n') ? '\n' : '');
        return { type: 'block', raw, cls: head[1].replace(/#[\w-]+/, '').trim(), id, tokens: this.lexer.blockTokens(body.inner, []) };
      },
      renderer(t) {
        const body = t.cls.split(/\s+/).includes('check') ? checkBody(this.parser, t.tokens) : this.parser.parse(t.tokens);
        return `<div class="${attr(t.cls)}"${t.id ? ` id="${t.id}"` : ''}>\n${body}</div>\n`;
      } },
    // An image alone on its line is a figure. "Table 2 [p. 9]: caption" is a paper item; anything else is a diagram
    // caption, such as "Recurrence against self-attention, drawn from Section 1 [p. 2]".
    { name: 'figure', level: 'block', start: lineStart(/!\[/),
      tokenizer(s) {
        const m = /^!\[(.+)\]\((\S+)\)[ \t]*(?:\n|$)/.exec(s); if (!m) return;
        const item = m[1].match(new RegExp(`^(${LABEL}) (\\[(?:pp?\\.|§) [^\\]]+\\]): ([\\s\\S]*)$`));
        const caption = item ? item[3] : m[1];
        const alt = item ? `${item[1]} from the paper` : m[1].replace(/\s*\[[^\]]*\]/g, '').replace(/[`$]/g, '');
        return { type: 'figure', raw: m[0], src: m[2], alt, label: item ? `${item[1]} ${item[2]}` : '', tokens: this.lexer.inlineTokens(caption, []) };
      },
      renderer(t) {
        const cap = (t.label ? `<b>${t.label}:</b> ` : '') + this.parser.parseInline(t.tokens);
        return `<figure style="margin:0">\n<img src="${attr(t.src)}" alt="${attr(t.alt)}">\n<div class="cap">${cap}</div>\n</figure>\n`;
      } },
    { name: 'question', level: 'block', start: lineStart(/Question: /),
      tokenizer(s) { const m = /^Question: ([^\n]+)(?:\n|$)/.exec(s); if (m) return { type: 'question', raw: m[0], tokens: this.lexer.inlineTokens(m[1], []) }; },
      renderer(t) { return `<p class="question">${this.parser.parseInline(t.tokens)}</p>\n`; } },
  ],
});

const tokens = md.lexer(readFileSync(input, 'utf8').replace(/\r\n/g, '\n'));
// "# Part 3. Title" opens the part; "# Title {#id}" opens a named section such as the metrics.
const first = tokens.findIndex(t => t.type === 'heading');
if (first < 0 || tokens[first].depth !== 1) throw new Error('start the file with "# Part N. Title" or "# Title {#id}"');
const [title] = tokens.splice(first, 1);
const named = title.text.match(/^(.*?)\s*\{#([\w-]+)\}$/), part = title.text.match(/^Part (\d+)\./);
const id = named ? named[2] : part ? `p${part[1]}` : null;
if (!id) throw new Error(`the first heading must be "# Part N. Title" or "# Title {#id}": ${title.text}`);
const open = `<section class="part" id="${id}">\n<h2>${md.parseInline(named ? named[1] : title.text)}</h2>\n`;

let html = md.parser(tokens);
html = html.replace(/<table>/g, '<table class="t">');
// Answer spans are built only for a "::: check" block; a hand-written <div class="check"> would lose them silently.
if (/<div class="check">[\s\S]*?<li><strong>/.test(html)) throw new Error('write the reflection questions as a "::: check" block, not as raw HTML');
const out = `${open}${html}</section>\n`;
const opened = (out.match(/<div\b/g) || []).length, closed = (out.match(/<\/div>/g) || []).length;
if (opened !== closed) throw new Error(`${opened} <div> but ${closed} </div>: a ::: block is not closed`);
writeFileSync(output, out);
console.log(`${output}: ${(out.match(/<math\b/g) || []).length} formulas`);
