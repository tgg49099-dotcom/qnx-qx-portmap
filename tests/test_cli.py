"""Tests de l'interface en ligne de commande."""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout

from qnx_portmap.cli import main

from .helpers import build_mini_corpus


def run(argv):
    """Lance la CLI et renvoie (code de sortie, sortie standard)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-cli-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_mini_corpus(cls.root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_text_output(self):
        code, out = run(["--corpus", self.root, "frob"])
        self.assertEqual(code, 0)
        self.assertIn("frob", out)
        self.assertIn("documente", out)
        self.assertIn("Frob the widget", out)

    def test_json_output(self):
        code, out = run(["--corpus", self.root, "--format", "json", "frob", "gone"])
        self.assertEqual(code, 1)  # "gone" est absent -> code 1
        payload = json.loads(out)
        self.assertEqual(payload["counts"]["symbols"], 2)
        self.assertEqual(payload["counts"]["documented"], 1)
        self.assertEqual(payload["counts"]["absent"], 1)
        self.assertEqual(payload["symbols"][0]["symbol"], "frob")
        self.assertTrue(payload["corpus"]["offline"])

    def test_markdown_output(self):
        code, out = run(["--corpus", self.root, "--format", "markdown", "frob"])
        self.assertEqual(code, 0)
        self.assertIn("| Symbole |", out)
        self.assertIn("`frob`", out)

    def test_input_from_file(self):
        path = os.path.join(self.tmp, "symboles.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# liste\nfrob\ngone\n")
        code, out = run(["--corpus", self.root, "--format", "json", "--file", path])
        payload = json.loads(out)
        self.assertEqual([s["symbol"] for s in payload["symbols"]], ["frob", "gone"])

    def test_duplicate_symbols_are_collapsed(self):
        code, out = run(["--corpus", self.root, "--format", "json", "frob", "frob"])
        payload = json.loads(out)
        self.assertEqual(payload["counts"]["symbols"], 1)

    def test_no_symbol_returns_error(self):
        code, out = run(["--corpus", self.root])
        self.assertEqual(code, 2)

    def test_missing_corpus_returns_error(self):
        code, out = run(["--corpus", os.path.join(self.tmp, "absent"), "frob"])
        self.assertEqual(code, 2)

    def test_verify_corpus_ok(self):
        code, out = run(["--corpus", self.root, "--verify-corpus"])
        self.assertEqual(code, 0)
        self.assertIn("SHA-256 des pages : OK", out)

    def test_verify_corpus_detects_corruption(self):
        root = os.path.join(self.tmp, "corpus-corrompu")
        build_mini_corpus(root)
        target = os.path.join(root, "pages", "8.0", "com.qnx.doc.neutrino.lib_ref",
                              "topic", "f", "frob.html.gz")
        with open(target, "ab") as fh:
            fh.write(b"\x00")
        code, out = run(["--corpus", root, "--verify-corpus"])
        self.assertEqual(code, 1)
        self.assertIn("ECHEC", out)

    def test_stats(self):
        code, out = run(["--corpus", self.root, "--stats"])
        self.assertEqual(code, 0)
        self.assertIn("pages", out)


if __name__ == "__main__":
    unittest.main()
