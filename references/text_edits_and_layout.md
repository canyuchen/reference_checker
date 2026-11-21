# Changing a citing sentence without breaking the paper

Read this before editing paper text because a claim about a cited work is unsupported. The audit must not create new problems: a rewrite can add a line, and under a page limit one line can push the conclusion onto the next page.

## Choosing the edit

Prefer the smallest change that makes the sentence true to the source, in this order:

1. **Remove the unsupported wording** ("widely used", "first", "single-axis", "most") and keep the rest.
2. **Narrow the scope** so the sentence says only what the source says ("client heterogeneity" → "statistical client heterogeneity").
3. **Move the claim to the authors.** If the statement is the authors' own inference, say so ("We expect …") and keep the citation only on the part the paper supports.
4. **Rewrite from the source wording.**
5. **Drop or replace the citation** when the cited paper is the wrong support.

A sentence with several citations is true only if each cited paper supports its part. When papers differ (one varies transitions only, another transitions and rewards), choose wording that holds for every paper under the citation ("transitions or rewards"), or split the citation.

A claim may be kept unchanged when it is clearly the authors' own statement and the sentence does not attribute it to the cited paper, or when another citation in the same group supports it. Record it as "kept, with reason". Label anything derived by reasoning from the source (for example from its algorithm box) as an inference in the evidence file.

Follow the project's writing rules when there are any (style memories, a `writing_preference/` folder), and check each new sentence against them.

## Checking the layout

For a paper with a page limit, or a camera-ready version:

```bash
scripts/clean_build.sh paper/ work/before          # before the edit
# apply the edit in a copy of the sources (or edit, then build again)
scripts/clean_build.sh paper_edited/ work/after
python3 scripts/layout_diff.py work/before/main.pdf work/after/main.pdf --marker References --show
```

- `clean_build.sh` copies the sources without build products and runs BibTeX fresh. A `main.bbl` left by another build is otherwise reused and the PDF shows references that no longer match the `.bib`.
- `layout_diff.py` exits 0 only if the page count, each page's number of lines, and each page's ending are unchanged. `--marker References` shows where the main text ends.
- If the layout moved, try a shorter wording before anything else. Do not fix a page overflow with spacing commands unless the user asks.
- Also check the build numbers: 0 undefined citations, 0 BibTeX warnings, and the expected number of bibliography entries.

Try the edit in a copy first, and write it to the user's working files only after the layout check passes. Record old sentence → new sentence, the reason, the supporting quotes, and the layout result in the evidence file.

## Other people may be editing the same paper

Other sessions or co-authors (Overleaf) may change the text during or after the audit. Before editing and before reporting, look at `git status`, `git log` and the remote. Edits made after the last audit are not covered by the evidence file until `sync_check.py` passes again.
