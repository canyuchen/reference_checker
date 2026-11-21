#!/usr/bin/env python3
"""Printed-byline check: compare a bib entry's title and authors with the first pages of the cited PDF.

Why: metadata (arXiv, Crossref, OpenReview profiles, dblp) often differs from what the paper prints:
dropped or reordered authors, profile-name variants, missing accents. The printed byline of the
version that the bib cites is the reference for author names.

Usage:
  pdf_byline.py refs.bib --pdf KEY=paper.pdf [--pdf KEY2=other.pdf ...]
  pdf_byline.py refs.bib --map map.tsv            # lines: KEY<TAB>path/to.pdf
  options: --pages N (default 2)   --json out.json

Per entry it reports
  title      bib title found in the PDF text (case/punctuation/accents ignored)
  order      every bib author found, in bib order, before the abstract
  missing    bib authors whose surname is not on the first pages
  fullname   surname printed, but the full name as written in the bib is not
  accents    same letters, different diacritics or casing (bib vs printed)
Exit code 1 if any entry has a finding.

Findings are leads to look at by eye, not verdicts. Text extraction breaks on superscripts,
small caps, names split by affiliation marks, and scanned or oddly encoded PDFs. A printed typo
is not copied into the bib; record it in the evidence file instead.
Needs: pypdf (pip install pypdf).
"""
import argparse, contextlib, io, json, re, sys, unicodedata

def parse_bib(path):
    txt = open(path, encoding='utf-8').read(); out = {}; i = 0
    while True:
        m = re.compile(r'@(\w+)\s*\{').search(txt, i)
        if not m: break
        j = m.end(); depth = 1
        while depth and j < len(txt):
            depth += {'{': 1, '}': -1}.get(txt[j], 0); j += 1
        body = txt[m.end():j - 1]; i = j
        if m.group(1).lower() in ('comment', 'string', 'preamble') or ',' not in body: continue
        key, rest = body.split(',', 1); fields = {}; k = 0
        while k < len(rest):
            fm = re.compile(r'\s*([A-Za-z_\-]+)\s*=\s*').match(rest, k)
            if not fm: k += 1; continue
            name = fm.group(1).lower(); k = fm.end()
            if k >= len(rest): break
            if rest[k] == '{':
                d = 1; s = k + 1; k += 1
                while d and k < len(rest):
                    d += {'{': 1, '}': -1}.get(rest[k], 0); k += 1
                val = rest[s:k - 1]
            elif rest[k] == '"':
                s = k + 1; k = rest.index('"', s) + 1; val = rest[s:k - 1]
            else:
                vm = re.compile(r'[^,\s}]+').match(rest, k); val = vm.group(0) if vm else ''; k = vm.end() if vm else k + 1
            fields[name] = re.sub(r'\s+', ' ', val).strip()
        out[key.strip()] = fields
    return out

CMB = {"'": '\u0301', '`': '\u0300', '^': '\u0302', '"': '\u0308', '~': '\u0303', '=': '\u0304', '.': '\u0307',
       'u': '\u0306', 'v': '\u030c', 'H': '\u030b', 'c': '\u0327', 'k': '\u0328', 'r': '\u030a'}
def tex2uni(s):
    """LaTeX accents -> Unicode (NFC)."""
    s = re.sub(r'\\i(?![A-Za-z])', 'ı', s).replace('{-}', '-')
    acc = lambda m: ('i' if m.group(2) == 'ı' else m.group(2)) + CMB[m.group(1)]
    s = re.sub(r"\\([`'^\"~=.uvHckr])\s*\{\s*\\?([A-Za-zı])\s*\}", acc, s)
    s = re.sub(r"\\([`'^\"~=.])\s*([A-Za-zı])", acc, s)
    s = re.sub(r'\\([uvHckr])\s+([A-Za-zı])', acc, s)
    for a, b in (('\\o', 'ø'), ('\\O', 'Ø'), ('\\l', 'ł'), ('\\L', 'Ł'), ('\\ss', 'ß'), ('\\ae', 'æ'), ('\\aa', 'å'), ('\\&', '&')):
        s = re.sub(re.escape(a) + r'(?![A-Za-z])', b, s)
    s = re.sub(r'[{}]', '', s).replace('~', ' ')
    return unicodedata.normalize('NFC', re.sub(r'\s+', ' ', s).strip())
EXTRA = str.maketrans({'ı': 'i', 'ø': 'o', 'Ø': 'O', 'ł': 'l', 'Ł': 'L', 'ß': 'ss', 'æ': 'ae', 'å': 'a', 'đ': 'd'})
def fold(s):  # accent- and case-insensitive, keeps spaces and punctuation
    return unicodedata.normalize('NFKD', s.translate(EXTRA)).encode('ascii', 'ignore').decode().lower()
def flat(s):  # letters and digits only
    return re.sub(r'[^a-z0-9]', '', fold(s))
def split0(s, sep):
    """Split on sep at brace depth 0."""
    parts, d, cur, i = [], 0, '', 0
    while i < len(s):
        if s[i] == '{': d += 1
        elif s[i] == '}': d -= 1
        if d == 0 and s.startswith(sep, i): parts.append(cur); cur = ''; i += len(sep); continue
        cur += s[i]; i += 1
    return parts + [cur]
