#!/usr/bin/env python3
"""Verify that every quote in a claims table appears verbatim in the saved source text.

Usage:
  python3 quote_check.py claims.tsv [--texts fulltext/]

claims.tsv columns (header row required): key, sentence, claim, verdict, quote, source_url, source_file
  - quote: one or more quotes separated by ' / ' (each checked separately)
  - source_file: path to the saved text (abstract or full text); if empty, tries <texts>/<key>.txt
  - verdict: abstract | fulltext | unsupported | rewritten | own | authors
Rows with verdict 'own' or 'authors' need no quote.

Matching ignores whitespace, line-break hyphenation, ligatures, quote/dash style and case of
nothing else. Exit code 1 if any quote is not found.
"""
import argparse, csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bibtools import norm

def canon(t):
    t = norm(t, loose=True)
    t = re.sub(r'(\w)- (\w)', r'\1\2', t)        # hyphenation across line breaks
    t = re.sub(r'[\s]+', ' ', t)
    return t

def squeeze(t):
    return re.sub(r'\W+', '', t).lower()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('claims'); ap.add_argument('--texts', default='fulltext')
    a = ap.parse_args()
    cache, bad, n = {}, [], 0
    with open(a.claims, encoding='utf-8') as f:
        for i, r in enumerate(csv.DictReader(f, delimiter='\t'), 2):
            verdict = (r.get('verdict') or '').strip().lower()
            if verdict in ('own', 'authors') and not (r.get('quote') or '').strip():
                continue
            src = (r.get('source_file') or '').strip() or os.path.join(a.texts, r['key'] + '.txt')
            if src not in cache:
                cache[src] = canon(open(src, encoding='utf-8', errors='replace').read()) if os.path.exists(src) else None
            text = cache[src]
            for q in [q.strip().strip('“”"') for q in (r.get('quote') or '').split(' / ') if q.strip()]:
                n += 1
                if text is None:
                    bad.append((i, r['key'], q, f'missing source file {src}')); continue
                cq = canon(q)
                if cq in text:
                    continue
                if squeeze(cq) and squeeze(cq) in squeeze(text):
                    bad.append((i, r['key'], q, 'found only after removing punctuation/spaces (PDF extraction?) — check by eye'))
                else:
                    bad.append((i, r['key'], q, 'NOT FOUND'))
    print(f'quotes checked: {n}  problems: {len(bad)}')
    for i, k, q, why in bad:
        print(f'  row {i} {k}: {why}\n     “{q[:160]}”')
    sys.exit(1 if any(b[3] != 'found only after removing punctuation/spaces (PDF extraction?) — check by eye' for b in bad) else 0)

if __name__ == '__main__':
    main()
