# ML / AI venues: official records, printed bylines, and known traps

Lessons from an audit of an ML paper (194 cited entries, ML venues, 2026-11). Read this when the bibliography is mostly NeurIPS / ICML / ICLR / ACL-family / AAAI / TMLR papers and arXiv preprints. It complements [sources.md](sources.md) (generic fetch URLs) and [web_software_and_robotics.md](web_software_and_robotics.md) (venue-noted arXiv entries, web pages, repositories, robotics venues). Access notes carry a date because sites change; re-test before relying on them.

## Contents
1. Which version does the entry cite
2. Author names: the printed byline decides
3. Official record per venue
4. Conference name, place, dates, ordinals
5. Records that look right and are wrong
6. Fields that usually have no accessible official source
7. Access notes (2026-11)

## 1. Which version does the entry cite

Decide first which version the entry cites, then judge it only against records of that version.

| The entry cites | How to tell | Authority, highest first |
|---|---|---|
| Venue version | `booktitle`, or a non-arXiv `journal` | printed PDF in the official proceedings > the venue's own records (proceedings page and BibTeX, accepted-paper list, OpenReview venue record, DOI record) > arXiv |
| arXiv version | `journal = arXiv preprint …` or `eprint`, no venue | arXiv record by ID (API) > the arXiv PDF |

Entries that say "arXiv preprint" and also name a venue in a note, web pages and software: see [web_software_and_robotics.md](web_software_and_robotics.md).

- Records of another version (the arXiv preprint of a conference paper) are listed in the evidence file as "other version". They never count as a conflict, and never as a confirmation of authors or year. arXiv author lists often differ from the published one, and the arXiv year is often one year before the venue year.
- Before writing "arXiv only" or "OpenReview only" for a recent paper, look for a published version: the venue's accepted-paper list, and whether the proceedings volume has appeared. ICML 2026 = PMLR v306 appeared about ten weeks after the conference, and nine entries moved from OpenReview links to PMLR pages.
- An arXiv `comment` ("Accepted to X") is a lead, not venue evidence. It needs a venue record next to it: the proceedings page, the accepted-paper list, or the OpenReview venue record with its `pdate`. A full citation with pages in the arXiv `journal_ref`, confirmed by a second independent record, reaches the multi-source level when the publisher's site is blocked (an ACC paper: `journal_ref` plus the dblp record).
- When a paper has moved from preprint to proceedings, switch the whole entry (type, venue, pages, editors, URL) to the published record. Do not leave arXiv fields next to venue fields.

## 2. Author names: the printed byline decides

Author names follow the byline printed in the PDF of the cited version. Metadata is a lead, the printed page is the reference.

Run `scripts/pdf_byline.py refs.bib --map map.tsv` (lines `key<TAB>pdf`). It checks the title, the order of surnames, full names, and diacritics on the first pages. Its findings are leads to inspect by eye.

Seen in metadata but different in print:
- profile-name variants from OpenReview or arXiv: "WenHao", "Mcmilin", a legal first name where the paper prints another name, added middle names or initials
- a missing author (the eighth of ten), a wrong author order (official proceedings BibTeX vs the PDF)
- accents dropped by arXiv, Crossref or dblp (Horváth, Jovanović, Balunović, Arık)

Rules that settle the usual cases:
- Published PDF not downloadable (ACM, IEEE, old OpenReview PDFs): use an arXiv PDF only if its header states it is the camera-ready ("Published as a conference paper at ICLR 2023", "Published in Transactions on Machine Learning Research (01/2026)"). Otherwise fall back to the same-version metadata and say so in the evidence file.
- A typo in the printed byline (one paper prints "Fadee" for "Fadaee") is not copied. Keep the spelling that the Anthology or DOI record and the author's other papers use, and record the printed form.
- Titles follow the official citation record (DOI record, Anthology, proceedings page, arXiv abstract page). Note a printed difference without adopting it.
- pypdf prints a spacing accent before its letter (`´a`) and a dotless `ı`. The script re-attaches them. Do the same in any ad-hoc comparison, or accent checks give false alarms.

## 3. Official record per venue