def authors(raw):
    """[(first, last)] in bib order; a fully braced name such as {DeepSeek-AI} is one corporate author."""
    out = []
    for a in split0(re.sub(r'\s+', ' ', raw or '').strip(), ' and '):
        a = a.strip()
        if not a or a.lower() == 'others': continue
        if ',' in a and len(split0(a, ',')) > 1:
            last, first = [x.strip() for x in split0(a, ',')[:2]]
        elif len(split0(a, ' ')) == 1: last, first = a, ''
        else:
            p = split0(a, ' '); last, first = p[-1], ' '.join(p[:-1])
        out.append((tex2uni(first), tex2uni(last)))
    return out
SPACING = {'\u00b4': '\u0301', '`': '\u0300', '\u02c6': '\u0302', '\u00a8': '\u0308', '\u02dc': '\u0303', '\u00af': '\u0304',
           '\u02d9': '\u0307', '\u02d8': '\u0306', '\u02c7': '\u030c', '\u02dd': '\u030b', '\u00b8': '\u0327', '\u02db': '\u0328', '\u02da': '\u030a'}
def pdf_text(path, pages):
    from pypdf import PdfReader
    with contextlib.redirect_stderr(io.StringIO()):
        rd = PdfReader(path); t = ' '.join((rd.pages[i].extract_text() or '') for i in range(min(pages, len(rd.pages))))
    t = re.sub(r'-\s*\n\s*', '', t)
    # pypdf emits a spacing accent before the letter it belongs to; re-attach it
    t = re.sub('([' + ''.join(SPACING) + r'])\s?([A-Za-zı])', lambda m: ('i' if m.group(2) == 'ı' else m.group(2)) + SPACING[m.group(1)], t)
    return unicodedata.normalize('NFC', re.sub(r'\s+', ' ', t))

def check(fields, path, pages):
    t = pdf_text(path, pages)
    m = re.search(r'\babstract\b', t, re.I)
    head = t[:m.start()] if m and m.start() > 40 else t[:3000]
    fa, fh = flat(t), flat(head)
    res = dict(title=flat(tex2uni(fields.get('title', ''))) in fa, order=True, missing=[], fullname=[], accents=[])
    pos = 0
    for first, last in authors(fields.get('author', '')):
        full = (first + ' ' + last).strip(); ff, fl = flat(full), flat(last)
        q = fh.find(ff, pos); n = len(ff)
        if q < 0: q = fh.find(fl, pos); n = len(fl)
        if q >= 0: pos = q + n
        elif ff in fa or fl in fa: res['order'] = False
        else: res['missing'].append(full)
        if fl in fa and ff not in fa: res['fullname'].append(full)
        if full.lower() not in head.lower():
            # same folded spelling printed with different diacritics/casing?
            hf, pmap = '', []
            for j, ch in enumerate(head):
                fc = fold(ch); hf += fc; pmap += [j] * len(fc)
            i = hf.find(fold(full))
            if i >= 0:
                printed = head[pmap[i]:pmap[i + len(fold(full)) - 1] + 1]
                if printed.lower() != full.lower(): res['accents'].append((full, printed))
    if res['missing']: res['order'] = False
    res['n_authors'] = len(authors(fields.get('author', '')))
    res['ok'] = res['title'] and res['order'] and not res['fullname'] and not res['accents']
    return res

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bib'); ap.add_argument('--pdf', action='append', default=[]); ap.add_argument('--map')
    ap.add_argument('--pages', type=int, default=2); ap.add_argument('--json')
    a = ap.parse_args()
    bib = parse_bib(a.bib); pairs = [p.split('=', 1) for p in a.pdf]
    if a.map: pairs += [l.rstrip('\n').split('\t')[:2] for l in open(a.map, encoding='utf-8') if l.strip() and not l.startswith('#')]
    out = {}; bad = 0
    for key, path in pairs:
        if key not in bib: print(f'{key}: NOT IN BIB'); bad += 1; continue
        try: r = check(bib[key], path, a.pages)
        except Exception as ex: print(f'{key}: could not read {path}: {ex}'); out[key] = dict(error=str(ex)); bad += 1; continue
        out[key] = r
        if r['ok']: print(f"{key}: OK (title + {r['n_authors']} authors in order)")
        else:
            bad += 1
            print(f"{key}: CHECK  title={'found' if r['title'] else 'NOT FOUND'}  order={'ok' if r['order'] else 'DIFFERS'}"
                  + (f"  missing={r['missing']}" if r['missing'] else '') + (f"  fullname_not_printed={r['fullname']}" if r['fullname'] else '')
                  + (''.join(f'  accents: bib "{b}" vs printed "{p}"' for b, p in r['accents'])))
    if a.json: json.dump(out, open(a.json, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{len(pairs) - bad} ok, {bad} to inspect, {len(pairs)} checked')
    sys.exit(1 if bad else 0)
if __name__ == '__main__': main()
