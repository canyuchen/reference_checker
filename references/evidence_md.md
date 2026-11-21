# Evidence Markdown template

Write in the user's language. One file, e.g. `references_evidence.md`, next to the paper. Sections:

```markdown
# <Paper> references and evidence

Audit date: YYYY-MM-DD. Scope: <bib files / versions>.

## 1. Method and result
- N entries, M fields; cited in <version A>: X keys, <version B>: Y keys.
- Literal check: which fields, allowed differences (list them).
- Rule check: url / eprint / archivePrefix / howpublished, and how they were derived.
- Source policy (official or ≥2 independent; aggregator-only dropped or replaced).
- Result: fields per level (official+multi / official / multi / rule / aggregator-only=0).
- Compile: BibTeX warnings, undefined citations.

## 2. Entry table
| # | key | reference | cited in | differs between versions |

### <n>. `<key>`
<formatted reference>
- type; cited in; same/different in other versions
- records: [Crossref](...); [ACL](...); [dblp](...); [PDF](...)

| field | value | basis |
|---|---|---|
| title | ... | literal: ACL .bib, Crossref, dblp |
| pages | 42–50 | literal: ACL .bib, ACL PDF |
| url | https://doi.org/... | rule: DOI resolver |

## 3. Conflicts between sources and how they were resolved
| key | field | source A says | source B says | kept | why |

## 4. Claims in the paper about each cited work
### `<key>`
Current sentence:
> <exact LaTeX sentence>

Before (if rewritten):
> <old sentence>

| claim | verdict | basis (verbatim quote from abstract or full text) |
|---|---|---|

Abstract source: [link]. Full-text source: [link] (version).

## 5. Changes made to the paper text
1. Old: ... → New: ... (reason; key)

## 6. Sentences without \cite that describe cited works
| sentence | claim | verdict | verbatim quote (source) |

## 7. Field levels and removals
- Removed / replaced fields, with reason.
- Fields with one official source only; fields with ≥2 non-official sources only.
- Sources that could not be used (blocked, rate-limited) .
- Per-entry level table.

## 8. Open items for the authors
```

Rules:
- Every quote in sections 4 and 6 must pass `quote_check.py` against a saved text; give the source URL next to it.
- Field tables are generated from `provenance.tsv`, never typed by hand.
- In the `author` / `editor` rows, write the names as in the bib (`Last, First and Last, First`) or separated by `; `.
- Keep the exact current sentence (LaTeX source) so `sync_check.py` can detect later edits.
