"""Mode anglais de la console : ``--lang en`` couvre TOUTE la sortie.

La regle du concours impose l'anglais pour tout le materiel de soumission.
Le francais reste la langue par defaut, octet pour octet : ce fichier le
verifie des deux cotes.
"""

import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from qnx_portmap import classify as classify_mod
from qnx_portmap import cli as cli_mod
from qnx_portmap import report as report_mod
from qnx_portmap.cli import main
from qnx_portmap.classify import Classifier
from qnx_portmap.corpus import Corpus

from .helpers import build_fixture_corpus

# Mots et tournures purement francais : aucun ne doit apparaitre sur une
# ligne de la sortie console en mode anglais. Le match respecte les
# frontieres de mots : "documente" ne declenche pas sur "documented",
# "exemples" ne declenche pas sur "examples".
FRENCH_MARKERS = [
    "etat des symboles", "corpus fige", "consulte le", "mode hors ligne",
    "aucun symbole", "documente", "decrit", "absent de la", "absent de tout",
    "inconnu", "voir", "liste de travail", "mise a niveau", "rien a migrer",
    "cite par le guide", "entree d'index", "en gras", "appel de fonction",
    "present en", "nouveau en", "erreur de saisie", "seulement mentionne",
    "appele", "introuvable", "analyser", "analyse", "symbole", "symboles",
    "statut", "page officielle", "citation exacte", "priorite", "verifiees",
    "attendu", "obtenu", "echec", "racine", "livres", "repertoire",
    "solutions", "chemin", "illisible", "fichier", "telechargee",
    "telechargement", "reconstruit", "reconstruire", "rechargement",
    "acces reseau", "defaut", "exemples", "sortie", "entree standard",
    "statistiques", "verifier", "visee", "langue", "sha-256 des", "fichiers",
]

# Paires fr/en dont la seule difference est l'espace avant le deux-points
# (typographie francaise) : aucun mot francais a detecter.
SPACING_ONLY = {"by_version", "corpus_root"}

# "oui"/"non" sont trop courts pour des marqueurs de mots ("non-blocking"
# dans une citation serait un faux positif) : couverts par le check dedie
# des cellules du tableau Markdown, voir test_en_markdown_cells.
CELL_ONLY = {"yes", "no"}

_MARKER_RX = [(m, re.compile(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % re.escape(m)))
              for m in FRENCH_MARKERS]


def _marker_hits(text):
    """Liste des marqueurs francais trouves dans un texte, avec leur ligne."""
    hits = []
    for lineno, line in enumerate(text.lower().splitlines(), 1):
        for marker, rx in _MARKER_RX:
            if rx.search(line):
                hits.append((lineno, marker))
                break
    return hits


def _pairs():
    """Toutes les paires (fr, en) qui different, des tables de libelles."""
    tables = (classify_mod.NOTES, report_mod.TEXT_STRINGS,
              report_mod.MD_STRINGS, cli_mod.CLI_STRINGS, cli_mod.HELP_STRINGS)
    for table in tables:
        for key, fr in table["fr"].items():
            if key in SPACING_ONLY or key in CELL_ONLY:
                continue
            en = table["en"][key]
            values = fr.items() if isinstance(fr, dict) else [(key, fr)]
            for sub, fr_val in values:
                en_val = en[sub] if isinstance(fr, dict) else en
                if fr_val != en_val:
                    yield key, fr_val


