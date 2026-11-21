---
name: reference-audit
description: Audit a LaTeX paper's references so that every .bib field is verified against official or multiple fetched sources (no hallucinated metadata), every sentence that cites or describes a cited work matches the original paper, and all evidence is written to a Markdown record. Use when the user asks to check, verify, clean or "de-hallucinate" a bibliography or citations, asks whether references are correct / have a basis ("有依据吗", "没有 hallucination", "机械验证", "多方验证"), adds new citations to a paper, or prepares a camera-ready / arXiv version.
---

# Reference audit

Goal: every field in the references has a verifiable basis — an official record or several sources compared mechanically; uncertain and unimportant fields are left out; every place the paper cites a work is appropriate and matches the original paper; everything is recorded in Markdown.

Three deliverables, all required:
1. **Bib**: every kept field is literally present in a fetched record for *that* paper, and that record is official or confirmed by a second independent source.
2. **Claims**: every sentence that cites a work, or names / refers back to a cited work without `\cite`, is supported by a verbatim quote from that work's abstract or full text, or is rewritten from the source wording.
3. **Evidence MD**: one Markdown file that records, per entry, each field's value and source, and per citing sentence, each claim with its verbatim quote and the source link. Template: [references/evidence_md.md](references/evidence_md.md).

## Hard rules

- **Never write a bib field from memory, from a search snippet, or from a subagent's summary.** Copy it from a fetched record you saved to disk. A subagent may fetch records, but values are taken from the saved files by a script.
- **Literal standard.** A value counts as sourced only if it appears verbatim in a record for that paper. Allowed differences only: LaTeX encoding (accents, `{}` case protection, `--`), whitespace, dblp's trailing period on titles, `-` vs `--` in pages, "Last, First" vs "First Last" for the same name, DOI case. Composed strings are not allowed (e.g. a booktitle assembled from venue name + city + dates that no record spells that way).
- **Source policy.** Keep a field only if (a) an official record supports it, or (b) ≥2 independent sources agree.
  - Official: publisher / DOI registrar (Crossref, DataCite), proceedings site (ACL Anthology, NeurIPS, PMLR, CVF, COLM, IJCAI, Springer, AAAI OJS), arXiv, the paper PDF, the conference or journal site, the author's own page (blog, figshare, model card).
  - Aggregators: dblp, OpenAlex, Semantic Scholar, Google Scholar. A field that only one aggregator gives: drop it if unimportant (pages, editors, volume, publisher, city/dates in a booktitle); replace it with the official value if one exists. Important fields (title, authors, year, venue) must reach official or multi-source; if they cannot, tell the user instead of guessing.
- **Conflicts: the publisher's PDF wins**, then the proceedings site, then Crossref. Aggregators are often wrong on pages, author order, and similar names (e.g. Mingkun Yang vs Ming-Hsuan Yang). Record each conflict and its resolution in the MD.
- **Follow the version the entry cites.** An entry that names a venue follows the venue paper (title, author list and order), even when its link points to arXiv; an arXiv-only entry follows the arXiv record. The two versions often differ in authors and title. Web pages and software repositories have their own rules (recommended citation in the README or CITATION.cff, Internet Archive for pages that block scripts). Details: [references/ml_venues.md](references/ml_venues.md) §1 for the version rule, and [references/web_software_and_robotics.md](references/web_software_and_robotics.md) for venue-noted arXiv entries, web pages, repositories and robotics venues.
- **Confirm before dropping, and drop what repeats.** Try to find an official record for an uncertain field first; drop it only if that fails. Drop a field that repeats what the entry already prints (a note "arXiv 2024" next to "arXiv preprint …, 2024").
- **A check compares the evidence with the bib value.** Showing that an evidence string occurs in a record is not enough, and no "matches" line in the MD may be a fixed sentence: each must come from a comparison a script ran.
- **Read each field from that entry's own record.** Never from "the first cached file that contains X" — that once copied a 2023 paper's NeurIPS editors into a 2024 entry.
- **Claims are checked against the source text, not the abstract alone.** Abstract first; if not there, the full text (PDF or official open-access text). A claim found in neither is rewritten from the source wording or removed. Every quote in the MD is verified by `scripts/quote_check.py` against the saved text.
- **Uncited sentences count.** Sentences with no `\cite` that compare against, name, or say "first/only/unlike X/most comprehensive" about cited works are claims too. "First" and "only" claims need a search for counterexamples (check arXiv v1 dates).
- **Do not change paper text silently.** Rewrites of citing sentences go to the user's working copy only after showing what changed; record old → new in the MD. Respect the user's writing-style memories when rewriting.

