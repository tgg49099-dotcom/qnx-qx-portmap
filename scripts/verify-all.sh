#!/usr/bin/env bash
# verify-all.sh - replay every published proof of this repository, in one
# command.
#
# Usage (from the root of the repository):
#
#     bash scripts/verify-all.sh
#     bash scripts/verify-all.sh --verbose    # also print the raw output of
#                                            # every check
#
# The checks, in this order:
#
#   1  the unit test suite                  the published proofs (a) and (b)
#   2  the anti-leak control of the corpus   the published proof (d)
#   3  the published manifest                the published proof (f)
#   4  the published numbers                 every test and file count of the README
#   5  the parity of the README output block the published example of the README
#   6  the RED counter-proof                 the published proofs (c) and (i)
#   7  the lengths of the submission kit     KIT-SOUMISSION-QNX.md
#   8  the placeholders of the documents      no placeholder left, same video URL
#
# THREE STATES, NEVER MIXED
#
#   OK           the check ran, and every proof it checks was confirmed.
#   FAILED       the check ran, and the result is negative: a proof is false
#                or the code is broken.  This is a real failure.
#   NOT CHECKED  the check could not run on this machine: the frozen QNX corpus
#                is absent (the QNX documentation is not redistributed), a
#                dependency is missing.  It is NEVER a failure and NEVER a
#                success.
#
# EXIT CODE
#   0  no published proof was contradicted.  Every row that ran is OK; a row
#      that could not run on this machine is reported NOT CHECKED, never OK,
#      and the verdict says how many there were.  The exit code answers one
#      question - "did any published proof turn out to be false?" - and not
#      "was every proof re-run on this machine?".
#   1  at least one row is FAILED: a published proof is false, or the code is
#      broken.  When some rows are NOT CHECKED as well, the verdict names both.
#   2  the command itself could not run (no python3).
#
# NO FALSE GREEN AND NO FALSE RED.  A check that did not run is never reported
# as OK; a check that could not run is never reported as FAILED; the summary
# counts OK and NOT CHECKED separately, and the two are never added up.
#
# It writes nothing in the repository: the logs go to a temporary directory
# outside of it, which is removed when the command ends.  The RED
# counter-proof, which breaks a rule of the code on purpose, is replayed on a
# temporary copy of the tree, never on the checkout of the reader.  The
# command needs no network.
#
# It needs nothing but bash, python3 and the scripts of this repository.

set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd) || exit 2
cd "$ROOT" || exit 2

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is absent: the command cannot run at all (RC 2)."
    echo "  install python3 (https://www.python.org/downloads/) and run it again."
    exit 2
fi

TMP=$(mktemp -d 2>/dev/null) || exit 2
trap 'rm -rf "$TMP"' 0
trap 'rm -rf "$TMP"; exit 2' 1 2 15

VERBOSE=0
if [ "${1:-}" = "--verbose" ]; then
    VERBOSE=1
fi

# The frozen corpus of the QNX documentation is not redistributed: it is
# looked for beside the package, or through the environment variable.
CORPUS=${QX_PORTMAP_CORPUS:-$ROOT/corpus}

ROWS="$TMP/rows"
: > "$ROWS"

nb_total=0
nb_ok=0
nb_failed=0
nb_not_checked=0
nb_check=0

# record LABEL RESULT DETAIL RC LOG
record() {
    nb_total=$((nb_total + 1))
    case "$2" in
        OK) nb_ok=$((nb_ok + 1)) ;;
        FAILED) nb_failed=$((nb_failed + 1)) ;;
        *) nb_not_checked=$((nb_not_checked + 1)) ;;
    esac
    printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$ROWS"
}

# copy_tree SRC DST - copies the tree, without the caches, so that a check
# that breaks a rule on purpose never touches the checkout of the reader.
copy_tree() {
    mkdir -p "$2" || return 1
    (cd "$1" && find . -type d \
        \( -name '__pycache__' -o -name 'build' -o -name 'dist' \
           -o -name 'qnx_portmap.egg-info' \) -prune -o \
        -type f -print) | while IFS= read -r f; do
        mkdir -p "$2/$(dirname -- "$f")" || exit 1
        cp -p "$1/$f" "$2/$f" || exit 1
    done
}

