"""Checks that the numbers published in the documentation are the real ones.

The README tells a judge how many tests the suite has, how many are skipped
without the frozen corpus, and how many files the published manifest lists.
These numbers drift every time a test or a file is added.  This tool reads
every such claim and compares it with the values measured by
``scripts/verify-all.sh`` on the same tree.  Every LISEZMOI file that
publishes a test count is checked too: a number written in a file of the
package must be the real one, exactly like the numbers of the README.

The documents a judge reads are checked as well - the two codelabs, the usage
guide, the video plan and the French LISEZMOI file publish the same counts:
a count that drifts there is a count the judge reads.

Usage (called by ``scripts/verify-all.sh``, check 4)::

    python3 tools/published_counts.py --tests 170 --skipped 27 \\
        --corpus absent --files 108

Exit code: 0 when every claim matches, 1 when one claim is false or when an
expected claim is not found any more (a reworded sentence must be checked
again, never silently dropped), 2 on a usage error.

The skip counts of the README describe a tree *without* the corpus; when the
corpus is present they cannot be measured, so they are reported
NOT CHECKED, never OK.

THE PUBLISHED RED COUNTER-PROOF

``docs/contre-epreuve-rouge.txt`` keeps the real output of the two runs of
``tools/contre_epreuve.py`` and names the commit it was measured on.  That
claim is true only while the code the twelve rules break has not changed, so
it is checked here instead of being trusted: the commit must exist, it must
be an ancestor of HEAD, and nothing under ``qnx_portmap/``, no discovered test
(``tests/test*.py``) and no ``tools/contre_epreuve.py`` may have changed
since it was measured.  A tree without a ``.git`` directory (the ZIP of the
repository) cannot answer that question: the claim is then reported NOT
CHECKED, never OK.
"""

import argparse
import os
import re
import subprocess
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
    ("docs/README-FR.md", "quick start: tests measured",
     r"Result measured on [^:]+: \*\*(\d+) tests, exit code 0\*\*", ["tests"]),
    ("docs/README-FR.md", "quick start: corpus next to the package",
     r"\| Corpus in `corpus/`[^|]*\| (\d+) tests, \*\*0 skipped\*\*", ["tests"]),
    ("docs/README-FR.md", "quick start: corpus through the variable",
     r"\| Corpus through `QX_PORTMAP_CORPUS` \| (\d+) tests, \*\*1 skipped\*\*", ["tests"]),
    ("docs/README-FR.md", "quick start: corpus absent",
     r"\| Corpus absent \| (\d+) tests, \*\*(\d+) skipped\*\*", ["tests", "skipped"]),
    ("docs/README-FR.md", "section Tests (fr): number of tests",
     r"^(\d+) tests, aucune dependance", ["tests"]),
    ("docs/README-FR.md", "section Tests (fr): corpus next to the package",
     r"\| Corpus dans `corpus/`[^|]*\| (\d+) tests, \*\*0 skip\*\*", ["tests"]),
    ("docs/README-FR.md", "section Tests (fr): corpus through the variable",
     r"\| Corpus via `QX_PORTMAP_CORPUS` \| (\d+) tests, \*\*1 skip\*\*", ["tests"]),
    ("docs/README-FR.md", "section Tests (fr): corpus absent",
     r"\| Corpus absent \| (\d+) tests, \*\*(\d+) skip\*\*", ["tests", "skipped"]),
    ("docs/README-FR.md", "section Tests (fr): skipped tests",
     r"Les (\d+) tests sautes sont ceux", ["skipped"]),
    ("docs/README-FR.md", "section Tests (fr): tests that run without the corpus",
     r"Les (\d+) autres tests passent \*\*sans corpus\*\*", ["passing"]),
    ("KIT-SOUMISSION-QNX.md", "project story: number of tests",
     r"^(\d+) tests, no third-party dependency", ["tests"]),
    ("KIT-SOUMISSION-QNX.md", "project story: the three configurations",
     r"`corpus/` next to the package, (\d+) tests and 0 skipped; with the corpus\s+"
     r"pointed to by the environment variable `QX_PORTMAP_CORPUS`, (\d+) tests and 1\s+"
     r"skipped; without any corpus, (\d+) tests and (\d+) skipped",
     ["tests", "tests", "tests", "skipped"]),
    ("LISEZMOI.md", "state of the project",
     r"\*\*(\d+) tests, all green\*\* \((\d+) of them are skipped", ["tests", "skipped"]),
    ("qnx_portmap/LISEZMOI.md", "verification commands",
     r"# (\d+) tests: green, (\d+) skipped without corpus", ["tests", "skipped"]),
    ("tests/LISEZMOI.md", "verification commands",
     r"# (\d+) tests: green, (\d+) skipped without corpus", ["tests", "skipped"]),
    ("qnx_portmap/LISEZMOI-FR.md", "verification commands (fr)",
     r"# (\d+) tests : verts, (\d+) sautes sans corpus", ["tests", "skipped"]),
    ("docs/codelab/QX-PORTMAP-CODELAB.md", "the unit test suite alone",
     r"Ran (\d+) tests in [\d.]+s\s*\n\s*\nOK \(skipped=(\d+)\)", ["tests", "skipped"]),
    ("docs/CODELAB-COMMUNITY-QNX.md", "the unit test suite",
     r"Ran (\d+) tests in [\d.]+s\s*\n\s*\nOK \(skipped=(\d+)\)", ["tests", "skipped"]),
    ("docs/UTILISATION.md", "the suite without the corpus",
     r"Without the corpus: (\d+) tests, (\d+) of them skipped", ["tests", "skipped"]),
    ("VIDEO-YOUTUBE-QNX-PORTMAP.md", "the suite of today",
     r"the published suite answers (\d+) tests", ["tests"]),
    ("VIDEO-YOUTUBE-QNX-PORTMAP.md", "the suite of today, in the filming table",
     r"the published suite has grown to (\d+) tests", ["tests"]),
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


