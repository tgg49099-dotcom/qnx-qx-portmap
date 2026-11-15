"""The English output shown in the README must be the real ``--lang en`` output.

A judge reads the README in English and runs the quick start with
``--lang en``.  This test replays the command against the frozen corpus and
checks two things:

- the complete English block of the README ("English output (real):") is,
  line by line, the real output of ``--lang en``;
- every line of the quick-start excerpt (the ``...`` lines aside) appears in
  the real output, in the same order.

It needs the frozen corpus, like ``tests/test_readme.py``: without it, it is
skipped, never failed.
"""

import io
import os
import unittest
from contextlib import redirect_stdout

from qnx_portmap.cli import main
from qnx_portmap.corpus import default_corpus_dir

from .helpers import CORPUS_ABSENT_MSG
from .test_readme import README, SYMBOLS, readme_example_output

MARKER_FULL = "English output (real):"
MARKER_QUICK = "Excerpt of the **real output** with `--lang en`"


def real_output_en():
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["--corpus", default_corpus_dir(), "--lang", "en"] + SYMBOLS)
    return buf.getvalue().replace(default_corpus_dir(), "<CORPUS>"), code


@unittest.skipUnless(os.path.isfile(os.path.join(default_corpus_dir(), "MANIFEST.json")),
                     CORPUS_ABSENT_MSG)
class TestReadmeEnglishOutput(unittest.TestCase):
    def test_readme_english_output_is_real(self):
        got, code = real_output_en()
        self.assertEqual(code, 1)   # bzero is absent -> exit code 1

        full = readme_example_output(README, MARKER_FULL)
        self.assertIsNotNone(full, "English output block not found in the README")
        self.assertEqual(full.strip(), got.strip())

        quick = readme_example_output(README, MARKER_QUICK)
        self.assertIsNotNone(quick, "quick-start excerpt not found in the README")
        if quick.startswith("text\n"):   # the language tag of the code fence
            quick = quick[len("text\n"):]
        real_lines = got.splitlines()
        pos = 0
        for line in quick.splitlines():
            if not line.strip() or line.strip() == "...":
                continue
            try:
                pos = real_lines.index(line, pos) + 1
            except ValueError:
                self.fail("quick-start line not in the real --lang en output, "
                          "or out of order: %r" % line)


if __name__ == "__main__":
    unittest.main()
