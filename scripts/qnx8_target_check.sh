#!/bin/sh
# qnx8_target_check.sh - the check to run ON a QNX 8.0 target.
#
# One command, one screen. It proves, on the target itself:
#
#   1. the system is a QNX system, and which version;
#   2. a Python 3 interpreter is available, and new enough for the package;
#   3. the frozen corpus is there, and every page matches its SHA-256;
#   4. the tool answers for the symbols that are asked.
#
# Usage (from the root of the repository, on the target):
#
#   sh scripts/qnx8_target_check.sh [CORPUS_DIR] [SYMBOL ...]
#
#   CORPUS_DIR  directory of the frozen corpus on the target. Default: the
#               QX_PORTMAP_CORPUS variable, then ./corpus of the repository.
#   SYMBOL      QNX symbols to analyse. Default: abort accept bzero.
#
# Two variables can be set instead of the arguments:
#   QX_PORTMAP_CORPUS   directory of the corpus on the target;
#   QX_PORTMAP_PYTHON   path of the Python 3 interpreter, when it is not in
#                        the PATH of the console of the target.
#
# The same command is the rehearsal on a Linux or macOS workstation: the
# script then says "NOT a QNX system - this run is a rehearsal" and proves
# the three other points. Nothing else is needed: a POSIX shell and python3.
# It installs nothing, it writes nothing in the repository, and it never
# touches the network.
#
# Exit code:
#   0  the check passed (the corpus is intact and the tool answered).
#   1  the check failed (no corpus, corrupted corpus, or the tool errored).
#   2  the check could not run at all (no Python 3 on this system).
#   3  QX_PORTMAP_REQUIRE_QNX8=1 was set and this system is not QNX 8:
#      the check itself passed, but it is a rehearsal, not the QNX 8.0 proof.
#
# The verdict line never lets a rehearsal look like the proof: it says
# "PASS - on a QNX 8 target" only when uname reports QNX with a release
# 8.x; on any other system (Linux, macOS, or QNX 7.1) it says
# "PASS (rehearsal only - this is NOT a run on QNX 8.0)".
#
# See docs/QNX-8.0-CIBLE.md for the whole procedure.

set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd) || exit 2
cd "$ROOT" || exit 2

CORPUS="${QX_PORTMAP_CORPUS:-$ROOT/corpus}"
SYMBOLS=""

if [ $# -gt 0 ]; then
    case "$1" in
        -h|--help)
            awk 'NR>1 && /^#/ {sub(/^# ?/,""); print; next} NR>1 {exit}' "$0"
            exit 0
            ;;
        *) CORPUS=$1; shift ;;
    esac
fi
for sym in "$@"; do
    SYMBOLS="$SYMBOLS $sym"
done
[ -n "$SYMBOLS" ] || SYMBOLS="abort accept bzero"

printf '== QX PORTMAP - check on the target ==\n\n'

# --- 1. the system --------------------------------------------------------
SYS=$(uname -s 2>/dev/null || echo unknown)
REL=$(uname -r 2>/dev/null || echo unknown)
ARCH=$(uname -m 2>/dev/null || echo unknown)
printf 'system      : %s %s (%s)\n' "$SYS" "$REL" "$ARCH"
QNX8=no
case "$SYS" in
    QNX*)
        case "$REL" in
            8.*)
                QNX8=yes
                printf 'target      : QNX 8 system detected (release %s)\n' "$REL"
                ;;
            *)
                printf 'target      : QNX system detected, but release %s is not 8.x - this run is NOT the QNX 8.0 proof\n' "$REL"
                ;;
        esac
        ;;
    *)
        printf 'target      : NOT a QNX system - this run is a rehearsal on %s\n' "$SYS"
        ;;
esac

