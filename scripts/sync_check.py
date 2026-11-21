#!/usr/bin/env python3
"""Check that the bib, the paper text and the evidence Markdown still agree.

Usage:
  python3 sync_check.py main_ref.bib references_evidence.md main.tex [checklist.tex ...]

Reports:
  1. cited keys missing from the bib or from the MD
  2. bib fields whose value differs from the MD field table, or that the MD does not list
  3. citing sentences whose text is not recorded verbatim in the MD (edited after the audit)
MD format expected: a heading line containing `key` in backticks, followed by a
'| field | value | basis |' table; current sentences quoted as '> ...' lines (see
references/evidence_md.md). Exit code 1 if anything is out of sync.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bibtools import parse_bib, latex_to_text, norm, split_names, cited_keys, CITE_RE
from cite_sentences import blank_comments, sentences

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

def md_tables(md):
    """key -> {field: value} from the first field table after a heading naming the key."""
    out = {}
    for m in re.finditer(r'^#{2,4} [^\n]*?`([^`]+)`[^\n]*\n(.*?)(?=^#{2,4} )', md + '\n## END\n', re.S | re.M):
        key, body = m.group(1), m.group(2)
        rows = {}
        for line in body.splitlines():
            r = re.match(r'\|\s*([a-zA-Z]+)\s*\|\s*(.*?)\s*\|\s*(.*)\|\s*$', line)
            if r and r.group(1).lower() not in ('field', '字段'):
                rows[r.group(1).lower()] = r.group(2).replace('\\|', '|')
        if rows and key not in out:
            out[key] = rows
    return out

def cmp_val(field, bibval, mdval):
    if field in ('author', 'editor'):
        a = [norm(latex_to_text(n)) for n in split_names(bibval)]
        sep = r';\s*' if ';' in mdval else r'\s+and\s+'  # MD may list names as 'A; B' or as in the bib, 'A and B'
        b = [norm(x) for x in re.split(sep, mdval)]
        trunc = re.search(r'(…|\.\.\.)', mdval)
        if trunc:
            b = [x for x in b if x and '…' not in x and '...' not in x]
            last = re.split(r'\s*(?:…|\.\.\.)', re.split(r';\s*', mdval)[len(b)] if len(re.split(r';\s*', mdval)) > len(b) else '')[0]
            if last.strip(): b.append(norm(last))
            num = re.search(r'(\d+)', mdval[trunc.start():])
            return a[:len(b)] == b and (not num or int(num.group(1)) == len(a))
        return a == b
    x, y = norm(latex_to_text(bibval)), norm(latex_to_text(mdval))
    if field == 'month':
        x, y = x.lower()[:3], y.lower()[:3]
    if field == 'doi':
        x, y = x.lower(), y.lower()
    if y.endswith('…') or y.endswith('...'):  # MD shortened a long value
        return x.startswith(y.rstrip('….').rstrip(', '))
    return x == y

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    bibp, mdp, texs = sys.argv[1], sys.argv[2], sys.argv[3:]
    bib, md = parse_bib(bibp), open(mdp, encoding='utf-8').read()
    tables = md_tables(md)
    problems = 0
    cited = cited_keys(texs)
    miss_bib = sorted(set(cited) - set(bib)); miss_md = sorted(set(cited) - set(tables))
    print(f'cited keys: {len(cited)}; bib entries: {len(bib)}; MD entries with field tables: {len(tables)}')
    if miss_bib: print('  cited but not in bib:', miss_bib); problems += len(miss_bib)
    if miss_md: print('  cited but no MD entry:', miss_md); problems += len(miss_md)
    diffs, unlisted, n = [], [], 0
    for k, e in bib.items():
        t = tables.get(k)
        if t is None:
            continue
        for f, v in e.items():
            if f == '_type': continue
            n += 1
            if f not in t: unlisted.append((k, f)); continue
            if not cmp_val(f, v, t[f]): diffs.append((k, f, v, t[f]))
    print(f'bib fields compared with MD: {n}; differ: {len(diffs)}; not listed in MD: {len(unlisted)}')
    for k, f, v, w in diffs: print(f'  {k}.{f}\n     bib: {re.sub(chr(10)," ",v)[:150]}\n     md : {w[:150]}')
    for k, f in unlisted: print(f'  {k}.{f} not in MD table')
    problems += len(diffs) + len(unlisted)
    # sentences
    mdn = norm(re.sub(r'^>\s?', '', md, flags=re.M))
    total, stale = 0, []
    for p in texs:
        raw = open(p, encoding='utf-8').read()
        for off, s in sentences(blank_comments(raw)):
            if not CITE_RE.search(s): continue
            total += 1
            if norm(s) not in mdn:  # the whole sentence, so an edit anywhere in it is caught
                stale.append((p, raw.count('\n', 0, off) + 1, s))
    print(f'citing sentences: {total}; not recorded verbatim in MD: {len(stale)}')
    for p, l, s in stale: print(f'  {os.path.basename(p)}:{l}  {s[:300]}')
    problems += len(stale)
    print('IN SYNC' if not problems else f'OUT OF SYNC ({problems} items)')
    sys.exit(1 if problems else 0)

if __name__ == '__main__':
    main()
