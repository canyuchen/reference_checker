#!/usr/bin/env python3
"""List every sentence that makes a claim about cited works, for the claims audit.

Usage:
  python3 cite_sentences.py main.tex [checklist.tex ...] --bib main_ref.bib [--out sentences.tsv]

Output rows (TSV): file, line, kind, keys_or_names, sentence
  kind = cite      sentence contains \\cite
         followup  sentence right after a cite sentence that starts with a pronoun / "This work" etc.
         name      no \\cite, but names a cited work (name = title prefix before ':' in the bib, or
                   an acronym in the title) — e.g. "unlike VLBiasBench"
         strong    no \\cite, but uses first/only/unlike/uniquely/most ... (check for counterexamples)
Sentences that only describe the paper's own design can be dropped by hand afterwards.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bibtools import parse_bib, latex_to_text, CITE_RE

STRONG = re.compile(r'\b(the first|first (?:to|benchmark|work|study|dataset|attempt|systematic)|the only|only (?:benchmark|work|study|dataset|one|existing)|'
                    r'unlike|uniquely|unique(?:ly)?|pioneer\w*|unprecedented|most (?:comprehensive|extensive|complete)|'
                    r'no (?:prior|previous|existing) (?:work|study|benchmark|dataset)s?|none of (?:the|these)|(?:the )?largest|'
                    r'(?:prior|previous|existing) (?:work|benchmarks?|studies) (?:fail|ignore|overlook|cannot|do not|lack))\b', re.I)
FOLLOW = re.compile(r'^(They|Their|It|Its|This (?:work|study|benchmark|paper|dataset|method)|These|The authors|'
                    r'The (?:benchmark|dataset|study|method))\b')
SKIP_ENVS = r'(?:figure|table|tabular|equation|align|lstlisting|verbatim|tikzpicture)\*?'

def blank_comments(s):
    out = []
    for line in s.split('\n'):
        m = re.search(r'(?<!\\)%', line)
        out.append(line if not m else line[:m.start()] + ' ' * (len(line) - m.start()))
    return '\n'.join(out)

def work_names(bib):
    names = {}
    for k, e in bib.items():
        t = latex_to_text(e.get('title', ''))
        m = re.match(r'\s*([^:]{2,40}):', t)
        if m and len(m.group(1).split()) <= 4:
            names.setdefault(m.group(1).strip(), set()).add(k)
        for ac in re.findall(r'\b([A-Z][A-Za-z]*[A-Z][A-Za-z0-9-]*)\b', t):
            if len(ac) >= 3 and ac.upper() != ac.lower():
                names.setdefault(ac, set()).add(k)
    # drop generic tokens
    for g in ['LLM', 'LLMs', 'VLM', 'VLMs', 'MLLM', 'MLLMs', 'NLP', 'QA', 'AI', 'LVLM', 'LVLMs', 'GPT', 'BERT']:
        names.pop(g, None)
    return names

def sentences(text):
    """yield (start_offset, sentence) on a comment-blanked string."""
    t = re.sub(r'\\begin\{' + SKIP_ENVS + r'\}.*?\\end\{' + SKIP_ENVS + r'\}', lambda m: ' ' * len(m.group(0)), text, flags=re.S)
    t = re.sub(r'\\(?:sub)*section\*?\{[^}]*\}|\\paragraph\*?\{(?:[^{}]|\{[^{}]*\})*\}|\\item\b|\\(?:begin|end)\{\w+\*?\}',
               lambda m: ' ' * len(m.group(0)), t)
    start = 0
    for m in re.finditer(r'(?<=[.!?])(?:\}|\))?\s+(?=[A-Z\\{(])|\n\s*\n', t):
        seg = t[start:m.start()]
        if seg.strip():
            yield start + (len(seg) - len(seg.lstrip())), re.sub(r'\s+', ' ', seg).strip()
        start = m.end()
    seg = t[start:]
    if seg.strip():
        yield start + (len(seg) - len(seg.lstrip())), re.sub(r'\s+', ' ', seg).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tex', nargs='+'); ap.add_argument('--bib', required=True)
    ap.add_argument('--out', default='sentences.tsv')
    a = ap.parse_args()
    names = work_names(parse_bib(a.bib))
    name_re = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, names), key=len, reverse=True)) + r')\b') if names else None
    rows = []
    for path in a.tex:
        raw = open(path, encoding='utf-8').read()
        text = blank_comments(raw)
        prev_cite = False
        for off, s in sentences(text):
            line = raw.count('\n', 0, off) + 1
            keys = [k.strip() for m in CITE_RE.finditer(s) for k in m.group(1).split(',') if k.strip()]
            if keys:
                rows.append((path, line, 'cite', ','.join(dict.fromkeys(keys)), s)); prev_cite = True; continue
            hit = sorted(set(name_re.findall(s))) if name_re else []
            if prev_cite and FOLLOW.match(s):
                rows.append((path, line, 'followup', '', s))
            elif hit:
                rows.append((path, line, 'name', ','.join(hit), s))
            elif STRONG.search(s):
                rows.append((path, line, 'strong', STRONG.search(s).group(0), s))
            prev_cite = False
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('file\tline\tkind\tkeys_or_names\tsentence\n')
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
    from collections import Counter
    c = Counter(r[2] for r in rows)
    print(f'{len(rows)} sentences -> {a.out}  ' + '  '.join(f'{k}={v}' for k, v in c.items()))

if __name__ == '__main__':
    main()