def check_counter_proof(root):
    """Checks that the published counter-proof is still measured on this code.

    Returns one row: (file, label, claim, real, state).  The claim is the
    short commit the published file names, the real value is the code it was
    measured on.  A tree that is not a git repository cannot answer the
    question, and the row is then NOT CHECKED, never OK.
    """
    label = "the published counter-proof is still measured on this code"
    path = os.path.join(root, "docs/contre-epreuve-rouge.txt")
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return ("docs/contre-epreuve-rouge.txt", label, "-", "-",
                "FAILED (file missing)")
    match = re.search(r"^Commit mesure : ([0-9a-f]{40})$", text, re.MULTILINE)
    if not match:
        return ("docs/contre-epreuve-rouge.txt", label, "-", "-",
                "FAILED (the measured commit is not named)")
    sha = match.group(1)
    short = sha[:7]
    if not os.path.isdir(os.path.join(root, ".git")):
        return ("docs/contre-epreuve-rouge.txt", label, short, "-",
                "NOT CHECKED (not a git repository)")

    def git(*args):
        try:
            proc = subprocess.run(["git", "-C", root] + list(args),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return 127, ""
        return proc.returncode, proc.stdout.decode("utf-8", "replace").strip()

    rc, _ = git("cat-file", "-e", sha + "^{commit}")
    if rc != 0:
        return ("docs/contre-epreuve-rouge.txt", label, short, "-",
                "FAILED (the measured commit is unknown)")
    rc, _ = git("merge-base", "--is-ancestor", sha, "HEAD")
    if rc != 0:
        return ("docs/contre-epreuve-rouge.txt", label, short, "-",
                "FAILED (the measured commit is not an ancestor of HEAD)")
    rc, out = git("diff", "--name-only", sha, "--",
                  "qnx_portmap/", "tests/test*.py", "tools/contre_epreuve.py")
    # a file that is not tracked yet is not seen by "git diff": it is looked
    # for separately, or a new file could slip under the measurement
    rc, untracked = git("ls-files", "--others", "--exclude-standard", "--",
                        "qnx_portmap/", "tests/test*.py",
                        "tools/contre_epreuve.py")
    changed = " ".join((out + " " + untracked).split())
    if changed:
        return ("docs/contre-epreuve-rouge.txt", label, short, "-",
                "FAILED (the measured code changed: %s)" % changed)
    return ("docs/contre-epreuve-rouge.txt", label, short, "same code", "OK")


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
    rows.append(check_counter_proof(args.root))
    for name, label, claim, real, state in rows:
        print("%-24s %-58s published %-5s real %-5s %s"
              % (name, label, claim, real, state))
    n_failed = len([r for r in rows if r[4].startswith("FAILED")])
    n_ok = len([r for r in rows if r[4] == "OK"])
    print("published numbers: %d OK, %d FAILED, %d NOT CHECKED"
          % (n_ok, n_failed, len(rows) - n_ok - n_failed))
    return 1 if n_failed else 0


if __name__ == "__main__":
    sys.exit(main())
