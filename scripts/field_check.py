#!/usr/bin/env python3
"""Check every .bib field literally against the fetched records of *that* entry.

Usage:
  python3 field_check.py main_ref.bib records/ [--out provenance.tsv] [--keys k1,k2]

records/<key>/<source>[_suffix].<ext>   (source names and families: references/sources.md)
  .json  -> all string/number values; Crossref/DataCite author objects also as "Given Family"
  .bib   -> fields decoded from LaTeX
  .xml/.html/.htm -> tags stripped, entities decoded
  .txt   -> as is (PDF text, page text)

Per field: the sources whose text contains the value literally (allowed differences only),
then a level: official+multi | official | multi | aggregator-only | rule | NONE.
Exit code 1 if any field is NONE or aggregator-only.
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bibtools import parse_bib, split_names, latex_to_text, norm, name_variants, bibtex_last

OFFICIAL = {'crossref', 'datacite', 'acl', 'arxiv', 'neurips', 'pmlr', 'cvf', 'colm', 'iclr', 'tmlr',
            'springer', 'ijcai', 'aaai', 'acm', 'ieee', 'venue', 'pdf', 'author', 'publisher', 'journal'}
AGGREGATOR = {'dblp', 'openalex', 's2', 'scholar'}
RULE_FIELDS = {'url', 'eprint', 'archiveprefix', 'eprinttype', 'primaryclass'}
SKIP_FIELDS = {'abstract', 'keywords', 'file', 'timestamp', 'biburl', 'bibsource', 'urldate', 'note_internal'}
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
          'october', 'november', 'december']

def source_of(fname):
    stem = os.path.basename(fname).split('.')[0]
    return stem.split('_')[0].lower()

def family(src):
    if src in AGGREGATOR: return 'aggregator'
    if src in OFFICIAL: return 'official'
    return 'unknown'

def _walk_json(o, out, names):
    if isinstance(o, dict):
        g = o.get('given') or o.get('givenName')
        f = o.get('family') or o.get('familyName')
        if isinstance(f, str):
            names.append(f)
            if isinstance(g, str):
                out.append(f'{g} {f}'); out.append(f'{f}, {g}')
        for v in o.values(): _walk_json(v, out, names)
    elif isinstance(o, list):
        for v in o: _walk_json(v, out, names)
    elif isinstance(o, (str, int, float)) and not isinstance(o, bool):
        out.append(str(o))

def load_record(path):
    """-> (normalised text, list of structured family names or None)"""
    ext = path.rsplit('.', 1)[-1].lower()
    raw = open(path, encoding='utf-8', errors='replace').read()
    fams = None
    if ext == 'json':
        try:
            o = json.loads(raw)
        except Exception:
            return norm(raw, loose=True), None
        out, names = [], []
        _walk_json(o, out, names)
        txt, fams = '\n'.join(out), names or None
    elif ext == 'bib':
        parts, fams = [], []
        for e in parse_bib_text(raw).values():
            for k, v in e.items():
                if k == '_type': continue
                dv = latex_to_text(v)
                parts.append(dv)
                if k in ('author', 'editor'):
                    for n in split_names(v):
                        parts.extend(name_variants(n))
                        if k == 'author': fams.append(latex_to_text(bibtex_last(n)))
        txt = '\n'.join(parts)
    elif ext in ('xml', 'html', 'htm'):
        txt = norm(raw, loose=True)
    else:
        txt = raw
    return norm(txt), fams

def parse_bib_text(raw):
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.bib', delete=False, encoding='utf-8') as t:
        t.write(raw); p = t.name
    try:
        return parse_bib(p)
    finally:
        os.unlink(p)

def has(text, val):
    return bool(val) and val in text

def has_token(text, tok):
    return re.search(r'(?<![\w])' + re.escape(tok) + r'(?![\w])', text) is not None

def check_field(field, raw, entry, recs):
    """-> (list of sources with literal hit, note, is_rule)"""
    hits, note = [], ''
    if field in ('author', 'editor'):
        names = split_names(raw)
        for src, (txt, _) in recs.items():
            pos, ok, missing, order_ok = -1, True, [], True
            for n in names:
                if n.lower() == 'others':
                    continue
                vs = [v for v in name_variants(n) if v in txt]
                if not vs:
                    ok = False; missing.append(n); continue
                after = [txt.find(v, pos + 1) for v in vs]
                after = [x for x in after if x >= 0]
                if after:
                    pos = min(after)
                else:
                    order_ok = False
            if ok and order_ok:
                hits.append(src)
            elif ok:
                note += f'{src}: all names present but order differs. '
            elif len(missing) < len(names):
                note += f'{src} lacks: {"; ".join(missing[:3])}{"…" if len(missing) > 3 else ""}. '
        return hits, note.strip(), False
    val = norm(latex_to_text(raw))
    if field == 'doi':
        for src, (txt, _) in recs.items():
            if val.lower() in txt.lower(): hits.append(src)
        return hits, '', False
    if field in RULE_FIELDS:
        doi = norm(latex_to_text(entry.get('doi', ''))).lower()
        epr = norm(entry.get('eprint', ''))
        v = val.lower()
        if field == 'url':
            if doi and v.rstrip('/') in (f'https://doi.org/{doi}', f'http://doi.org/{doi}', f'https://dx.doi.org/{doi}'):
                return ['doi'], 'rule: DOI resolver', True
            if epr and re.fullmatch(r'https?://arxiv\.org/(abs|pdf)/' + re.escape(epr.lower()) + r'(v\d+)?(\.pdf)?', v):
                return ['arxiv-id'], 'rule: arXiv ID', True
        if field == 'eprint':
            for src, (txt, _) in recs.items():
                if has_token(txt, val) or has(txt, val): hits.append(src)
            return hits, 'rule: arXiv ID in record', True
        if field in ('archiveprefix', 'eprinttype') and val.lower() == 'arxiv' and epr:
            return ['arxiv-id'], 'rule: eprint present', True
        for src, (txt, _) in recs.items():
            if has(txt, val): hits.append(src)
        return hits, 'literal URL' if hits else 'not found in any record', bool(hits)
    if field in ('year', 'volume', 'number'):
        for src, (txt, _) in recs.items():
            if has_token(txt, val): hits.append(src)
        return hits, '', False
    if field == 'month':
        m = val.lower()[:3]
        idx = [i for i, x in enumerate(MONTHS) if x.startswith(m)]
        forms = {val}
        if idx:
            i = idx[0]; forms |= {MONTHS[i].capitalize(), MONTHS[i][:3].capitalize(), f'-{i+1:02d}-'}
        for src, (txt, _) in recs.items():
            if any(f in txt for f in forms): hits.append(src)
        return hits, 'content: month name/number', False
    if field == 'pages':
        v = val.replace(' ', '')
        a, _, b = v.partition('-')
        for src, (txt, _) in recs.items():
            t = txt.replace(' ', '')
            if v in t or f'{a}–{b}' in t:
                hits.append(src)
            elif src == 'pdf' and b and has_token(txt, a) and has_token(txt, b):
                hits.append(src); note = 'pdf: both page numbers present (content)'
        return hits, note, False
    # title, booktitle, journal, publisher, series, address, howpublished, note, ...
    cands = {val, val.rstrip('.')}
    for src, (txt, _) in recs.items():
        if any(has(txt, c) for c in cands): hits.append(src)
    if not hits:
        lo = [s for s, (t, _) in recs.items() if any(c.lower() in t.lower() for c in cands)]
        if lo: note = 'case differs in: ' + ', '.join(lo) + ' (not literal)'
    return hits, note, False

def level(hits, is_rule):
    if is_rule and hits:
        return 'rule'
    srcs = set(h for h in hits)
    off = {s for s in srcs if family(s) == 'official'}
    if off and len(srcs) >= 2: return 'official+multi'
    if off: return 'official'
    if len(srcs) >= 2: return 'multi'
    if srcs: return 'aggregator-only'
    return 'NONE'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bib'); ap.add_argument('records')
    ap.add_argument('--out', default='provenance.tsv'); ap.add_argument('--keys')
    a = ap.parse_args()
    bib = parse_bib(a.bib)
    keys = a.keys.split(',') if a.keys else list(bib)
    rows, cnt, bad, splits = [], Counter(), [], []
    for key in keys:
        e = bib[key]
        d = os.path.join(a.records, key)
        recs = {}
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.startswith('.'): continue
                src = source_of(fn)
                txt, fams = load_record(os.path.join(d, fn))
                name = src if src not in recs else f'{src}#{len([r for r in recs if r.split("#")[0] == src]) + 1}'
                recs[name] = (txt, fams)
        if not recs:
            print(f'[no records] {key}', file=sys.stderr)
        # strip '#n' for family/level purposes but keep for listing
        for field, raw in e.items():
            if field == '_type': continue
            if field in SKIP_FIELDS:
                rows.append((key, field, raw[:80], 'REMOVE?', '', 'non-bibliographic field')); cnt['REMOVE?'] += 1; continue
            hits, note, is_rule = check_field(field, raw, e, recs)
            base = sorted(set(h.split('#')[0] for h in hits))
            lv = level(base, is_rule)
            cnt[lv] += 1
            rows.append((key, field, re.sub(r'\s+', ' ', raw), lv, ', '.join(base), note))
            if lv in ('NONE', 'aggregator-only'): bad.append(rows[-1])
        # name-split check against structured family names
        if 'author' in e:
            bl = [latex_to_text(bibtex_last(n)) for n in split_names(e['author']) if n.lower() != 'others']
            for src, (_, fams) in recs.items():
                if fams and len(fams) >= len(bl):
                    diff = [(x, y) for x, y in zip(bl, fams) if norm(x) != norm(y)]
                    if diff:
                        splits.append((key, src, diff[:4]))
                    break
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('key\tfield\tvalue\tlevel\tsources\tnote\n')
        for r in rows: f.write('\t'.join(r) + '\n')
    print(f'fields: {sum(cnt.values())}  ' + '  '.join(f'{k}={v}' for k, v in cnt.most_common()))
    print(f'provenance -> {a.out}')
    if bad:
        print('\nNeeds action (NONE / aggregator-only):')
        for r in bad: print(f'  {r[0]}.{r[1]} [{r[3]}] {r[2][:90]}  {r[5]}')
    if splits:
        print('\nLast-name parse differs from structured record (check BibTeX name split):')
        for k, s, d in splits: print(f'  {k} vs {s}: ' + '; '.join(f'bib={x!r} src={y!r}' for x, y in d))
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
