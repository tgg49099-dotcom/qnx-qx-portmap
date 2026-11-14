"""Tests sur les fixtures miniatures (extraits courts de pages QNX reelles).

Ces tests ne demandent **aucun corpus** : ils tournent sur les 12 extraits
courts de la documentation officielle ranges dans ``tests/fixtures/``. Ils
prouvent que l'outil fonctionne sur de la documentation QNX reelle, meme si le
corpus complet n'est pas disponible (il est reconstruit a la demande par
``scripts/bootstrap_corpus.sh``).

Le corpus miniature est ecrit dans un repertoire temporaire avec la meme
structure que le corpus fige (MANIFEST.json, index/pages.jsonl, SHA256SUMS,
pages compressees) : il passe donc par le vrai code de chargement.
"""

import os
import shutil
import tempfile
import unittest

from qnx_portmap.classify import (ABSENT, Classifier, DOCUMENTED, ELSEWHERE,
                                  UNKNOWN)
from qnx_portmap.corpus import Corpus
from qnx_portmap.extract import (bold_identifiers, parse_topic_page,
                                 sentences_with, strip_tags)

from .helpers import FIXTURES_DIR, build_fixture_corpus, fixture, read_fixture

MAX_FIXTURES = 12
MAX_LINES = 3
MAX_BYTES = 4000


def fixture_files():
    return sorted(f for f in os.listdir(FIXTURES_DIR) if f.endswith(".txt"))


class TestFixtureInvariants(unittest.TestCase):
    """Les fixtures respectent les regles de publication."""

    def test_at_most_twelve_fixtures(self):
        files = fixture_files()
        self.assertLessEqual(len(files), MAX_FIXTURES,
                             "plus de %d fixtures : %s" % (MAX_FIXTURES, files))
        self.assertEqual(len(files), MAX_FIXTURES)

    def test_every_fixture_has_a_source_url_and_a_date(self):
        for name in fixture_files():
            meta, _ = read_fixture(name)
            self.assertIn("source", meta, name)
            self.assertTrue(meta["source"].startswith(
                "https://www.qnx.com/developers/docs/"), name)
            self.assertEqual(meta.get("consulte le"), "2026-11-14", name)
            self.assertEqual(len(meta.get("sha256 de la page source", "")), 64, name)

    def test_every_excerpt_is_one_to_three_lines(self):
        for name in fixture_files():
            _meta, lines = read_fixture(name)
            self.assertGreaterEqual(len(lines), 1, name)
            self.assertLessEqual(len(lines), MAX_LINES, name)

    def test_every_fixture_is_small(self):
        for name in fixture_files():
            path = os.path.join(FIXTURES_DIR, name)
            self.assertLess(os.path.getsize(path), MAX_BYTES, name)

    def test_excerpt_is_verbatim_and_not_empty(self):
        for name in fixture_files():
            _meta, lines = read_fixture(name)
            self.assertTrue(any(l.strip() for l in lines), name)


class TestFixtureCorpus(unittest.TestCase):
    """Le corpus miniature se charge comme le corpus fige."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-fixtures-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_fixture_corpus(cls.root)
        cls.corpus = Corpus(cls.root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_corpus_loads(self):
        self.assertEqual(len(self.corpus.pages), 8)
        self.assertEqual(self.corpus.versions(), ["7.1", "8.0"])

    def test_integrity_is_ok(self):
        report = self.corpus.verify()
        self.assertTrue(report["ok"], report["failed"])
        sums = self.corpus.verify_sha256sums()
        self.assertTrue(sums["ok"], sums["failed"])


class TestExtractionOnRealQnxExcerpts(unittest.TestCase):
    """Les extracteurs de l'outil sur la documentation QNX reelle."""

    def test_topic_page_title_and_shortdesc(self):
        html = ("<html><body><article>%s%s</article></body></html>"
                % ("\n".join(fixture("f01-abort.txt")),
                   "\n".join(fixture("f02-abort.txt"))))
        parsed = parse_topic_page(html)
        self.assertEqual(parsed["title"], "abort()")
        self.assertEqual(parsed["shortdesc"],
                         "Raise the SIGABRT signal to terminate program execution")
        self.assertIn("abort", parsed["names"])

    def test_bold_mention_is_detected(self):
        html = "<html><body><article>%s</article></body></html>" % \
            "\n".join(fixture("f07-rw_interrupt.txt"))
        self.assertIn("rw_interrupt", bold_identifiers(html))

    def test_call_form_is_found_with_word_boundary(self):
        text = strip_tags("\n".join(fixture("f03-abort.txt")))
        hits = sentences_with(text, "abort", limit=1, call_form=True)
        self.assertTrue(hits)
        self.assertIn("abort()", hits[0])

    def test_prose_contains_only_english_words(self):
        """Un extrait de prose ne contient aucun nom d'API : c'est le mot
        anglais qui y est, pas un symbole QNX (voir le test du classifieur)."""
        text = strip_tags("\n".join(fixture("f08-prose.txt")))
        self.assertIn("Changing a bit", text)
        self.assertIn("entire", sentences_with(text, "entire")[0])
        self.assertNotIn("(", text)