| Venue | Official record | Notes |
|---|---|---|
| NeurIPS | `papers.nips.cc` year listing, each paper's `-Bibtex.bib`, PDF at `/file/<hash>-Paper-Conference.pdf` | BibTeX gives volume, editors, publisher. 2022+ also have Curran DOIs (10.52202/…) in Crossref with pages. Editors are abbreviated there ("J. Tomczak"): copy as given. |
| ICML, AISTATS, CoRL, other PMLR | `proceedings.mlr.press/v<vol>/` index, each paper's page and BibTeX | The volume index lists OpenReview forum IDs for recent years, which gives exact matching. Publisher is "PMLR". |
| ICLR | `iclr.cc/virtual/<year>/papers.html?filter=titles` (2020+), `iclr.cc/Conferences/<year>/Schedule?type=Poster` (2018–19), poster pages (authors as JSON-LD), `proceedings.iclr.cc` (2024+) | The poster page links the OpenReview forum, which confirms an `openreview.net/forum?id=` URL. `proceedings.iclr.cc` BibTeX has contained typos and a garbled author: compare with the PDF. |
| ACL, EMNLP, NAACL, Findings | ACL Anthology `.bib` and PDF | Trust Anthology pages over Crossref. Anthology has no "Findings of ACL" series field: do not add one. |
| TMLR | OpenReview record (venue "Accepted by TMLR", `pdate`), the PDF header with month/year | The official BibTeX has journal, year, ISSN and no volume. The dblp habit `volume = {2026}` prints "2026, 2026". |
| COLM | OpenReview group page for the official conference name, proceedings BibTeX | Copy the name as given, do not normalize. |
| MLSys | `proceedings.mlsys.org` BibTeX | Publisher as in that BibTeX. |
| AAAI | Crossref DOI record (10.1609/aaai…), `aaai.org/proceeding/…` | Crossref has no editors for AAAI. |
| ACM (CCS, KDD, WWW, CSUR) | Crossref DOI record | ACM article numbers ("79:1–79:44") are a dblp convention. Crossref gives "1-44". Keep only what the registrar record shows. |
| IEEE conferences, ACC | Crossref if a DOI exists | Some have no Crossref DOI and IEEE Xplore is blocked. Then venue, year and pages need the authors' arXiv `journal_ref` plus a second record (§1). Drop publisher and URL. |
| Springer, Elsevier, journals | Crossref (`container-title`, `short-container-title`, volume, issue, page), the article page's `citation_*` meta tags | Article numbers as pages (e.g. 1912613) are confirmed by `citation_firstpage`. |
| arXiv preprints | arXiv API by ID; DOI `10.48550/arXiv.<id>` is registered at DataCite, not Crossref | Check that the ID's title and first author match the entry. |

## 4. Conference name, place, dates, ordinals

Strings such as "9th International Conference on Learning Representations, ICLR 2021, Virtual Event, May 3-7, 2021" are easy to write from memory and often wrong there. The literal standard in SKILL.md applies: keep such a string only if a record spells it that way (dblp booktitles do, and they are sometimes wrong). Use the pages below to check each part of that record. A part that the official pages contradict or do not show is removed:

- `iclr.cc/Conferences/<year>`, `neurips.cc/Conferences/<year>`: dates and whether the meeting was virtual. ICLR 2020 was "Virtual Only" from April 26 to May 1, so "Addis Ababa" is wrong. ICLR 2021 names no country.
- PMLR volume page `<title>`: "Held in <city> on <dates>".
- Crossref `event` (name, location, sometimes dates), ACL PDF header lines, the Anthology `.bib` `address`.
- OpenReview group page title for the official name and ordinal ("10th Annual Conference on Robot Learning").

If the only source for place and dates is dblp, shorten the booktitle to the official proceedings name.

## 5. Records that look right and are wrong

- **A fuzzy title match can be another paper.** A title search returned arXiv 2301.02621 for "Deep Leakage from Gradients", and a 2022 paper for a 2017 one. After any title search, compare the first author and year, then fetch by ID.
- **A DOI can sit under the wrong container.** One workshop paper's DOI was filed under a 2004 conference. One journal paper also had a DOI for its conference version. Read `container-title` and the year of the DOI record before using its pages or venue.
- **dblp volume numbers:** dblp labels NeurIPS 2024 as volume 38. The official BibTeX says 37.
- **Crossref page numbers for recent EMNLP** differed from the Anthology. The Anthology and the PDF footer win.
- **Official proceedings BibTeX can be wrong too** (author order, a misspelled title word). When the official record and the printed PDF disagree, the PDF wins for names and the conflict is written down.
- **A cached abstract can belong to another paper** when it was stored after a title search. Store abstracts and full texts by ID, and check the title inside the file before quoting from it.

## 6. Fields that usually have no accessible official source

Drop these when no official record shows them. They are not needed to identify the paper.

- `editor` for ACM and AAAI proceedings (Crossref has none, publisher pages are blocked)
- `publisher` and `url` for IEEE papers known only through dblp
- `series`, `address`, `month`, `organization` that came from a Google Scholar or dblp export
- place and dates inside `booktitle`

Do not drop title, authors, year or venue. If one of those cannot reach an official record or two independent ones, tell the user.

## 7. Access notes (2026-11)

Blocked or challenged for scripts, and not to be bypassed: dblp.org and its Dagstuhl mirror (bot challenge), OpenReview `/pdf` and `/attachment` and sometimes `notes?id=` (challenge or 403), AAAI OJS (challenge), ACM DL pages and PDFs (403), IEEE Xplore (empty 202). Rate-limited: Semantic Scholar (429), OpenAlex title search (a small daily budget).

Usable: arXiv export API (batch `id_list`, about 3 s between calls), Crossref `/works`, DataCite, OpenReview `api2 /notes/search?term=<title>&content=title` (about 6 s between calls, back off on 429; results include dblp-imported records, which count as dblp), papers.nips.cc, PMLR, ACL Anthology, iclr.cc, proceedings.iclr.cc, MLSys, IJCAI, CVF.

When a source is blocked, say so in the evidence file and use the next source. A blocked source never justifies filling a field from memory.
