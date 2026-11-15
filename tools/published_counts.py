"""Checks that the numbers published in the documentation are the real ones.

The README tells a judge how many tests the suite has, how many are skipped
without the frozen corpus, and how many files the published manifest lists.
These numbers drift every time a test or a file is added.  This tool reads
every such claim and compares it with the values measured by
``scripts/verify-all.sh`` on the same tree.

Usage (called by ``scripts/verify-all.sh``, check 4)::

    python3 tools/published_counts.py --tests 158 --skipped 25 \\
        --corpus absent --files 105

Exit code: 0 when every claim matches, 1 when one claim is false or when an
expected claim is not found any more (a reworded sentence must be checked
again, never silently dropped), 2 on a usage error.

The skip counts of the README describe a tree *without* the corpus; when the
corpus is present they cannot be measured, so they are reported
NOT CHECKED, never OK.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (file, label, regex, meaning of each group)
# meanings: "tests" = total number of tests, "skipped" = tests skipped
# without the corpus, "passing" = tests that run without the corpus,
# "files" = files listed by the published manifest.
CLAIMS = [
    ("README.md", "quick start: tests measured",
     r"Result measured on [^:]+: \*\*(\d+) tests, exit code 0\*\*", ["tests"]),
    ("README.md", "table row: corpus beside the package",
     r"\| Corpus in `corpus/`[^|]*\| (\d+) tests, \*\*0 skipped\*\*", ["tests"]),
    ("README.md", "table row: corpus through the variable",
     r"\| Corpus (?:through|via) `QX_PORTMAP_CORPUS` \| (\d+) tests, \*\*1 skipped\*\*",
     ["tests"]),
    ("README.md", "table row: corpus absent",
     r"\| Corpus absent \| (\d+) tests, \*\*(\d+) skipped\*\*", ["tests", "skipped"]),
    ("README.md", "section Tests: number of tests",
     r"^(\d+) tests, no dependency", ["tests"]),
    ("README.md", "section Tests: tests that run without the corpus",
     r"The (\d+) other tests pass \*\*without the corpus\*\*", ["passing"]),
    ("README.md", "verify-all block: unit test suite",
     r"unit test suite\s+OK\s+(\d+) tests, (\d+) skipped", ["tests", "skipped"]),
    ("README.md", "verify-all block: published manifest",
     r"MANIFESTE-PUBLIE\.txt lists (\d+) files", ["files"]),
    ("LISEZMOI.md", "state of the project",
     r"\*\*(\d+) tests, all green\*\* \((\d+) of them are skipped", ["tests", "skipped"]),
    ("qnx_portmap/LISEZMOI.md", "verification commands",
     r"# (\d+) tests: green, (\d+) skipped without corpus", ["tests", "skipped"]),
]


def check(root, tests, skipped, corpus_present, files):
    """Returns (rows, n_failed); each row is (file, label, claim, real, state)."""
    real = {"tests": tests, "files": files}
    if not corpus_present:
        real["skipped"] = skipped
        real["passing"] = tests - skipped
    rows = []
    for name, label, pattern, meanings in CLAIMS:
        path = os.path.join(root, name)
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            rows.append((name, label, "-", "-", "FAILED (file missing)"))
            continue
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if not matches:
            rows.append((name, label, "-", "-", "FAILED (claim not found)"))
            continue
        for match in matches:
            for group, meaning in enumerate(meanings, start=1):
                claim = int(match.group(group))
                if meaning not in real:
                    rows.append((name, label + " [" + meaning + "]", claim, "?",
                                 "NOT CHECKED (corpus present)"))
                elif claim == real[meaning]:
                    rows.append((name, label + " [" + meaning + "]", claim,
                                 real[meaning], "OK"))
                else:
                    rows.append((name, label + " [" + meaning + "]", claim,
                                 real[meaning], "FAILED"))
    n_failed = len([r for r in rows if r[4].startswith("FAILED")])
    return rows, n_failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tests", type=int, required=True)
    parser.add_argument("--skipped", type=int, required=True)
    parser.add_argument("--corpus", choices=("absent", "present"), required=True)
    parser.add_argument("--files", type=int, required=True)
    parser.add_argument("--root", default=ROOT)
    args = parser.parse_args(argv)
    rows, n_failed = check(args.root, args.tests, args.skipped,
                           args.corpus == "present", args.files)
    for name, label, claim, real, state in rows:
        print("%-24s %-58s published %-5s real %-5s %s"
              % (name, label, claim, real, state))
    n_ok = len([r for r in rows if r[4] == "OK"])
    print("published numbers: %d OK, %d FAILED, %d NOT CHECKED"
          % (n_ok, n_failed, len(rows) - n_ok - n_failed))
    return 1 if n_failed else 0


if __name__ == "__main__":
    sys.exit(main())
