# Sources: where to fetch records and how to name them

Save each record as `records/<bibkey>/<source>.<ext>`. The file stem (before the first `.` or `_`) decides the source name and family used by `field_check.py`:

| stem | family | how to fetch |
|---|---|---|
| `crossref` | official | `https://api.crossref.org/works/<DOI>` (JSON). Also has `event` (conference name/place/dates) and sometimes `abstract`. |
| `datacite` | official | `https://api.datacite.org/dois/<DOI>` — arXiv DOIs `10.48550/arXiv.<id>`, figshare, Zenodo. |
| `acl` | official | `https://aclanthology.org/<id>.bib`; page `https://aclanthology.org/<id>/` (abstract); PDF `https://aclanthology.org/<id>.pdf` (byline, page-number footer). |
| `arxiv` | official | `http://export.arxiv.org/api/query?id_list=<id>` (Atom XML: title, authors, v1 date); arXiv BibTeX export `https://arxiv.org/bibtex/<id>`. |
| `neurips` | official | `https://papers.nips.cc/paper_files/paper/<year>/hash/<hash>-Abstract-Conference.html` and its `-Bibtex.bib`. |
| `pmlr` | official | `https://proceedings.mlr.press/v<vol>/<key>.html` and `.bib`. |
| `cvf` | official | `https://openaccess.thecvf.com/...html`; BibTeX is in the page. |
| `colm` | official | `https://proceedings.colm.cc/` paper page and its BibTeX. |
| `iclr` | official | Accepted-paper JSON, e.g. `https://iclr.cc/static/virtual/data/iclr-2025-orals-posters.json`. OpenReview API often returns 403 — do not bypass. |
| `tmlr` | official | `https://jmlr.org/tmlr/papers/` list (check encoding: it may be saved double-encoded). |
| `springer` | official | Chapter page `https://link.springer.com/chapter/<DOI>`: LNCS volume, editors, pages. |
| `ijcai`, `aaai`, `acm`, `ieee`, `venue` | official | Proceedings / conference site pages, AAAI OJS, ACM DL, IEEE Xplore. |
| `pdf` | official | Text of the paper PDF (`pdftotext -layout` or pdfminer for two-column). |
| `author` | official | Author's own blog, figshare, Hugging Face model card. |
| `dblp` | aggregator | `https://dblp.org/rec/<dblpkey>.bib` or `.xml`; search `https://dblp.org/search/publ/api?q=...&format=json`; SPARQL `https://sparql.dblp.org/`. |
| `openalex` | aggregator | `https://api.openalex.org/works/doi:<DOI>` (by DOI is fine; title search rate-limits ~15 requests). |
| `s2` | aggregator | `https://api.semanticscholar.org/graph/v1/paper/DOI:<DOI>?fields=...` (often 429). |
| `scholar` | aggregator | Google Scholar BibTeX (never the only source). |

Multiple records from the same source: `crossref_event.json`, `pdf_p1.txt`, etc. — the stem before `_` is the source.

## Tips

- arXiv-only papers: prefer the dblp CoRR form or arXiv's own BibTeX over Google Scholar's `journal={arXiv preprint ...}`; keep `eprint`/`archivePrefix` consistent with the arXiv record.
- Conference city/dates in a booktitle need a record that spells them that way (dblp booktitles usually do; check against the conference site or Crossref `event`). If only dblp has them, drop them or use the official booktitle.
- Content support for multi-source (when the strings differ in form): same author surnames in the same order, same numbers, abbreviation words that are prefixes of the full words, each part of a venue name found in another record. Record this as "content-level" in the MD; it is weaker than literal.
- Abstracts for claims: ACL page, arXiv abstract, Crossref `abstract`, OpenReview page, publisher page. Full text: ACL/CVF/NeurIPS/PMLR PDF, arXiv PDF (note which version), Europe PMC full-text XML for medical journals.
- Dataset claims: fetch the dataset's own files (GitHub raw, figshare API `https://api.figshare.com/v2/articles/<id>`) and licence (`https://api.github.com/repos/<owner>/<repo>/license`).
