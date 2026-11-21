# Example paper: references and evidence

Audit date: 2026-11-21. Scope: `refs.bib`, `main.tex`.

This is a worked example for `reference_checker`. The records in `records/` were fetched from the arXiv API and DataCite on the audit date; `fulltext/vaswani2017attention.txt` is the arXiv abstract.

## 1. Method and result
- 1 entry, 6 fields; cited in `main.tex`: 1 key.
- Literal check by `scripts/field_check.py`; url / eprint / archivePrefix derived from the verified arXiv ID.
- Result: official+multi = 3, rule = 3, aggregator-only = 0, NONE = 0.

## 2. Entries

### 1. `vaswani2017attention`
Vaswani et al. Attention Is All You Need. arXiv:1706.03762, 2017.
- type: misc (arXiv preprint); cited in main.tex
- records: [arXiv API](https://export.arxiv.org/api/query?id_list=1706.03762); [DataCite](https://api.datacite.org/dois/10.48550/arXiv.1706.03762)

| field | value | basis |
|---|---|---|
| title | Attention Is All You Need | official+multi: arxiv, datacite |
| author | Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, Lukasz and Polosukhin, Illia | official+multi: arxiv, datacite |
| year | 2017 | official+multi: arxiv, datacite |
| eprint | 1706.03762 | rule: arXiv ID in record |
| archiveprefix | arXiv | rule: eprint present |
| url | https://arxiv.org/abs/1706.03762 | rule: arXiv ID |

## 3. Conflicts between sources
None.

## 4. Claims in the paper about each cited work

### Claims: `vaswani2017attention`
Current sentence:
> The Transformer is based solely on attention mechanisms and dispenses with recurrence and convolutions entirely~\cite{vaswani2017attention}.

| claim | verdict | basis (verbatim quote) |
|---|---|---|
| uses attention only, no recurrence or convolution | abstract | "the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely" |

Current sentence:
> It reached 41.8 BLEU on WMT 2014 English-to-French after training for 3.5 days on eight GPUs~\cite{vaswani2017attention}.

| claim | verdict | basis (verbatim quote) |
|---|---|---|
| 41.8 BLEU, WMT 2014 En-Fr, 3.5 days on eight GPUs | abstract | "On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs" |

Abstract source: [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).

## 5. Changes made to the paper text
None.

## 6. Field levels and removals
`refs_unverified.bib` is the same entry before the audit. It also had `pages = {1--11}` and `address = {Long Beach, CA, USA}`. Neither appears in any record of the arXiv version, so both were removed.

## 7. Open items for the authors
None.
