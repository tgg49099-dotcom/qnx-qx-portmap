"""Tests de la classification : statut d'un symbole dans la documentation 8.0.

Ces tests utilisent un petit corpus synthetique (voir tests/helpers.py) :
chaque cas limite de la mission y est representes de facon deterministe.
"""

import os
import shutil
import tempfile
import unittest

from qnx_portmap.classify import (ABSENT, Classifier, DOCUMENTED, ELSEWHERE, UNKNOWN)
from qnx_portmap.corpus import Corpus

from .helpers import build_mini_corpus


class TestClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-class-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_mini_corpus(cls.root)
        cls.corpus = Corpus(cls.root)
        cls.classifier = Classifier(cls.corpus)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def classify_one(self, symbol):
        results = self.classifier.classify([symbol])
        self.assertEqual(len(results), 1)
        return results[0]

    # -- cas nominaux ----------------------------------------------------
    def test_documented_symbol(self):
        res = self.classify_one("frob")
        self.assertEqual(res.status, DOCUMENTED)
        self.assertTrue(res.url.endswith("/topic/f/frob.html"))
        self.assertEqual(res.citation, "Frob the widget")
        self.assertIn("frob() function frobs the widget", res.detail)
        self.assertTrue(res.in_71)
        self.assertTrue(res.in_80)

    def test_variable_is_documented_too(self):
        res = self.classify_one("widget")
        self.assertEqual(res.status, DOCUMENTED)
        self.assertEqual(res.kind, "variable")

    # -- cas limites de la mission ---------------------------------------
    def test_absent_symbol(self):
        """Cas limite : symbole absent de la 8.0."""
        res = self.classify_one("gone")
        self.assertEqual(res.status, ABSENT)
        self.assertTrue(res.in_71)
        self.assertFalse(res.in_80)
        self.assertIn("/7.1/", res.url)
        self.assertEqual(res.citation, "Gone since 8.0")

    def test_described_elsewhere_symbol(self):
        """Cas limite : symbole decrit ailleurs (renvoi d'index).

        Le renvoi de l'index ("The following are described elsewhere") prime
        sur une simple mention dans le corps d'une page : la citation doit
        venir de la table de l'index, pas du parcours du corpus.
        """
        res = self.classify_one("vanish")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertIn("user guide", res.citation)
        self.assertTrue(res.url.endswith("neutrino.user_guide/topic/vanish.html"), res.url)
        # la source de la citation est bien la table "described elsewhere"
        self.assertIn("described elsewhere", res.citation_source)
        # une mention trouvee par parcours du corpus aurait un autre type
        self.assertEqual(res.citation_kind, "")

    def test_symbol_cited_in_bold(self):
        """Cas limite : symbole cite en gras dans une page de la 8.0.

        Le symbole n'apparait qu'en gras, jamais sous la forme "nom(" :
        l'outil doit quand meme le trouver, et dire qu'il est cite en gras.
        """
        res = self.classify_one("bold_api")
        self.assertEqual(res.status, ELSEWHERE)
        self.assertTrue(res.url.endswith("neutrino.user_guide/topic/bold.html"), res.url)
        self.assertIn("bold_api", res.citation)
        self.assertEqual(res.citation_kind, "cite en gras")
        # la citation vient bien d'un <strong> dans la page officielle
        page = self.corpus.find_url(res.url)
        self.assertIn("<strong>bold_api</strong>", self.corpus.html(page))

    def test_english_word_mentioned_in_prose_is_not_a_symbol(self):
        """Cas limite : un mot anglais rencontre en prose n'est pas un symbole.

        "argument" apparait dans une phrase de la page officielle : le
        qualifier de "decrit ailleurs" serait faux. L'outil doit dire
        "inconnu du corpus".
        """
        res = self.classify_one("argument")
        self.assertEqual(res.status, UNKNOWN)
        self.assertEqual(res.citation, "")

    def test_duplicate_symbol_is_reported_once(self):
        """Cas limite : symbole duplique dans la liste d'entree."""
        results = self.classifier.classify(["frob", "frob", "frob"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].symbol, "frob")

    def test_empty_list(self):
        """Cas limite : liste vide."""
        results = self.classifier.classify([])
        self.assertEqual(results, [])
        self.assertEqual(Classifier.worklist(results), [])

    def test_unknown_symbol(self):
        res = self.classify_one("pas_un_symbole_qnx")
        self.assertEqual(res.status, UNKNOWN)
        self.assertFalse(res.in_71)
        self.assertFalse(res.in_80)
        self.assertEqual(res.citation, "")

    def test_empty_symbols_are_ignored(self):
        results = self.classifier.classify(["", "  ", "frob"])
        self.assertEqual([r.symbol for r in results], ["frob"])

    # -- liste de travail -------------------------------------------------
    def test_worklist_lists_absent_before_described_elsewhere(self):
        results = self.classifier.classify(["vanish", "gone", "frob"])
        worklist = Classifier.worklist(results)
        self.assertEqual([r.symbol for r in worklist], ["gone", "vanish"])
        self.assertEqual(worklist[0].status, ABSENT)
        self.assertLess(worklist[0].priority, worklist[1].priority)

    def test_documented_symbol_is_not_in_the_worklist(self):
        results = self.classifier.classify(["frob"])
        self.assertEqual(Classifier.worklist(results), [])

    def test_index_stats(self):
        stats = self.classifier.index_stats()
        self.assertEqual(stats["8.0"]["entries"], 2)
        self.assertEqual(stats["8.0"]["elsewhere"], 2)
        self.assertEqual(stats["7.1"]["entries"], 2)


if __name__ == "__main__":
    unittest.main()