echo "======================================================================================================"
echo "QX PORTMAP - replay every published proof of this repository"
echo "======================================================================================================"
echo "checks     : 8"
echo

# ---------------------------------------------------------------- 1. the suite
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
QX_PORTMAP_VERIFY_ALL_NESTED=1 python3 -B -m unittest discover -s tests -t . > "$log" 2>&1
rc=$?
n_tests=$(sed -n 's/^Ran \([0-9][0-9]*\) tests\{0,1\}.*/\1/p' "$log" | head -1)
n_skip=$(sed -n 's/^OK (skipped=\([0-9][0-9]*\))$/\1/p' "$log" | head -1)
[ -n "$n_tests" ] || n_tests="?"
[ -n "$n_skip" ] || n_skip="0"
if [ "$rc" -eq 0 ]; then
    record "unit test suite" "OK" "$n_tests tests, $n_skip skipped" "$rc" "$log"
else
    record "unit test suite" "FAILED" "the suite failed" "$rc" "$log"
fi

# ------------------------------------------------- 2. the anti-leak control
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
if [ ! -f "$CORPUS/index/pages.jsonl" ]; then
    record "anti-leak control of the QNX corpus" "NOT CHECKED" \
           "the frozen QNX corpus is absent here" "-" "$log"
else
    python3 -B scripts/controle_fuite_corpus.py --tree . --corpus "$CORPUS" > "$log" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ] && ! grep -E "correspondances" "$log" | grep -qvE ":[[:space:]]*0[[:space:]]*$"; then
        record "anti-leak control of the QNX corpus" "OK" \
               "0 match with the QNX documentation" "$rc" "$log"
    elif [ "$rc" -eq 2 ]; then
        record "anti-leak control of the QNX corpus" "NOT CHECKED" \
               "the corpus could not be read on this machine" "$rc" "$log"
    else
        record "anti-leak control of the QNX corpus" "FAILED" \
               "the control found a match in the published tree" "$rc" "$log"
    fi
fi

# ------------------------------------------------------- 3. the public manifest
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
python3 -B scripts/manifeste_publie.py --check > "$log" 2>&1
rc=$?
n_files=$(sed -n 's/.*est a jour : \([0-9][0-9]*\) fichiers.*/\1/p' "$log" | head -1)
[ -n "$n_files" ] || n_files="?"
if [ "$rc" -eq 0 ]; then
    record "published manifest" "OK" "MANIFESTE-PUBLIE.txt lists $n_files files" "$rc" "$log"
else
    record "published manifest" "FAILED" "the published manifest is obsolete" "$rc" "$log"
fi

# ------------------------------------------- 4. the published numbers
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
if [ -f "$CORPUS/index/pages.jsonl" ]; then corpus_state=present; else corpus_state=absent; fi
if [ "$n_tests" = "?" ] || [ "$n_files" = "?" ]; then
    record "published numbers of the README" "NOT CHECKED" \
           "the suite or the manifest gave no number" "-" "$log"
else
    python3 -B tools/published_counts.py --tests "$n_tests" --skipped "$n_skip" \
        --corpus "$corpus_state" --files "$n_files" > "$log" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then
        record "published numbers of the README" "OK" \
               "every published count is the real one" "$rc" "$log"
    else
        record "published numbers of the README" "FAILED" \
               "a published count is not the real one" "$rc" "$log"
    fi
fi

# --------------------------------------------- 5. the parity of the README
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
python3 -B -m unittest tests.test_readme -v > "$log" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then
    record "parity of the README output block" "FAILED" \
           "the README is not the real output" "$rc" "$log"
elif grep -qE "^OK \(skipped=[0-9]+\)" "$log"; then
    record "parity of the README output block" "NOT CHECKED" \
           "the frozen corpus is absent here" "$rc" "$log"
else
    record "parity of the README output block" "OK" \
           "the README shows the real output" "$rc" "$log"
fi

