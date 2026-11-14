"""Tests du corpus : chargement, integrite, corruption."""

import os
import shutil
import tempfile
import unittest

from qnx_portmap.corpus import (Corpus, CorpusError, default_corpus_dir, read_symbols)

from .helpers import CORPUS_ABSENT_MSG, build_mini_corpus


class TestReadSymbols(unittest.TestCase):
    def test_reads_one_per_line(self):
        self.assertEqual(read_symbols("abort\nbzero\n"), ["abort", "bzero"])

    def test_reads_comma_separated(self):
        self.assertEqual(read_symbols("abort, bzero, pthread_create"),
                         ["abort", "bzero", "pthread_create"])

    def test_ignores_comments_and_blanks(self):
        self.assertEqual(read_symbols("# un commentaire\n\nabort  # ici\n"),
                         ["abort"])

    def test_removes_duplicates(self):
        self.assertEqual(read_symbols("abort\nabort\nbzero\n"), ["abort", "bzero"])


class TestMiniCorpus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qxpm-test-")
        self.root = os.path.join(self.tmp, "corpus")
        build_mini_corpus(self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_loads_pages_and_manifest(self):
        corpus = Corpus(self.root)
        self.assertEqual(corpus.manifest["pages_total"], 8)
        self.assertEqual(len(corpus.pages), 8)
        self.assertEqual(corpus.manifest["pages_by_version"]["8.0"], 6)

    def test_integrity_ok_on_fresh_corpus(self):
        corpus = Corpus(self.root)
        report = corpus.verify()
        self.assertTrue(report["ok"], report["failed"])
        self.assertEqual(report["checked"], 8)

    def test_detects_a_corrupted_page(self):
        """Cas limite : fichier de corpus corrompu."""
        target = os.path.join(self.root, "pages", "8.0", "com.qnx.doc.neutrino.lib_ref",
                              "topic", "f", "frob.html.gz")
        with open(target, "ab") as fh:
            fh.write(b"\x00corruption")
        corpus = Corpus(self.root)
        report = corpus.verify()
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["failed"]), 1)
        self.assertIn("frob.html", report["failed"][0][0])

    def test_detects_a_corrupted_sha256sums_file(self):
        sums = os.path.join(self.root, "SHA256SUMS")
        with open(sums, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        lines[0] = ("0" * 64) + "  " + lines[0].split("  ", 1)[1]
        with open(sums, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        corpus = Corpus(self.root)
        report = corpus.verify_sha256sums()
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["failed"]), 1)

    def test_missing_corpus_raises(self):
        with self.assertRaises(CorpusError):
            Corpus(os.path.join(self.tmp, "pas-la"))

    def test_missing_manifest_raises(self):
        empty = os.path.join(self.tmp, "vide")
        os.makedirs(empty)
        with self.assertRaises(CorpusError):
            Corpus(empty)

    def test_missing_page_is_reported_as_a_failure(self):
        corpus = Corpus(self.root)
        os.remove(os.path.join(self.root, "pages", "8.0", "com.qnx.doc.neutrino.lib_ref",
                               "topic", "f", "frob.html.gz"))
        report = corpus.verify()
        self.assertFalse(report["ok"])
        self.assertIn("frob.html", report["failed"][0][0])
        page = corpus.find_url("https://www.qnx.com/developers/docs/8.0/"
                                "com.qnx.doc.neutrino.lib_ref/topic/f/frob.html")
        with self.assertRaises(CorpusError):
            corpus.raw_bytes(page)

    def test_page_content_is_readable(self):
        corpus = Corpus(self.root)
        page = corpus.find_url("https://www.qnx.com/developers/docs/8.0/"
                                "com.qnx.doc.neutrino.lib_ref/topic/f/frob.html")
        self.assertIsNotNone(page)
        self.assertIn("Frob the widget", corpus.text(page))


class TestCorpusLocation(unittest.TestCase):
    """Ou l'outil cherche le corpus fige."""

    def setUp(self):
        self.old = os.environ.get("QX_PORTMAP_CORPUS")

    def tearDown(self):
        if self.old is None:
            os.environ.pop("QX_PORTMAP_CORPUS", None)
        else:
            os.environ["QX_PORTMAP_CORPUS"] = self.old

    def test_env_var_has_priority(self):
        os.environ["QX_PORTMAP_CORPUS"] = "/tmp/corpus-de-test"
        self.assertEqual(default_corpus_dir(), "/tmp/corpus-de-test")

    def test_repo_corpus_is_found_without_env_var(self):
        """Si le corpus est present, l'outil le trouve sans variable d'env.

        Le corpus n'est pas distribue avec le depot : ce test est donc
        saute (et non en echec) quand il est absent.
        """
        os.environ.pop("QX_PORTMAP_CORPUS", None)
        path = default_corpus_dir()
        if not os.path.isfile(os.path.join(path, "MANIFEST.json")):
            self.skipTest(CORPUS_ABSENT_MSG)
        self.assertTrue(os.path.isfile(os.path.join(path, "MANIFEST.json")),
                        "corpus introuvable dans : %s" % path)


if __name__ == "__main__":
    unittest.main()
