#!/usr/bin/env python3
"""Compare the layout of two builds of the same paper, page by page.

Why: a one-clause rewrite of a citing sentence can add a line, and under a page limit that line
can push the conclusion onto the next page. Build the paper before and after the edit (each from
a clean copy), then run this to see exactly which pages moved.

Usage: layout_diff.py before.pdf after.pdf [--marker "References"] [--show]
  --marker TEXT  also report the first page on which TEXT starts a line in each PDF
                 (e.g. "References", to see where the main text ends)
  --show         print the changed lines of each differing page
Exit code: 0 = same page count, and every page keeps its number of text lines and its last two lines
           1 = page count, a page's line count, or a page's ending changed (inspect those pages)
Needs: pypdf.
"""
import argparse, contextlib, difflib, io, sys
def pages(path):
    from pypdf import PdfReader
    with contextlib.redirect_stderr(io.StringIO()):
        return [[l.rstrip() for l in (p.extract_text() or '').splitlines() if l.strip()] for p in PdfReader(path).pages]
def first_page(pp, marker):
    for i, lines in enumerate(pp, 1):
        if any(l.strip().startswith(marker) for l in lines): return i
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('before'); ap.add_argument('after'); ap.add_argument('--marker'); ap.add_argument('--show', action='store_true')
    a = ap.parse_args(); A, B = pages(a.before), pages(a.after); moved = len(A) != len(B)
    print(f'pages: {len(A)} -> {len(B)}' + ('' if len(A) == len(B) else '   <-- PAGE COUNT CHANGED'))
    if a.marker:
        x, y = first_page(A, a.marker), first_page(B, a.marker)
        print(f'"{a.marker}" first starts a line on page: {x} -> {y}' + ('' if x == y else '   <-- MOVED')); moved |= x != y
    changed = [i for i in range(min(len(A), len(B))) if A[i] != B[i]]
    for i in changed:
        same_n = len(A[i]) == len(B[i]); moved |= not same_n
        same_end = A[i][-2:] == B[i][-2:]; moved |= not same_end   # a different page end means text crossed a page break
        tail = 'page ends the same' if same_end else 'PAGE END DIFFERS'
        print(f'page {i + 1}: lines {len(A[i])} -> {len(B[i])}{"" if same_n else "   <-- LINE COUNT CHANGED"}; {tail}')
        if a.show:
            for l in difflib.unified_diff(A[i], B[i], 'before', 'after', lineterm='', n=0):
                if not l.startswith(('---', '+++', '@@')): print('    ' + l)
    if not changed and len(A) == len(B): print('text identical on every page')
    print('RESULT:', 'layout changed' if moved else f'layout unchanged ({len(changed)} page(s) with reflowed text only)')
    sys.exit(1 if moved else 0)
if __name__ == '__main__': main()
