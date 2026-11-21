#!/usr/bin/env bash
# Smoke test: run the stdlib scripts on examples/attention and check each exit code.
# Usage: tests/run_examples.sh   (from anywhere; needs python3 >= 3.8)
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
EX="$ROOT/examples/attention"
S="$ROOT/scripts"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0

expect() {  # expect <wanted rc> <label> <command...>
  local want=$1 label=$2; shift 2
  "$@" >"$TMP/out.txt" 2>&1
  local rc=$?
  if [ "$rc" -eq "$want" ]; then
    echo "ok    $label (rc=$rc)"
  else
    echo "FAIL  $label (rc=$rc, wanted $want)"; sed 's/^/      /' "$TMP/out.txt"; fail=1
  fi
}

cd "$EX" || exit 1
expect 0 "py_compile all scripts"            python3 -m py_compile "$S"/*.py
expect 0 "clean_build.sh syntax"             bash -n "$S/clean_build.sh"
expect 0 "inventory"                         python3 "$S/bibtools.py" inventory refs.bib main.tex
expect 0 "field_check: verified bib"         python3 "$S/field_check.py" refs.bib records/ --out "$TMP/prov.tsv"
expect 1 "field_check: unverified bib"       python3 "$S/field_check.py" refs_unverified.bib records/ --out "$TMP/prov_bad.tsv"
grep -q $'\tpages\t1--11\tNONE' "$TMP/prov_bad.tsv" && echo "ok    pages flagged NONE" || { echo "FAIL  pages not flagged NONE"; fail=1; }
expect 0 "cite_sentences"                    python3 "$S/cite_sentences.py" main.tex --bib refs.bib --out "$TMP/sentences.tsv"
[ "$(tail -n +2 "$TMP/sentences.tsv" | wc -l)" -eq 2 ] && echo "ok    2 citing sentences" || { echo "FAIL  sentence count"; fail=1; }
expect 0 "quote_check: real quotes"          python3 "$S/quote_check.py" claims.tsv
sed 's/41\.8 after/41.0 after/' claims.tsv > "$TMP/claims_bad.tsv"
expect 1 "quote_check: altered quote"        python3 "$S/quote_check.py" "$TMP/claims_bad.tsv"
expect 0 "sync_check: in sync"               python3 "$S/sync_check.py" refs.bib references_evidence.md main.tex
sed 's/41\.8 BLEU on/41.9 BLEU on/' main.tex > "$TMP/main_edited.tex"
expect 1 "sync_check: sentence edited"       python3 "$S/sync_check.py" refs.bib references_evidence.md "$TMP/main_edited.tex"
expect 1 "sync_check: fields not in MD"      python3 "$S/sync_check.py" refs_unverified.bib references_evidence.md main.tex

[ "$fail" -eq 0 ] && echo "ALL PASSED" || echo "SOME CHECKS FAILED"
exit "$fail"