## Workflow

Work in a scratch directory (`work/`); keep `records/` and `fulltext/` until the audit is final, and copy the scripts' outputs that the MD cites next to the MD if the user wants them kept.

1. **Inventory.** Parse the bib and the .tex files. List cited keys (incl. checklist/appendix files that are `\input`), uncited bib entries, and missing keys. Template files that are not compiled (e.g. `neurips_20xx.tex`) do not count.
   `python3 scripts/bibtools.py inventory main_ref.bib paper/*.tex`
   If the paper compiles, the `\bibcite` lines of the `.aux` give the same set and the reference numbers. Repeat the inventory whenever co-authors have edited: newly cited entries need the same audit.
2. **Fetch records** into `records/<key>/<source>.<ext>` (one file per source; naming in [references/sources.md](references/sources.md)). Get at least one official record per entry and, where possible, a second independent one. Use DOIs and arXiv IDs to fetch; use title search only to find the ID, then fetch by ID. Respect rate limits (OpenAlex ~15 title searches before 429; OpenReview API 403 — do not bypass blocks).
3. **Check fields mechanically.**
   `python3 scripts/field_check.py main_ref.bib records/ --out provenance.tsv`
   Each field gets: the sources containing it literally, and a level — `official+multi`, `official`, `multi`, `rule` (url/eprint derived from a verified DOI/arXiv ID), `aggregator-only`, or `NONE`. Fix every `NONE` and `aggregator-only` by fetching more, replacing with the official value, or dropping the field. Re-run until clean.
4. **Name splitting.** BibTeX must parse each author's last name as the sources give it ("Van Durme, Benjamin", "Daumé III, Hal"). `field_check.py` prints BibTeX-parsed last names next to the sources' family names when the record has structured names (Crossref/DataCite/ACL).
   Then check the names against the printed byline of the cited version, because metadata drops authors, reorders them and loses accents:
   `python3 scripts/pdf_byline.py main_ref.bib --map pdfs.tsv` (lines `key<TAB>pdf`; needs pypdf)
   It reports title, surname order, full names and diacritics on the first pages; treat its findings as leads to inspect by eye. Official record per venue, place/date strings, and known traps for NeurIPS / ICML / ICLR / ACL / TMLR / AAAI / ACM / IEEE: [references/ml_venues.md](references/ml_venues.md).
5. **Claims.** For every citing sentence (and uncited sentence about cited works):
   `python3 scripts/cite_sentences.py paper/main.tex --bib main_ref.bib --out sentences.tsv`
   Split each sentence into atomic claims about the cited work (numbers, "first", direction of a finding, what the method does). For each claim, find a verbatim quote: abstract → full text. Save texts to `fulltext/<key>.txt` (use pdfminer for two-column PDFs; ghostscript txtwrite interleaves columns). Put claims in `claims.tsv` (`key, sentence, claim, verdict, quote, source_url, source_file`), then:
   `python3 scripts/quote_check.py claims.tsv`
   Verdicts: `abstract`, `fulltext`, `unsupported→rewritten`, `author's own claim`, `for the authors` (cannot be settled from sources, e.g. timing of concurrent work).
   A citation also makes implicit claims: "benchmarks for X~\citep{a,b,c}" says each of a, b and c is a benchmark for X, and a citation at the end of a sentence covers the whole sentence. A true claim with the wrong work cited is a problem too.
   Parallelism: with many entries, subagents may each take a batch of keys and return claims + quotes, but the quote check is always run by script on saved text, never trusted from the agent. Review every item a subagent marks as not supported against the source yourself before editing. Brief template and verdict set for large audits: [references/citation_brief.md](references/citation_brief.md).