# --- 2. the interpreter ---------------------------------------------------
# The interpreter of a QNX target is not always in the PATH of the console:
# QX_PORTMAP_PYTHON gives its path explicitly when it is not.
PY=""
if [ -n "${QX_PORTMAP_PYTHON:-}" ]; then
    if [ -x "$QX_PORTMAP_PYTHON" ]; then
        PY="$QX_PORTMAP_PYTHON"
    else
        printf 'python      : QX_PORTMAP_PYTHON=%s is not executable\n' "$QX_PORTMAP_PYTHON"
    fi
fi
if [ -z "$PY" ]; then
    for cand in python3 python; do
        if command -v "$cand" >/dev/null 2>&1; then
            PY="$cand"
            break
        fi
    done
fi
if [ -z "$PY" ]; then
    printf 'python      : NOT FOUND - the tool needs Python 3 on the target\n'
    printf '               (set QX_PORTMAP_PYTHON to the path of the interpreter)\n'
    printf '\nRESULT      : FAIL (no Python 3 on this system)\n'
    exit 2
fi
printf 'python      : %s\n' "$("$PY" --version 2>&1)"

# --- 2b. is that interpreter new enough for the package? ------------------
# The package qnx_portmap/ needs Python 3.4 or later: measured with
# "vermin --target=3.13- qnx_portmap/" (see docs/QNX-8.0-CIBLE.md, section 1).
# The target of the SDP 8.0.3 carries Python 3.13, so the check is a formality
# there; it is here to catch a target with an old interpreter.
if "$PY" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 4) else 1)' 2>/dev/null; then
    printf 'compat      : OK - the package needs Python 3.4 or later\n'
    RC_COMPAT=0
else
    printf 'compat      : FAIL - the package needs Python 3.4 or later\n'
    RC_COMPAT=1
fi

# --- 3. the corpus and its integrity --------------------------------------
printf 'corpus      : %s\n' "$CORPUS"
if [ ! -f "$CORPUS/MANIFEST.json" ]; then
    printf '             : MANIFEST.json absent - there is no corpus here.\n'
    printf '               The QNX documentation is not redistributed with this\n'
    printf '               repository (see CORPUS-NON-PUBLIE.txt). Build it on the\n'
    printf '               host with "bash scripts/bootstrap_corpus.sh --out corpus"\n'
    printf '               and copy it to the target, or run the quick mode on the\n'
    printf '               target itself (it needs the network).\n'
    printf '\nRESULT      : FAIL (no corpus on this system)\n'
    exit 1
fi
printf '\n-- corpus integrity --\n'
"$PY" -m qnx_portmap --corpus "$CORPUS" --verify-corpus
rc_verify=$?

# --- 4. the answers -------------------------------------------------------
printf '\n-- symbols --\n'
"$PY" -m qnx_portmap --corpus "$CORPUS" $SYMBOLS
rc_symbols=$?

# --- the verdict ----------------------------------------------------------
printf '\n-- verdict --\n'
printf 'verify-corpus exit code : %s (0 = every page matches its SHA-256)\n' "$rc_verify"
printf 'symbols exit code       : %s (0 = every symbol documented, 1 = at least one absent or unknown, 2 = error)\n' "$rc_symbols"
printf 'compat exit code        : %s (0 = the interpreter is new enough for the package)\n' "${RC_COMPAT:-1}"
printf 'QNX 8 target            : %s (%s %s)\n' "$QNX8" "$SYS" "$REL"
if [ "$rc_verify" -eq 0 ] && [ "${RC_COMPAT:-1}" -eq 0 ] && { [ "$rc_symbols" -eq 0 ] || [ "$rc_symbols" -eq 1 ]; }; then
    if [ "$QNX8" = yes ]; then
        printf 'RESULT      : PASS - on a QNX 8 target\n'
        exit 0
    fi
    printf 'RESULT      : PASS (rehearsal only - this is NOT a run on QNX 8.0)\n'
    if [ "${QX_PORTMAP_REQUIRE_QNX8:-0}" = 1 ]; then
        printf '              QX_PORTMAP_REQUIRE_QNX8=1: exit code 3 (not the QNX 8.0 proof)\n'
        exit 3
    fi
    exit 0
fi
printf 'RESULT      : FAIL\n'
exit 1
