#!/usr/bin/env python3
"""Shared helpers: BibTeX parsing, LaTeX decoding, normalisation, cited-key inventory.

CLI:  python3 bibtools.py inventory main_ref.bib file1.tex [file2.tex ...]
"""
import re, sys, unicodedata, html

# ---------------------------------------------------------------- bib parsing
def _read_braced(s, i):
    """s[i] == '{' -> (content, index after closing brace)."""
    depth, j = 1, i + 1
    while j < len(s) and depth:
        if s[j] == '\\':
            j += 2; continue
        if s[j] == '{': depth += 1
        elif s[j] == '}': depth -= 1
        j += 1
    return s[i + 1:j - 1], j

def _read_quoted(s, i):
    j, depth = i + 1, 0
    while j < len(s):
        c = s[j]
        if c == '\\': j += 2; continue
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        elif c == '"' and depth == 0: break
        j += 1
    return s[i + 1:j], j + 1

def parse_bib(path):
    """Return {key: {'_type': type, field: raw_value, ...}} in file order."""
    s = open(path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'@(\w+)\s*([{(])', s):
        typ = m.group(1).lower()
        if typ in ('comment', 'preamble', 'string'):
            continue
        i = m.end()
        km = re.match(r'\s*([^,\s]+)\s*,', s[i:])
        if not km:
            continue
        key = km.group(1); i += km.end()
        f = {'_type': typ}
        while True:
            fm = re.match(r'\s*(\w[\w-]*)\s*=\s*', s[i:])
            if not fm:
                break
            name = fm.group(1).lower(); i += fm.end()
            parts = []
            while True:  # value may be concatenation with #
                while s[i].isspace(): i += 1
                if s[i] == '{':
                    v, i = _read_braced(s, i)
                elif s[i] == '"':
                    v, i = _read_quoted(s, i)
                else:
                    vm = re.match(r'[^,#}\s]+', s[i:]); v = vm.group(0); i += vm.end()
                parts.append(v)
                while i < len(s) and s[i].isspace(): i += 1
                if i < len(s) and s[i] == '#':
                    i += 1; continue
                break
            f[name] = ''.join(parts)
            while i < len(s) and s[i].isspace(): i += 1
            if i < len(s) and s[i] == ',':
                i += 1; continue
            break
        out[key] = f
    return out

def split_names(v):
    return [n.strip() for n in re.split(r'\s+and\s+', re.sub(r'\s+', ' ', v.strip())) if n.strip()]

# ------------------------------------------------------------ LaTeX decoding
_ACC = {"'": '\u0301', '`': '\u0300', '"': '\u0308', '^': '\u0302', '~': '\u0303',
        '=': '\u0304', '.': '\u0307', 'c': '\u0327', 'v': '\u030c', 'u': '\u0306',
        'H': '\u030b', 'k': '\u0328', 'r': '\u030a'}
_MACROS = {r'\i': 'ı', r'\j': 'ȷ', r'\o': 'ø', r'\O': 'Ø', r'\l': 'ł', r'\L': 'Ł', r'\ss': 'ß',
           r'\ae': 'æ', r'\AE': 'Æ', r'\oe': 'œ', r'\OE': 'Œ', r'\aa': 'å', r'\AA': 'Å',
           r'\&': '&', r'\_': '_', r'\%': '%', r'\$': '$', r'\#': '#', r'\textendash': '–',
           r'\textemdash': '—', r'\textquoteright': '’'}

def latex_to_text(v):
    v = re.sub(r'\\url\{([^}]*)\}', r'\1', v)
    try:
        from pylatexenc.latex2text import LatexNodes2Text
        t = LatexNodes2Text(math_mode='verbatim', strict_latex_spaces=True).latex_to_text(v)
    except Exception:
        t = v
        t = re.sub(r'\\url\{([^}]*)\}', r'\1', t)
        for a, c in _ACC.items():
            t = re.sub(r'\\' + re.escape(a) + r'\s*\{?\s*(\\[ij]|[A-Za-z])\s*\}?',
                       lambda m: (_MACROS.get(m.group(1), m.group(1))) + c, t)
        for k in sorted(_MACROS, key=len, reverse=True):
            t = re.sub(re.escape(k) + r'(?![A-Za-z])\s?', _MACROS[k], t)
        t = t.replace('---', '—').replace('--', '–').replace('``', '“').replace("''", '”')
        t = t.replace('{', '').replace('}', '').replace('~', ' ')
    return unicodedata.normalize('NFC', t)

def norm(t, loose=False):
    """Normalise for literal comparison (allowed differences only)."""
    t = html.unescape(t)
    t = unicodedata.normalize('NFC', t)
    t = (t.replace('\u2010', '-').replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
          .replace('--', '-').replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"')
          .replace('\u201d', '"').replace('\u00a0', ' ').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
          .replace('ﬀ', 'ff').replace('ﬃ', 'ffi'))
    t = re.sub(r'<[^>]+>', ' ', t) if loose else t
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def name_variants(name):
    """'Last, First' / 'First Last' -> set of normalised display forms."""
    n = norm(latex_to_text(name))
    out = {n}
    if ',' in n:
        parts = [p.strip() for p in n.split(',')]
        if len(parts) == 2:
            out.add(f'{parts[1]} {parts[0]}')
        elif len(parts) == 3:  # von Last, Jr, First
            out.add(f'{parts[2]} {parts[0]} {parts[1]}'); out.add(f'{parts[2]} {parts[0]}, {parts[1]}')
    return out

def bibtex_last(name):
    """Approximate BibTeX's last-name parse (for checking splits like 'Van Durme')."""
    n = re.sub(r'\s+', ' ', name.strip())
    if ',' in n:
        return n.split(',')[0].strip()
    toks, depth, cur = [], 0, ''
    for ch in n:  # split on spaces outside braces
        if ch == '{': depth += 1
        if ch == '}': depth -= 1
        if ch == ' ' and depth == 0:
            toks.append(cur); cur = ''
        else:
            cur += ch
    toks.append(cur)
    if len(toks) == 1:
        return toks[0]
    # von part: first lowercase-initial token (not first) to end
    for k in range(1, len(toks) - 1):
        if toks[k][:1].islower():
            return ' '.join(toks[k:])
    return toks[-1]

# ------------------------------------------------------------- tex helpers
def strip_comments(s):
    return '\n'.join(re.sub(r'(?<!\\)%.*', '', l) for l in s.split('\n'))

CITE_RE = re.compile(r'\\(?:[cC]ite\w*|[pP]arencite|[tT]extcite|nocite)\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}')

def cited_keys(tex_paths):
    keys = {}
    for p in tex_paths:
        s = strip_comments(open(p, encoding='utf-8').read())
        for m in CITE_RE.finditer(s):
            for k in m.group(1).split(','):
                k = k.strip()
                if k and k != '*':
                    keys.setdefault(k, set()).add(p)
    return keys

def inventory(bib, texs):
    b = parse_bib(bib)
    c = cited_keys(texs)
    nf = sum(len(f) - 1 for f in b.values())
    print(f'bib entries: {len(b)}  fields: {nf}')
    print(f'cited keys: {len(c)}')
    print('cited but missing from bib:', sorted(set(c) - set(b)) or 'none')
    print('in bib but not cited:', sorted(set(b) - set(c)) or 'none')
    dup = [k for k in b if list(b).count(k) > 1]
    if dup: print('duplicate keys:', dup)

if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'inventory':
        inventory(sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
