# Web pages, software entries, robotics venues, and what the style prints

Lessons from an audit with 203 cited entries (arXiv preprints, robotics and ML venues, web pages, repositories; 2026-11). It adds to [ml_venues.md](ml_venues.md), which covers the cited-version rule, printed bylines and the main ML venues.

## 1. Entries that name a venue but link to arXiv

Some bibliographies cite `journal = arXiv preprint …` with a `note` such as "CoRL 2022". Ask the user once which version such entries follow. In that audit the user chose the venue version: title, author list and order follow the venue paper, and the arXiv ID and URL are checked separately.
- Differences found this way: authors only on a later arXiv version (Reflexion, OpenVLA, Diffusion Policy), a changed title (VIMA; RDA carries "RDA:" only on arXiv), a different author order (MOKA).
- When the bib title follows the venue, the arXiv ID is confirmed as the same paper by its authors and a near-identical title. The MD states the arXiv title next to it.
- A venue named in a note needs venue evidence: the proceedings page, the schedule or the OpenReview venue record. The authors' arXiv comment "Accepted to X" alone is not enough; if nothing else exists, drop the note.
- Nicknames and middle initials are part of the printed name: 'Linxi "Jim" Fan', "Sida I. Wang", "Xavi Puig". Write a nickname as ``Jim'' in the bib; straight quotes print as two closing quotes.
- Team bylines: if the first page prints only a team name, use the team name. If it prints the team name followed by every author, add `and others` or list them. With `and others`, the bib list must be a prefix of the source list.

## 2. Web pages

- The title, byline and date must each appear verbatim in the saved page text, and each must equal the bib value. A check that only finds the evidence string on the page let "Anthropic Frontier Red Team" pass although the page says "Frontier Red Team".
- Prefer the page `<title>`, `<h1>` and `og:title`; body text extraction can insert spaces ("Fetch : Phase").
- If the announcement URL redirects, cite the canonical URL.
- A page that blocks scripts (openai.com returns 403) can be confirmed from the Internet Archive:
  - `https://archive.org/wayback/available?url=<url>` and `https://web.archive.org/cdx/search/cdx?url=<url>` list the snapshots. The first HTTP 200 capture dates the page.
  - `https://web.archive.org/web/<timestamp>id_/<url>` returns the raw snapshot (it may be gzip-compressed). Check `<h1>`, `og:title`, and that `rel="canonical"` is the cited URL.

## 3. Software and repositories

- Read the README "Citation" section and CITATION.cff first. If they ask for a paper, cite the paper: One simulator's README asked for its arXiv paper (18 authors) where the bib had cited the repository under the organisation name.
- Copy the recommended citation exactly, including capitalisation (one framework's recommended title is in sentence case). Check a few release tags if the bib says which release it was taken from.
- Without a recommended citation: title = the name the README gives the project ("Codex CLI"), author = the owner's display name from `api.github.com/orgs/<org>`, year = `created_at` from `api.github.com/repos/<owner>/<repo>`.
- If the repository page times out, the API's `html_url` confirms the URL.
- Zenodo: a concept DOI resolves to the latest version record. Confirm through `https://doi.org/<doi>` and `https://zenodo.org/api/records/<id>`.

## 4. Record names for these sources

`field_check.py` takes the source from the file stem before the first `_`. Use the generic official stems:
- RSS index, OpenReview venue record, RLJ page, conference schedule: `venue_rss.html`, `venue_openreview.json`, `venue_schedule.html`.
- Web page text, README, CITATION.cff, host API reply, Internet Archive snapshot: `author_page.txt`, `author_readme.txt`, `author_citation.txt`, `author_api.json`, `author_archive.txt`.
- Zenodo: `datacite.json`.

## 5. Robotics and other venues not in ml_venues.md

| Venue | Official record | Notes |
|---|---|---|
| RSS | `roboticsproceedings.org/rss<NN>/` index and PDFs | The index title can differ from the PDF (RoboCasa). RSS 2025 PDFs have no text layer: use the index and Crossref (10.15607/rss.…). |
| CoRL | PMLR volume | The PMLR page reversed the author order of RT-2 and SayCan; the PDF was right. |
| RLC | `rlj.cs.umass.edu/<year>/papers/` page and PDF, `rl-conference.cc/<year>/paper_schedule.html` | The PDF has a cover page; the running header may carry a short title. Pre-proceedings may still change. |
| NeurIPS Datasets and Benchmarks | `datasets-benchmarks-proceedings.neurips.cc` (2021), main proceedings later | The track name needs its own evidence. |
| ICRA, IROS, RA-L, Science Robotics | Crossref | Science Robotics titles are in sentence case. Crossref titles contain HTML entities; decode before comparing. |

- PMLR volume numbers: find the volume by its exact name ("Proceedings of ICML 2024") in the volume index. A loose match picked a workshop volume.
- The ICLR site and OpenReview author fields omit authors who have no OpenReview profile (GAIA, Terminal-Bench). The PDF lists them.
- OpenReview API v2 covers recent venues; ICLR 2023 and earlier need API v1.
- arXiv metadata can truncate a surname (ASAP) or split a team name into two authors.

## 6. Fields that repeat or are not printed

- Drop a field that repeats what the entry already prints. One audit removed 81 notes "arXiv 2024" that stood next to "arXiv preprint arXiv:…, 2024".
- Add a verified official URL when an entry prints no locator (a model page that printed only "Title, 2026").
- A field the style does not print (`doi` on `@misc` under plainnat) may stay if it is verified.
- Look at the `.bbl` after every bib edit. plainnat lowercases titles that are not wrapped in double braces, and a changed author can move the entry and renumber the list.

## 7. Scope and reporting

- Take the cited set from `\bibcite` in the compiled `.aux`. Two days after the first pass of one audit, five more entries were cited, and four of them needed fixes.
- Never hard-code a verdict or its basis text. A fixed sentence "arXiv title is identical" was printed for entries whose bib title follows the venue.
- Before dropping an uncertain field, try once more to confirm it. Two fields with only indirect evidence were confirmed by an RLJ PDF and an Internet Archive snapshot.