# -------------------------------------------------- 6. the RED counter-proof
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
if copy_tree "$ROOT" "$TMP/tree"; then
    (cd "$TMP/tree" && python3 -B tools/contre_epreuve.py) > "$log" 2>&1
    rc=$?
    n1=$(sed -n 's/^\([0-9][0-9]*\) \/ \([0-9][0-9]*\) contre-epreuves concluantes.*/\1/p' "$log" | head -1)
    n2=$(sed -n 's/^\([0-9][0-9]*\) \/ \([0-9][0-9]*\) contre-epreuves concluantes.*/\2/p' "$log" | head -1)
    if [ "$rc" -eq 0 ] && [ -n "$n1" ]; then
        record "RED counter-proof" "OK" "$n1 / $n2 rules counter-proved" "$rc" "$log"
    elif grep -q "the repository must be clean" "$log"; then
        record "RED counter-proof" "NOT CHECKED" \
               "the working copy is not clean" "$rc" "$log"
    else
        record "RED counter-proof" "FAILED" "a rule could not be counter-proved" "$rc" "$log"
    fi
else
    record "RED counter-proof" "NOT CHECKED" "the temporary copy failed" "-" "$log"
fi

# -------------------------------------------- 7. the lengths of the submission kit
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
python3 -B tools/mesure_kit.py --check > "$log" 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
    record "lengths of the submission kit" "OK" \
           "every measured length matches the text" "$rc" "$log"
else
    record "lengths of the submission kit" "FAILED" \
           "a measured length does not match the text" "$rc" "$log"
fi

# ------------------------------------------ 8. the placeholders of the documents
nb_check=$((nb_check + 1))
log="$TMP/log-$nb_check"
python3 -B tools/controle_placeholders.py > "$log" 2>&1
rc=$?
n_place=$(sed -n 's/^CONTROL OF THE PLACEHOLDERS - \([0-9][0-9]*\) published documents.*/\1/p' "$log" | head -1)
[ -n "$n_place" ] || n_place="?"
if [ "$rc" -eq 0 ]; then
    record "placeholders and draft banners" "OK" \
           "nothing left in the $n_place published documents" "$rc" "$log"
else
    record "placeholders and draft banners" "FAILED" \
           "a placeholder or a draft banner is left" "$rc" "$log"
fi

# ------------------------------------------------------------------ the table
echo "======================================================================================================"
echo "SUMMARY - one line per verification"
echo "======================================================================================================"
printf '%-42s %-12s %-46s %s\n' "VERIFICATION" "RESULT" "DETAIL" "EXIT"
printf '%-42s %-12s %-46s %s\n' \
       "------------------------------------------" \
       "------------" \
       "------------------------------------------------" \
       "----"
while IFS="$(printf '\t')" read -r label result detail rc log; do
    printf '%-42s %-12s %-46s %s\n' "$label" "$result" "$detail" "$rc"
done < "$ROWS"
echo "======================================================================================================"

# The raw output of a check is printed when it failed, and for every check
# with --verbose.  It never contains a path of this repository: the output is
# the same on every machine.
while IFS="$(printf '\t')" read -r label result detail rc log; do
    if [ "$VERBOSE" -eq 1 ] || [ "$result" = "FAILED" ]; then
        echo
        echo "---- raw output: $label ----"
        tail -n 25 "$log" 2>/dev/null
    fi
done < "$ROWS"

if [ "$nb_failed" -gt 0 ] && [ "$nb_not_checked" -gt 0 ]; then
    echo "VERDICT: FAILED AND NOT CHECKED - $nb_failed check(s) FAILED and"
    echo "         $nb_not_checked check(s) could not run out of $nb_total (RC 1)"
    echo "         this is NOT a success: the table above says which row is which."
    RC=1
elif [ "$nb_not_checked" -gt 0 ]; then
    echo "VERDICT: NO CHECK FAILED - $nb_ok/$nb_total OK, $nb_not_checked NOT CHECKED (RC 0)"
    echo "         the check(s) that could not run on this machine are named in the"
    echo "         table above and are never reported as OK: nothing was disproved,"
    echo "         but these proofs were NOT re-run here."
    RC=0
elif [ "$nb_failed" -gt 0 ]; then
    echo "VERDICT: FAILED - $nb_failed check(s) failed out of $nb_total (RC 1)"
    RC=1
else
    echo "VERDICT: EVERY CHECK PASSED - $nb_ok/$nb_total OK (RC 0)"
    RC=0
fi
echo "======================================================================================================"
exit "$RC"
