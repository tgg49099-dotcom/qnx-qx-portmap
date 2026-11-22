"""Tests d'integration sur le corpus reellement fige dans le depot.

Ces tests verifient que le corpus livre est bien complet, integre et
exploitable, et que la reponse de l'outil sur des symboles reels est la
bonne (page officielle + citation exacte).
"""

import os
import re
import unittest

from qnx_portmap.classify import (ABSENT, Classifier, DOCUMENTED, ELSEWHERE, UNKNOWN)
from qnx_portmap.corpus import Corpus, default_corpus_dir

from .helpers import CORPUS_ABSENT_MSG, frozen_corpus_dir, frozen_corpus_skip_reason

# The frozen corpus of the project: the one in the tree, or the one that
# QX_PORTMAP_CORPUS points to when it is that very corpus (fingerprint).
CORPUS_DIR = frozen_corpus_dir()


def corpus_available():
    return CORPUS_DIR is not None


@unittest.skipUnless(corpus_available(), frozen_corpus_skip_reason())
class TestFrozenCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus(CORPUS_DIR)
        cls.classifier = Classifier(cls.corpus)

    # -- integrite --------------------------------------------------------
    def test_corpus_is_complete(self):
        man = self.corpus.manifest
        self.assertEqual(man["pages_total"], 3426)
        self.assertEqual(man["pages_by_version"]["8.0"], 2226)
        self.assertEqual(man["pages_by_version"]["7.1"], 1200)
        self.assertEqual(len(self.corpus.pages), man["pages_total"])

    def test_every_page_matches_its_sha256(self):
        report = self.corpus.verify()
        self.assertTrue(report["ok"], report["failed"][:3])
        self.assertEqual(report["checked"], 3426)

    def test_sha256sums_covers_the_corpus(self):
        report = self.corpus.verify_sha256sums()
        self.assertTrue(report["ok"], report["failed"][:3])
        self.assertEqual(report["checked"], man_pages(self.corpus))

    def test_manifest_documents_the_sources(self):
        man = self.corpus.manifest
        self.assertEqual(man["consulted"], "2026-11-14")
        self.assertEqual(man["docs_root"]["8.0"],
                         "https://www.qnx.com/developers/docs/8.0/")

    # -- index ------------------------------------------------------------
    def test_index_8_0_counts(self):
        stats = self.classifier.index_stats()
        self.assertEqual(stats["8.0"]["entries"], 1907)
        self.assertEqual(stats["8.0"]["elsewhere"], 211)

    def test_index_7_1_counts(self):
        stats = self.classifier.index_stats()
        self.assertEqual(stats["7.1"]["entries"], 2024)
        self.assertEqual(stats["7.1"]["elsewhere"], 89)

    def test_new_and_removed_symbols(self):
        cur = set(self.classifier.entries)
        prev = set(self.classifier.prev_entries)
        self.assertEqual(len(cur - prev), 89)
        self.assertEqual(len(prev - cur), 206)

    # -- reponses reelles -------------------------------------------------
    def classify_one(self, symbol):
        results = self.classifier.classify([symbol])
        self.assertEqual(len(results), 1)
        return results[0]

    def test_documented_symbol(self):
        res = self.classify_one("abort")
        self.assertEqual(res.status, DOCUMENTED)
        self.assertEqual(res.url, "https://www.qnx.com/developers/docs/8.0/"
                                  "com.qnx.doc.neutrino.lib_ref/topic/a/abort.html")
        self.assertEqual(res.citation, "Raise the SIGABRT signal to terminate program execution")
        self.assertIn("abort() function causes abnormal process termination", res.detail)

    def test_absent_symbol(self):
        res = self.classify_one("bzero")
        self.assertEqual(res.status, ABSENT)
        self.assertIn("/7.1/", res.url)
        self.assertEqual(res.citation, "Set the first part of an object to null bytes")

    def test_described_elsewhere_symbol(self):
        res = self.classify_one("accept")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertIn("FreeBSD documentation", res.citation)
        self.assertTrue(any("man.freebsd.org" in u for u in res.see_urls))

    def test_symbol_cited_in_bold(self):
        """Cas limite reel : rw_interrupt est cite en gras dans la doc 8.0."""
        res = self.classify_one("rw_interrupt")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertTrue(res.url.endswith("callout_rwstorage.html"), res.url)
        self.assertIn("rw_interrupt", res.citation)
        page = self.corpus.find_url(res.url)
        self.assertRegex(self.corpus.html(page),
                          r"<strong[^>]*>\s*rw_interrupt\s*</strong>")

    def test_unknown_symbol(self):
        res = self.classify_one("symbole_qui_nexiste_pas_qnx")
        self.assertEqual(res.status, UNKNOWN)
        self.assertEqual(res.citation, "")

    def test_duplicate_symbol(self):
        results = self.classifier.classify(["abort", "abort"])
        self.assertEqual(len(results), 1)

    def test_empty_list(self):
        self.assertEqual(self.classifier.classify([]), [])

    def test_gaps_are_all_resolved(self):
        """Les 203 ecarts 7.1 -> 8.0 sont tous classes (aucun inconnu)."""
        cur = set(self.classifier.entries)
        prev = set(self.classifier.prev_entries)
        gaps = sorted(prev - cur)
        self.assertEqual(len(gaps), 206)
        results = self.classifier.classify(gaps)
        self.assertEqual([r for r in results if r.status == UNKNOWN], [])
        # Studio 19/11/2026 : 14 de ces ecarts sont annonces « removed » par
        # le guide officiel de migration ; ils passent de ELSEWHERE a ABSENT.
        self.assertEqual(len([r for r in results if r.status == ELSEWHERE]), 118)
        self.assertEqual(len([r for r in results if r.status == ABSENT]), 88)
        self.assertEqual(len([r for r in results if r.removed_by_migration_guide]), 14)

    def test_worklist_is_ordered_by_priority(self):
        results = self.classifier.classify(["bzero", "accept", "abort"])
        worklist = Classifier.worklist(results)
        self.assertEqual([r.symbol for r in worklist], ["bzero", "accept"])
        self.assertEqual(worklist[0].status, ABSENT)
        self.assertLess(worklist[0].priority, worklist[1].priority)


def man_pages(corpus):
    """Nombre de fichiers listes dans SHA256SUMS (pages + index)."""
    return corpus.manifest["files"]


if __name__ == "__main__":
    unittest.main()