6. **Rewrite** unsupported sentences from the source wording; re-check them. Prefer the smallest edit: remove the unsupported word, narrow the scope, or move the claim to the authors before rewording. Under a page limit one added line can push the conclusion to the next page, so try the edit in a copy and show that the layout did not move:
   `scripts/clean_build.sh paper/ work/before` and `scripts/clean_build.sh paper_edited/ work/after`, then
   `python3 scripts/layout_diff.py work/before/main.pdf work/after/main.pdf --marker References --show`
   Order of edits, sentences with several citations, and what to do when the layout moves: [references/text_edits_and_layout.md](references/text_edits_and_layout.md).
7. **Write the MD** (template in references/evidence_md.md). Generate the per-field tables from `provenance.tsv`, not by hand.
8. **Final consistency check** (also use this alone when the user asks "is it still like this?"):
   `python3 scripts/sync_check.py main_ref.bib references_evidence.md paper/main.tex [paper/checklist.tex]`
   It reports bib fields that differ from the MD tables, entries missing from the MD, and citing sentences that are not recorded in the MD (i.e. edited after the audit). Then compile: 0 BibTeX warnings, 0 undefined citations. Compile from a clean copy (`scripts/clean_build.sh SRC OUT`), because a `main.bbl` left by an earlier build is reused silently and the PDF then shows references that no longer match the bib. Also look at `git log` and the remote for edits made since the MD was written. An MD written before this skill may lack the `| field | value | basis |` tables; then the field part of `sync_check.py` lists every entry as missing and only its sentence part is usable.
9. **Multiple versions** (arXiv / venue / camera): the bib and the corrected sentences must be ported to every version; check each one with step 8 and report versions that still carry wrong passages.

## Reporting to the user

State the counts (fields per level, claims per verdict, sentences rewritten), list what was dropped and why, list conflicts and how they were resolved, list blocked sources, and list what is left for the authors. Say plainly which versions or sentences are not yet covered. Do not report "all verified" if `sync_check.py` shows unrecorded sentences.

## Lessons from past audits

- Crossref/dblp/OpenAlex had wrong pages for several ACL papers, a wrong author order (BasqBBQ), and a wrong author. The ACL PDF footer and byline settled them.
- Official venue names are often surprising (COLM's BibTeX says "Conference On Language Models"); copy, don't normalise.
- ACL Anthology pages can disagree with the PDF (SHADES: 20 vs 37 regions); the PDF wins for content claims.
- Checking only abstracts misses claims that are true (found only in full text) and lets false ones through; 47 of 348 claims were unsupported in one audit, including a reversed finding, wrong counts (21 vs 22 models; 17,000 vs 16,995), misattributed percentages, and "first benchmark to…" that an earlier arXiv v1 contradicted.
- Dataset facts quoted in the paper (age ranges, licences) are claims too: check them against the dataset files and licence records.
- Co-authors or other agent sessions may edit the paper after the audit; always end with `sync_check.py`.
- Proceedings web metadata can be wrong where the PDF is right: PMLR reversed an author order, an RSS index showed a different title, and the ICLR site omitted authors without an OpenReview profile (one audit, 203 entries). More in references/web_software_and_robotics.md.
- In one audit, 13 of 352 claims did not match the full text although the sentences had passed an earlier review. Most were category labels: a framework or a method paper listed as a benchmark, a web-navigation benchmark listed under programming tasks.
- In another audit (194 cited entries), a title search returned a different paper twice, a DOI sat under the wrong conference, and conference place/date strings written from memory were wrong for ICLR 2020 and 2021. After a title search, compare first author and year, then fetch by ID. Details in references/ml_venues.md.
- In the same audit, a 28-character rewrite of one citing sentence on page 2 moved the conclusion from page 10 to page 11. A shorter wording kept every page unchanged. `layout_diff.py` shows this in seconds.
- Look at the `.bbl` after editing: the style decides what readers see (title case without double braces, quotes around nicknames, fields that are not printed).
