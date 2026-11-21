# reference_checker

[![test](https://github.com/canyuchen/reference_checker/actions/workflows/test.yml/badge.svg)](https://github.com/canyuchen/reference_checker/actions/workflows/test.yml)

A [Claude Code](https://claude.com/claude-code) skill, `reference-audit`, that audits the references of a LaTeX paper. It checks two things and writes down the evidence for both:

1. **The bibliography.** Every field that stays in the `.bib` appears verbatim in a fetched record of that paper, and the record is official or confirmed by a second independent source. Fields that cannot be confirmed and are not needed to identify the paper are removed.
2. **The citing sentences.** Every sentence that cites or describes a cited work is supported by a verbatim quote from that work's abstract or full text. Unsupported sentences are rewritten from the source wording.

The result is one Markdown evidence file next to the paper. It lists, per entry, each field with its source, and per citing sentence, each claim with its quote and link.

## Why

Language models write plausible bibliography fields from memory: a page range, an editor list, a conference city and dates. They also describe cited papers from memory. Both kinds of error are hard to see by reading. This skill replaces recall with fetched records and script-run comparisons:

- No field is written from memory, from a search snippet, or from a subagent's summary.
- Official sources (publisher, DOI registrar, proceedings site, arXiv, the paper PDF) outrank aggregators (dblp, OpenAlex, Semantic Scholar, Google Scholar).
- Every quote in the evidence file is checked by a script against the saved source text.
- Sources that block scripts are reported and never bypassed.

## Install

```bash
git clone https://github.com/canyuchen/reference_checker ~/.claude/skills/reference-audit
```

The skill then appears in every Claude Code session. To use it in one project only, clone it into `<project>/.claude/skills/reference-audit` instead. Requirements:

- Python 3.8 or later. The core scripts use only the standard library.
- `pypdf` for `pdf_byline.py` and `layout_diff.py` (`pip install pypdf`).
- `latexmk` and `rsync` for `clean_build.sh`.
- Optional: `pylatexenc` for more complete LaTeX decoding.

## Use

Ask Claude Code in the paper's folder, for example:

- "Check that every reference field has a verified source and record the evidence in Markdown."
- "Do the citing sentences in the related work match the original papers?"
- "Is the evidence file still in sync with the paper?"

Or call the skill by name: `/reference-audit`.

## Contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Rules and the nine-step workflow. This is what Claude reads first. |
| `references/sources.md` | Where to fetch each kind of record and how to name the saved files. |
| `references/ml_venues.md` | Cited-version rule, printed bylines, official record per ML venue, known wrong records. |
| `references/web_software_and_robotics.md` | Web pages, software repositories, robotics venues, what the bibliography style prints. |
| `references/citation_brief.md` | Brief for subagents that check citing sentences in large audits. |
| `references/text_edits_and_layout.md` | How to change a citing sentence and show that the page layout did not move. |
| `references/evidence_md.md` | Template of the evidence file. |
| `scripts/bibtools.py` | BibTeX parsing, LaTeX decoding, inventory of cited keys. |
| `scripts/field_check.py` | Compares every `.bib` field with the saved records and assigns a source level. |
| `scripts/pdf_byline.py` | Compares title and authors with the first pages of the cited PDF. |
| `scripts/cite_sentences.py` | Lists the sentences that make claims about cited works. |
| `scripts/quote_check.py` | Verifies that every quote occurs in the saved source text. |
| `scripts/sync_check.py` | Reports where the bib, the paper text and the evidence file no longer agree. |
| `scripts/clean_build.sh` | Builds the paper from a clean copy and reports pages, warnings and undefined citations. |
| `scripts/layout_diff.py` | Compares two builds page by page. |
| `examples/attention/` | A worked example with real records for one arXiv paper (see below). |
| `tests/run_examples.sh` | Runs the scripts on the example and checks each exit code. |

The scripts also work without Claude Code. Each one prints its usage with `--help` or when run without arguments.

```bash
python3 scripts/bibtools.py inventory refs.bib main.tex appendix.tex
python3 scripts/field_check.py refs.bib records/ --out provenance.tsv
python3 scripts/pdf_byline.py refs.bib --map pdfs.tsv
python3 scripts/quote_check.py claims.tsv
python3 scripts/sync_check.py refs.bib references_evidence.md main.tex
scripts/clean_build.sh paper/ work/build
python3 scripts/layout_diff.py work/before/main.pdf work/after/main.pdf --marker References
```

## Worked example

[`examples/attention/`](examples/attention/) is a one-entry audit of *Attention Is All You Need* (arXiv:1706.03762). The records in `records/` were fetched from the arXiv API and DataCite on 2026-11-21.

| File | What it shows |
|---|---|
| `refs_unverified.bib` | The entry before the audit, with `pages` and `address` that no record of the arXiv version contains. `field_check.py` marks both `NONE` and exits 1. |
| `refs.bib` | The entry after the audit. Every field is `official+multi` or derived by rule from the verified arXiv ID. |
| `main.tex` | Two citing sentences. |
| `claims.tsv`, `fulltext/` | One claim per sentence with a verbatim quote from the abstract. `quote_check.py` finds both. |
| `references_evidence.md` | The evidence file. `sync_check.py` reports `IN SYNC`, and reports the sentence again as soon as one number in it changes. |

```bash
cd examples/attention
python3 ../../scripts/field_check.py refs_unverified.bib records/ --out /tmp/prov.tsv   # 2 fields NONE, exit 1
python3 ../../scripts/field_check.py refs.bib records/ --out /tmp/prov.tsv              # clean, exit 0
python3 ../../scripts/quote_check.py claims.tsv
python3 ../../scripts/sync_check.py refs.bib references_evidence.md main.tex
```

Run all checks at once with `tests/run_examples.sh`.

## Status and limits

- The rules and reference notes come from three audits of ML, NLP and robotics papers in November 2026, with about 200 cited entries each.
- The scripts compare and report. They do not fetch records. Fetching is done by the agent, which follows `references/sources.md`.
- Access notes in the reference files are dated. Sites change their limits and bot checks, so test a source before relying on it.
- `pdf_byline.py` reports leads to inspect by eye. PDF text extraction fails on some layouts.
- The skill has not been evaluated against a baseline run without it.

## License

MIT. See [LICENSE](LICENSE).
