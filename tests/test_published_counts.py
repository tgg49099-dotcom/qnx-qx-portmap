"""The checker of the published numbers must catch a false number.

``tools/published_counts.py`` compares every test and file count written in
the README, the French README, the submission kit and the two LISEZMOI files with the values measured by
``scripts/verify-all.sh``.  These tests run it on a small synthetic tree:
a sound tree is green, one false number is caught (and only that one), a
reworded claim is caught, and the skip counts are never reported OK when the
corpus is present.
"""

import os
import tempfile
import unittest

from tools.published_counts import check

README = """Result measured on 15 November 2026: **{n} tests, exit code 0**, without

| Corpus in `corpus/`, next to the package | {n} tests, **0 skipped**, exit code 0 |
| Corpus through `QX_PORTMAP_CORPUS` | {n} tests, **1 skipped**, exit code 0 |
| Corpus absent | {n} tests, **{s} skipped**, exit code 0 |

{n} tests, no dependency, **no network access**. Two cases:

The {p} other tests pass **without the corpus**. Among them

unit test suite                            OK           {n} tests, {s} skipped                          0
published manifest                         OK           MANIFESTE-PUBLIE.txt lists {f} files           0
"""
LISEZMOI = "Working V0. **{n} tests, all green** ({s} of them are skipped when\n"
PKG = "python3 -m unittest discover -s tests -t .   # {n} tests: green, {s} skipped without corpus\n"
README_FR = """Result measured on 16 November 2026: **{n} tests, exit code 0**, without

| Corpus in `corpus/`, next to the package | {n} tests, **0 skipped**, exit code 0 |
| Corpus through `QX_PORTMAP_CORPUS` | {n} tests, **1 skipped**, exit code 0 |
| Corpus absent | {n} tests, **{s} skipped**, exit code 0 |

{n} tests, aucune dependance, **aucun acces reseau**. Trois cas :

| Corpus dans `corpus/` (a cote du paquet) | {n} tests, **0 skip**, code de sortie 0 |
| Corpus via `QX_PORTMAP_CORPUS` | {n} tests, **1 skip**, code de sortie 0 |
| Corpus absent | {n} tests, **{s} skip**, code de sortie 0 |

Les {s} tests sautes sont ceux qui exigent le corpus complet

Les {p} autres tests passent **sans corpus**.
"""
KIT = """{n} tests, no third-party dependency, no network access. Measured on
16 November 2026 in the three possible configurations: with the corpus in
`corpus/` next to the package, {n} tests and 0 skipped; with the corpus
pointed to by the environment variable `QX_PORTMAP_CORPUS`, {n} tests and 1
skipped; without any corpus, {n} tests and {s} skipped (the skipped ones are
"""


def make_tree(root, n=10, s=3, f=7, p=None, fr_n=None):
    if p is None:
        p = n - s
    os.makedirs(os.path.join(root, "qnx_portmap"))
    with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as h:
        h.write(README.format(n=n, s=s, f=f, p=p))
    with open(os.path.join(root, "LISEZMOI.md"), "w", encoding="utf-8") as h:
        h.write(LISEZMOI.format(n=n, s=s))
    with open(os.path.join(root, "qnx_portmap", "LISEZMOI.md"), "w", encoding="utf-8") as h:
        h.write(PKG.format(n=n, s=s))
    os.makedirs(os.path.join(root, "docs"))
    with open(os.path.join(root, "docs", "README-FR.md"), "w", encoding="utf-8") as h:
        h.write(README_FR.format(n=n if fr_n is None else fr_n, s=s, p=n - s))
    with open(os.path.join(root, "KIT-SOUMISSION-QNX.md"), "w", encoding="utf-8") as h:
        h.write(KIT.format(n=n, s=s))


class TestPublishedCounts(unittest.TestCase):
    def test_sound_tree_is_green(self):
        with tempfile.TemporaryDirectory() as root:
            make_tree(root)
            rows, failed = check(root, 10, 3, False, 7)
            self.assertEqual(failed, 0, rows)
            self.assertTrue(all(r[4] == "OK" for r in rows), rows)

    def test_one_false_number_is_caught(self):
        with tempfile.TemporaryDirectory() as root:
            make_tree(root, p=6)          # "The 6 other tests" instead of 7
            rows, failed = check(root, 10, 3, False, 7)
            self.assertEqual(failed, 1, rows)
            bad = [r for r in rows if r[4] == "FAILED"]
            self.assertIn("run without the corpus", bad[0][1])
            self.assertEqual((bad[0][2], bad[0][3]), (6, 7))

    def test_stale_test_count_is_caught_everywhere(self):
        with tempfile.TemporaryDirectory() as root:
            make_tree(root, n=10)
            rows, failed = check(root, 11, 3, False, 7)  # one test was added
            self.assertGreaterEqual(failed, 8, rows)

    def test_stale_french_readme_is_caught(self):
        # 16/11/2026: docs/README-FR.md still said 124 tests while the suite
        # had 183, because the French README was not checked at all.
        with tempfile.TemporaryDirectory() as root:
            make_tree(root, fr_n=9)
            rows, failed = check(root, 10, 3, False, 7)
            self.assertEqual(failed, 8, rows)
            self.assertEqual({r[0] for r in rows if r[4] == "FAILED"},
                             {"docs/README-FR.md"})

    def test_reworded_claim_is_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as root:
            make_tree(root)
            path = os.path.join(root, "LISEZMOI.md")
            with open(path, "w", encoding="utf-8") as h:
                h.write("Working V0. Many tests, all green.\n")
            rows, failed = check(root, 10, 3, False, 7)
            self.assertEqual(failed, 1, rows)
            self.assertEqual([r[4] for r in rows if r[0] == "LISEZMOI.md"],
                             ["FAILED (claim not found)"])

    def test_skip_counts_not_checked_with_corpus(self):
        with tempfile.TemporaryDirectory() as root:
            make_tree(root)
            rows, failed = check(root, 10, 0, True, 7)
            self.assertEqual(failed, 0, rows)
            states = {r[4] for r in rows if "[skipped]" in r[1] or "[passing]" in r[1]}
            self.assertEqual(states, {"NOT CHECKED (corpus present)"})


if __name__ == "__main__":
    unittest.main()
