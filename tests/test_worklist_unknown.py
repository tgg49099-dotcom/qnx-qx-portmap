"""An unknown symbol is never silently left out of the upgrade worklist.

Found on 16 November 2026 while filming the demo: in quick mode,
``--quick MsgSend ... bzero`` printed ``bzero  unknown`` and then
"(nothing to migrate: every analyzed symbol is documented in 8.0)", which
is false. The worklist only holds decided symbols (absent, described
elsewhere); the unknown ones are now named after it, in text and Markdown,
in English and French, in full and quick mode.
"""

import os
import shutil
import tempfile
import unittest

from qnx_portmap.classify import Classifier
from qnx_portmap.corpus import Corpus

from .helpers import build_fixture_corpus
from .test_lang_en import run_cli


class TestWorklistUnknown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-unknown-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_fixture_corpus(cls.root)
        classifier = Classifier(Corpus(cls.root))
        cls.documented = sorted(classifier.entries)[0]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def cli(self, *argv):
        return run_cli(["--corpus", self.root] + list(argv))

    def test_documented_plus_unknown_does_not_claim_everything_is_documented(self):
        code, out = self.cli(self.documented, "zzz_unknown_symbol")
        self.assertEqual(code, 1)
        self.assertNotIn("every analyzed symbol is documented", out)
        self.assertIn("(nothing to migrate among the decided symbols)", out)
        self.assertIn("(+ 1 unknown symbol(s), not in this list: zzz_unknown_symbol", out)

    def test_only_documented_keeps_the_old_sentence(self):
        code, out = self.cli(self.documented)
        self.assertEqual(code, 0)
        self.assertIn("(nothing to migrate: every analyzed symbol is documented in 8.0)", out)
        self.assertNotIn("unknown symbol(s)", out)

    def test_french_names_the_unknown_symbols_too(self):
        _, out = self.cli("--lang", "fr", self.documented, "zzz_unknown_symbol")
        self.assertNotIn("tous les symboles analyses sont documentes", out)
        self.assertIn("(rien a migrer parmi les symboles tranches)", out)
        self.assertIn("(+ 1 symbole(s) inconnu(s), hors de cette liste : zzz_unknown_symbol", out)

    def test_markdown_names_the_unknown_symbols(self):
        _, out = self.cli("--lang", "en", "--format", "markdown",
                          self.documented, "zzz_unknown_symbol")
        self.assertNotIn("_No symbol to migrate._", out)
        self.assertIn("_No symbol to migrate among the decided ones._", out)
        self.assertIn("_Unknown, not in this list: `zzz_unknown_symbol`._", out)

    def test_worklist_only_mode_names_them(self):
        _, out = self.cli("--worklist", self.documented, "zzz_a", "zzz_b")
        self.assertIn("(+ 2 unknown symbol(s), not in this list: zzz_a, zzz_b", out)


if __name__ == "__main__":
    unittest.main()