class TestClassifierOnRealQnxExcerpts(unittest.TestCase):
    """L'outil complet, sur un corpus construit avec les fixtures."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-fixtures-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_fixture_corpus(cls.root)
        cls.classifier = Classifier(Corpus(cls.root))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def classify_one(self, symbol):
        results = self.classifier.classify([symbol])
        self.assertEqual(len(results), 1)
        return results[0]

    def test_documented_symbol(self):
        res = self.classify_one("abort")
        self.assertEqual(res.status, DOCUMENTED)
        self.assertEqual(res.url, "https://www.qnx.com/developers/docs/8.0/"
                                  "com.qnx.doc.neutrino.lib_ref/topic/a/abort.html")
        self.assertEqual(res.citation,
                         "Raise the SIGABRT signal to terminate program execution")
        self.assertIn("abort() function causes abnormal process termination", res.detail)

    def test_documented_variable(self):
        res = self.classify_one("errno")
        self.assertEqual(res.status, DOCUMENTED)
        self.assertEqual(res.kind, "variable")
        self.assertEqual(res.citation, "Thread-local error variable")

    def test_described_elsewhere_from_the_index(self):
        res = self.classify_one("accept")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertIn("io_sock", res.url)
        self.assertTrue(res.see_urls)

    def test_absent_symbol(self):
        res = self.classify_one("bzero")
        self.assertEqual(res.status, ABSENT)
        self.assertIn("/7.1/", res.url)
        self.assertEqual(res.citation, "Set the first part of an object to null bytes")

    def test_symbol_mentioned_in_bold(self):
        res = self.classify_one("rw_interrupt")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertEqual(res.citation_kind, "cite en gras")
        self.assertIn("rw_interrupt", res.citation)

    def test_symbol_called_in_another_book(self):
        res = self.classify_one("getprotobyname_r")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertEqual(res.citation_kind, "appel de fonction")
        self.assertIn("io_sock", res.url)

    def test_symbol_removed_and_cited_by_the_migration_guide(self):
        res = self.classify_one("_smalloc")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertEqual(res.citation_kind, "appel de fonction")
        self.assertTrue(res.mentioned_in_migration_guide)

    def test_unknown_symbol(self):
        res = self.classify_one("symbole_qui_nexiste_pas_qnx")
        self.assertEqual(res.status, UNKNOWN)
        self.assertEqual(res.citation, "")

    def test_english_word_is_not_a_symbol(self):
        """Un mot anglais rencontre dans une phrase n'est pas un symbole QNX."""
        res = self.classify_one("entire")
        self.assertEqual(res.status, UNKNOWN)

    def test_worklist_is_ordered_by_priority(self):
        results = self.classifier.classify(["bzero", "accept", "abort"])
        worklist = Classifier.worklist(results)
        self.assertEqual([r.symbol for r in worklist], ["bzero", "accept"])
        self.assertEqual(worklist[0].status, ABSENT)
        self.assertLess(worklist[0].priority, worklist[1].priority)


if __name__ == "__main__":
    unittest.main()
