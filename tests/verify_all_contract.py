"""The one-command proof of the repository must obey a strict contract.

``scripts/verify-all.sh`` is the command a judge runs to replay every
published proof of this repository.  Its contract is:

* on a tree without the frozen QNX corpus, the command exits **0** and says
  ``NO CHECK FAILED``; the checks that could not run are reported
  ``NOT CHECKED`` and are never counted as ``OK``;
* when a published proof is false, the command exits **1** and names the
  failed check.

This test proves both, on a temporary copy of the tree: the green run and the
red run.  It is the counter-proof of the contract itself - a test that has
never been seen to fail proves nothing.

It also checks that the command writes nothing in the tree it runs on.

This file is named ``verify_all_contract.py`` and not ``test_verify_all.py``
on purpose: it is not part of the discovery of the unit test suite, so the
number of tests published in the README stays true (it is checked by
the fourth row of the command, ``published numbers of the README``).  It is run on its
own, with one command::

    python3 -m unittest tests.verify_all_contract
"""

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "verify-all.sh")

# The caches are not part of the published tree and are not compared.
IGNORED_DIRS = (".git", "__pycache__", "build", "dist", "qnx_portmap.egg-info")

GREEN_VERDICT = re.compile(
    r"VERDICT: NO CHECK FAILED - (\d+)/(\d+) OK, (\d+) NOT CHECKED \(RC 0\)")


def copy_tree(dst):
    """Copies the working tree (without the caches) into *dst*."""
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "build", "dist", "*.pyc", "*.pyo"))


def run_verify_all(tree):
    """Runs the command in *tree* and returns (exit code, output)."""
    proc = subprocess.run(["bash", "scripts/verify-all.sh"], cwd=tree,
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def summary_rows(out):
    """Reads the table of the command and returns one list per row."""
    rows = []
    in_table = False
    for line in out.splitlines():
        if line.startswith("VERIFICATION"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("====="):
            break
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 4:
            rows.append(parts)
    return rows


def digest_tree(tree):
    """A digest of every published file of the tree."""
    digest = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for name in sorted(filenames):
            if name.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, name)
            digest.update(os.path.relpath(full, tree).encode("utf-8"))
            with open(full, "rb") as handle:
                digest.update(handle.read())
    return digest.hexdigest()


class TestVerifyAllContract(unittest.TestCase):
    def test_verify_all_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            green = os.path.join(tmp, "green")
            copy_tree(green)
            before = digest_tree(green)
            code, out = run_verify_all(green)

            # 1. the green run: nothing is disproved, so the exit code is 0
            self.assertEqual(code, 0, "verify-all.sh must exit 0 when no "
                             "published proof is contradicted:\n%s" % out)
            match = GREEN_VERDICT.search(out)
            self.assertIsNotNone(match, "the verdict is missing or malformed:\n%s" % out)
            ok, total, not_checked = (int(match.group(1)), int(match.group(2)),
                                      int(match.group(3)))
            # 2. NOT CHECKED is counted apart, never as OK
            self.assertEqual(ok + not_checked, total,
                             "the OK count and the NOT CHECKED count must "
                             "add up to the number of checks")
            self.assertGreater(not_checked, 0,
                               "without the frozen corpus, some checks cannot "
                               "run and must be reported NOT CHECKED")
            self.assertLess(ok, total,
                            "the checks that could not run must never be "
                            "presented as successes")
            rows = summary_rows(out)
            self.assertEqual(len(rows), 8)
            self.assertEqual([r[1] for r in rows].count("FAILED"), 0,
                             "no check may fail on a sound tree:\n%s" % out)

            # 3. the command writes nothing in the tree it runs on
            self.assertEqual(before, digest_tree(green),
                             "verify-all.sh must not write in the repository")

            # 4. the red run: a published proof is broken -> exit code 1
            red = os.path.join(tmp, "red")
            copy_tree(red)
            with open(os.path.join(red, "README.md"), "ab") as handle:
                handle.write(b"\n")       # the manifest no longer matches
            code, out = run_verify_all(red)
            self.assertEqual(code, 1, "verify-all.sh must exit 1 when a "
                             "published proof is false:\n%s" % out)
            rows = summary_rows(out)
            failed = [r for r in rows if r[1] == "FAILED"]
            self.assertEqual(len(failed), 1,
                             "exactly one check must fail:\n%s" % out)
            self.assertEqual(failed[0][0], "published manifest")
            self.assertIn("VERDICT: FAILED", out)

            # 5. the red run of the published numbers: the README announces
            # one test more than the suite has -> that row fails (the
            # manifest is regenerated so that it is the only false proof)
            red2 = os.path.join(tmp, "red2")
            copy_tree(red2)
            path = os.path.join(red2, "README.md")
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            match = re.search(r"Result measured on [^:]+: \*\*(\d+) tests", text)
            self.assertIsNotNone(match)
            text = (text[:match.start(1)] + str(int(match.group(1)) + 1)
                    + text[match.end(1):])
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            subprocess.run(["python3", "-B", "scripts/manifeste_publie.py"],
                           cwd=red2, capture_output=True, check=True)
            code, out = run_verify_all(red2)
            self.assertEqual(code, 1, "a false test count must fail:\n%s" % out)
            failed = [r[0] for r in summary_rows(out) if r[1] == "FAILED"]
            self.assertEqual(failed, ["published numbers of the README"], out)


if __name__ == "__main__":
    unittest.main()
