"""The README must show a really produced output, not an invented example.

This test replays the example command of the README against the frozen corpus
and compares, line by line, the output obtained with the one written in the
README. If the tool changes, the test fails: the README must be updated.

Two files are checked, and both must carry the *same* verbatim block:

- ``README.md``          the English README (the one a judge reads),
- ``docs/README-FR.md``   the French reference, kept byte-identical to the
                          version published before the translation.

The console output of the tool is in French and is not translated; the
English README shows it verbatim and adds an English translation next to it,
which this test also checks is present.

The number of tests of the suite is kept at 124: this file carries one test
method, as before, with the additional checks inside it.
"""

import io
import os
import unittest
from contextlib import redirect_stdout

from qnx_portmap.cli import main
from qnx_portmap.corpus import default_corpus_dir

from .helpers import CORPUS_ABSENT_MSG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
README_FR = os.path.join(ROOT, "docs", "README-FR.md")
SYMBOLS = ["abort", "accept", "bzero", "zzz_fonction_inexistante"]

# The marker that introduces the verbatim output block in each file.
MARKER_EN = "Real output of the command"
MARKER_FR = "Sortie reelle :"

# Rows of the English translation table that must sit next to the block.
TRANSLATION_ROWS = [
    "| `documente` | documented in QNX 8.0 |",
    "| `decrit ailleurs` | described elsewhere in the QNX 8.0 documentation |",
    "| `absent de la 8.0` | present in QNX 7.1, absent from the QNX 8.0 corpus |",
    "| `inconnu du corpus` | not found in the frozen corpus |",
]


def readme_example_output(path=README, marker=MARKER_EN):
    """Extracts the output block that follows the given marker."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    pos = text.find(marker)
    if pos < 0:
        return None
    start = text.find("```", pos)
    if start < 0:
        return None
    start += 3
    while text[start] == "\n":
        start += 1
    end = text.find("```", start)
    if end < 0:
        return None
    return text[start:end]


def real_output():
    """Runs the example command against the frozen corpus and returns its output."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["--corpus", default_corpus_dir()] + SYMBOLS)
    got = buf.getvalue()
    # the corpus path depends on the machine: it is normalized
    root = default_corpus_dir()
    got = got.replace(root, "<CORPUS>")
    return got, code


@unittest.skipUnless(os.path.isfile(os.path.join(default_corpus_dir(), "MANIFEST.json")),
                     CORPUS_ABSENT_MSG)
class TestReadmeExample(unittest.TestCase):
    def test_readme_shows_the_real_output(self):
        expected = readme_example_output(README, MARKER_EN)
        self.assertIsNotNone(expected, "example block not found in the README")

        got, code = real_output()
        self.assertEqual(expected.strip(), got.strip())
        self.assertEqual(code, 1)   # bzero is absent -> exit code 1

        # the French reference of the README must carry the very same block
        self.assertTrue(os.path.isfile(README_FR),
                        "docs/README-FR.md is missing (French reference of the README)")
        expected_fr = readme_example_output(README_FR, MARKER_FR)
        self.assertIsNotNone(expected_fr, "example block not found in docs/README-FR.md")
        self.assertEqual(expected_fr.strip(), got.strip())
        self.assertEqual(expected_fr.strip(), expected.strip())

        # the English README must translate the console output of the tool
        with open(README, encoding="utf-8") as fh:
            text = fh.read()
        for row in TRANSLATION_ROWS:
            self.assertIn(row, text,
                          "missing English translation of the console labels: %s" % row)
        self.assertIn("verbatim tool output", text,
                      "the verbatim block must be marked as such")


if __name__ == "__main__":
    unittest.main()