def run_cli(argv):
    """Lance la CLI et renvoie (code de sortie, sortie standard + erreurs)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:           # --help, erreurs fatales
            if isinstance(exc.code, int):
                code = exc.code
            elif exc.code is None:
                code = 0
            else:
                err.write(str(exc.code) + "\n")   # message fatale
                code = 1
    return code, out.getvalue() + err.getvalue()


class TestLangEn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-lang-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_fixture_corpus(cls.root)
        classifier = Classifier(Corpus(cls.root))
        elsewhere = sorted(classifier.elsewhere)
        absent = sorted(set(classifier.prev_entries)
                        - set(classifier.entries) - set(classifier.elsewhere))
        # jeu deterministe couvrant tous les statuts disponibles du corpus
        cls.symbols = (sorted(classifier.entries)[:1] + elsewhere[:1]
                       + absent[:1] + ["zzz_unknown_symbol"])
        cls.statuses = {r.status for r in classifier.classify(cls.symbols)}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_symbol_set_covers_the_statuses(self):
        # le jeu doit au moins couvrir documente et inconnu ; decrit ailleurs
        # et absent le sont aussi quand le corpus de test les fournit
        self.assertIn("documented", self.statuses)
        self.assertIn("unknown", self.statuses)

    # -- mode anglais : 0 ligne francaise sur toute la sortie --------------
    def test_en_query_text_is_english(self):
        code, out = run_cli(["--corpus", self.root, "--lang", "en"] + self.symbols)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])
        self.assertIn("frozen corpus:", out)
        self.assertIn("consulted on", out)
        self.assertIn("--- Upgrade worklist", out)

    def test_en_json_and_markdown_are_english(self):
        for fmt, marker in (("json", '"status": "documented"'),
                            ("markdown", "| Symbol | Status")):
            code, out = run_cli(["--corpus", self.root, "--format", fmt,
                                 "--lang", "en"] + self.symbols)
            self.assertFalse(_marker_hits(out), (fmt, _marker_hits(out)[:5]))
            self.assertIn(marker, out)

    def test_en_markdown_cells(self):
        # contre-preuve dediee aux paires oui/non : cellules du tableau
        _, out = run_cli(["--corpus", self.root, "--format", "markdown",
                          "--lang", "en"] + self.symbols)
        self.assertNotIn("| oui |", out)
        self.assertNotIn("| non |", out)
        self.assertTrue("| yes |" in out or "| no |" in out)
        _, fr = run_cli(["--corpus", self.root, "--format", "markdown"]
                        + self.symbols)
        self.assertTrue("| oui |" in fr or "| non |" in fr)

    def test_en_verify_corpus_is_english(self):
        code, out = run_cli(["--corpus", self.root, "--verify-corpus",
                             "--lang", "en"])
        self.assertEqual(code, 0)
        self.assertIn("pages checked:", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

    def test_en_stats_are_english(self):
        code, out = run_cli(["--corpus", self.root, "--stats", "--lang", "en"])
        self.assertEqual(code, 0)
        self.assertIn("consulted on", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

    def test_en_help_is_english(self):
        code, out = run_cli(["--lang", "en", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("Examples:", out)
        self.assertIn("output language", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

    def test_en_error_paths_are_english(self):
        code, out = run_cli(["--corpus", "/absent", "--lang", "en"])
        self.assertEqual(code, 2)
        self.assertIn("corpus not found", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

        code, out = run_cli(["--corpus", self.root, "--lang", "en"])
        self.assertEqual(code, 2)
        self.assertIn("no symbol given", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

        code, out = run_cli(["--corpus", self.root, "--file", "/nonexistent",
                             "--lang", "en", "abort"])
        self.assertIn("unreadable file", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

    def test_en_notes_follow_the_language(self):
        corpus = Corpus(self.root)
        base = Classifier(corpus)
        everywhere = (sorted(base.entries) + sorted(base.elsewhere)
                      + sorted(set(base.prev_entries) - set(base.entries)))
        for lang, must_be_french in (("en", False), ("fr", True)):
            classifier = Classifier(Corpus(self.root), lang=lang)
            results = classifier.classify(everywhere + ["zzz_unknown_symbol"])
            blob = "\n".join("%s\n%s\n%s" % (r.note, r.citation_kind, r.detail)
                             for r in results)
            hits = _marker_hits(blob)
            if must_be_french:
                self.assertTrue(hits)
            else:
                self.assertFalse(hits, hits[:5])

    # -- mode par defaut : inchange, octet pour octet ----------------------
    def test_default_mode_is_frozen(self):
        code_d, out_d = run_cli(["--corpus", self.root] + self.symbols)
        code_f, out_f = run_cli(["--corpus", self.root, "--lang", "fr"] + self.symbols)
        self.assertEqual(code_d, code_f)
        self.assertEqual(out_d, out_f)
        # le francais est bien la (contre-preuve du detecteur)
        self.assertTrue(_marker_hits(out_d))
        self.assertIn("corpus fige", out_d)
        # sortie figee : empreinte du texte, chemin du corpus masque
        masked = out_d.replace(self.root, "<CORPUS>")
        digest = hashlib.sha256(masked.encode("utf-8")).hexdigest()
        self.assertEqual(digest, FROZEN_FR_SHA256)

    # -- contre-epreuve structurelle : chaque paire traduite est couverte --
    def test_every_translated_string_is_caught_by_a_marker(self):
        missed = [s for _, s in _pairs() if not _marker_hits(s)]
        self.assertEqual(missed, [])


FROZEN_FR_SHA256 = "c7bebbecdf55c548bd51eec6e74e2ffacf7c7ab7460d7720f2d5da7fd43eaf10"
