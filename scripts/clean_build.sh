#!/bin/bash
# Build a LaTeX paper from a clean copy and report the numbers that matter for a reference audit.
#
# Why a clean copy: a main.bbl (or stale main.tex / .bib copies) left in the source or output
# directory by an earlier build is silently reused, so the PDF can show references that no longer
# match the .bib. Copying the sources without build products and running BibTeX fresh avoids that.
#
# Usage: clean_build.sh SRC_DIR OUT_DIR [MAIN]     (MAIN defaults to "main"; OUT_DIR must not be SRC_DIR)
# Prints: pages, overfull boxes, undefined citations/references, BibTeX warnings, \bibitem count.
set -u
SRC="${1:?usage: clean_build.sh SRC_DIR OUT_DIR [MAIN]}"; OUT="${2:?usage: clean_build.sh SRC_DIR OUT_DIR [MAIN]}"; MAIN="${3:-main}"
SRC_ABS="$(cd "$SRC" && pwd)" || exit 2
mkdir -p "$OUT" || exit 2
OUT_ABS="$(cd "$OUT" && pwd)"
[ "$SRC_ABS" = "$OUT_ABS" ] && { echo "OUT_DIR must differ from SRC_DIR"; exit 2; }
EXC=(); for e in aux bbl blg log out fls fdb_latexmk synctex.gz pdf toc lof lot ptc nav snm run.xml bcf; do EXC+=(--exclude "/$MAIN.$e"); done
rsync -a --delete "${EXC[@]}" --exclude '.git' "$SRC_ABS/" "$OUT_ABS/" || exit 2
cd "$OUT_ABS" || exit 2
latexmk -pdf -interaction=nonstopmode -halt-on-error "$MAIN.tex" > build.out 2>&1; RC=$?
c() { grep -c "$1" "$2" 2>/dev/null || true; }
echo "latexmk exit code:      $RC"
echo "pages:                  $(sed -n 's/.*Output written on .*(\([0-9]*\) pages.*/\1/p' "$MAIN.log" | tail -1)"
echo "overfull boxes:         $(c '^Overfull' "$MAIN.log")"
echo "undefined citations:    $(c 'Citation .* undefined' "$MAIN.log")"
echo "undefined references:   $(c 'Reference .* undefined' "$MAIN.log")"
echo "BibTeX warnings:        $(c '^Warning--' "$MAIN.blg")"
echo "bibliography entries:   $(c '\\bibitem' "$MAIN.bbl")"
echo "pdf:                    $OUT_ABS/$MAIN.pdf"
[ "$RC" -ne 0 ] && { echo "--- last lines of build.out ---"; tail -15 build.out; }
exit $RC
