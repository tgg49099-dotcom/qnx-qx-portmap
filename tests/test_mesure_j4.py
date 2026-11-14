"""La mesure J4 doit etre vraie, pas seulement ecrite.

Le critere J4 de la fiche est un **taux** : le nombre de symboles QNX
reellement utilises par de vrais projets que l'outil reussit a resoudre *et*
a citer, sur 100.

Un taux se peut etre maquiller de deux manieres :

* en rearrangeant l'echantillon pour ne garder que des symboles faciles ;
* en comptant comme « resolu » des symboles qui ne le sont pas.

Les tests de ce fichier ferment les deux portes :

1. **Le taux calcule par le script est identique au taux compte a la main**
   sur dix symboles donnes dans le test (etat, symbole, etat attendu
   verifies a la main dans ``docs/mesure-J4.md``) ;
2. **La liste des 100 symboles est bien formee** : pas de symbole vide, pas
   de doublon, 20 symboles par depot, 5 depots, chaque etat dans les trois
   etats prevus, chaque symbole « resolu et cite » avec une page et une
   citation ;
3. **Le taux publie franchit le seuil J4 de 80 %** : si une mesure future
   tombait sous le seuil, ce test echoue et le dossier de soumission doit
   changer de cap ;
4. **La mesure est reproductible** : rejouer l'outil sur les 100 symboles
   (corpus fige) redonne exactement les statuts publies.

Les tests qui ont besoin du corpus complet sont **sautes** quand le corpus
n'est pas present (message : "corpus absent : lancer scripts/bootstrap_corpus.sh").
"""

import importlib.util
import json
import os
import re
import unittest

from qnx_portmap.classify import Classifier
from qnx_portmap.corpus import Corpus, default_corpus_dir

from .helpers import CORPUS_ABSENT_MSG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESURE_DIR = os.path.join(ROOT, "docs", "mesure-J4")
MESURE_JSON = os.path.join(MESURE_DIR, "mesure-J4.json")
MESURE_MD = os.path.join(ROOT, "docs", "mesure-J4.md")
SEUIL_J4 = 80.0

RESOLU = "resolu_et_cite"
AILLEURS = "resolu_mais_decrit_ailleurs"
NON_RESOLU = "non_resolu"


def load_mesure_module():
    """Charge ``tools/mesure_j4.py`` (le dossier tools/ n'est pas un paquet)."""
    path = os.path.join(ROOT, "tools", "mesure_j4.py")
    spec = importlib.util.spec_from_file_location("mesure_j4", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mesure = load_mesure_module()


def load_data():
    with open(MESURE_JSON, encoding="utf-8") as fh:
        return json.load(fh)


# Les dix symboles du controle a la main. L'etat de chacun a ete relu dans
# la documentation QNX 8.0 (voir docs/mesure-J4.md et les pages de citations
# docs/mesure-J4/citations-*.txt). Sept sont resolus et cites, deux sont
# documentes ailleurs, un a disparu de la reference 8.0 : le taux compte a
# la main est donc 7 / 10 = 70 %.
MAIN_DIX = [
    ("GETIOVLEN", RESOLU),
    ("resmgr_attach", RESOLU),
    ("iofunc_open", RESOLU),
    ("ThreadCtl", RESOLU),
    ("devctl", RESOLU),
    ("slogf", RESOLU),
    ("ConnectAttach", RESOLU),
    ("InterruptAttach", AILLEURS),
    ("setsockopt", AILLEURS),
    ("fcfgopen", NON_RESOLU),
]
TAUX_MAIN = 70.0


class TestTauxCompteALaMain(unittest.TestCase):
    """Le taux du script doit etre celui qu'on compte a la main."""

    def test_le_taux_du_script_egale_le_taux_compte_a_la_main(self):
        data = load_data()
        par_symbole = {r["symbol"]: r for r in data["symbols"]}
        records = []
        for symbole, etat in MAIN_DIX:
            self.assertIn(symbole, par_symbole,
                          "%s n'est pas dans l'echantillon publie" % symbole)
            records.append(par_symbole[symbole])
        # 1. le taux calcule par le script de mesure
        calcule = mesure.taux(records)
        # 2. le taux compte a la main, sur les dix symboles du test
        a_la_main = 100.0 * sum(1 for _s, e in MAIN_DIX if e == RESOLU) / len(MAIN_DIX)
        self.assertEqual(a_la_main, TAUX_MAIN)
        self.assertAlmostEqual(calcule, a_la_main, places=6,
                               msg="le taux du script (%s) n'est pas celui "
                                   "compte a la main (%s)" % (calcule, a_la_main))

    def test_les_etats_publies_des_dix_symboles_sont_bien_ceux_du_test(self):
        data = load_data()
        par_symbole = {r["symbol"]: r for r in data["symbols"]}
        for symbole, etat in MAIN_DIX:
            self.assertEqual(par_symbole[symbole]["etat"], etat,
                             "etat publie incorrect pour %s" % symbole)

    def test_un_taux_sur_zero_leve_une_erreur(self):
        with self.assertRaises(ValueError):
            mesure.taux([])


class TestEchantillon(unittest.TestCase):
    """La liste des 100 symboles doit etre bien formee."""

    def setUp(self):
        self.data = load_data()

    def test_cent_symbols_distincts(self):
        symbols = [r["symbol"] for r in self.data["symbols"]]
        self.assertEqual(len(symbols), 100)
        self.assertEqual(len(set(symbols)), 100, "doublon dans l'echantillon")

    def test_aucun_symbole_vide(self):
        for rec in self.data["symbols"]:
            self.assertTrue(rec["symbol"].strip(),
                            "symbole vide dans l'echantillon")
            self.assertTrue(rec["repo"].strip(),
                            "depot vide dans l'echantillon")

    def test_vingt_symboles_par_depot_et_cinq_depots(self):
        par_depot = {}
        for rec in self.data["symbols"]:
            par_depot.setdefault(rec["repo"], []).append(rec["symbol"])
        self.assertEqual(len(par_depot), 5)
        for depot, symbols in par_depot.items():
            self.assertEqual(len(symbols), 20, depot)
            self.assertEqual(len(set(symbols)), 20, depot)

    def test_les_etats_sont_exclusifs_et_complets(self):
        for rec in self.data["symbols"]:
            self.assertIn(rec["etat"], (RESOLU, AILLEURS, NON_RESOLU), rec["symbol"])
        compte = {}
        for rec in self.data["symbols"]:
            compte[rec["etat"]] = compte.get(rec["etat"], 0) + 1
        self.assertEqual(sum(compte.values()), 100)
        publie = self.data["principal"]["counts"]
        self.assertEqual(compte.get(RESOLU, 0), publie[RESOLU])
        self.assertEqual(compte.get(AILLEURS, 0), publie[AILLEURS])
        self.assertEqual(compte.get(NON_RESOLU, 0), publie[NON_RESOLU])

    def test_chaque_symbole_resolu_a_une_page_et_une_citation(self):
        for rec in self.data["symbols"]:
            if rec["etat"] != RESOLU:
                continue
            self.assertTrue(rec["url"].startswith(
                "https://www.qnx.com/developers/docs/8.0/"), rec["symbol"])
            self.assertEqual(len(rec["page_sha256"]), 64, rec["symbol"])
            self.assertEqual(len(rec["citation_sha256"]), 64, rec["symbol"])
            self.assertGreater(rec["citation_octets"], 0, rec["symbol"])

    def test_les_symboles_absents_etaient_dans_la_reference_7_1(self):
        for rec in self.data["symbols"]:
            if rec["etat"] == NON_RESOLU:
                self.assertTrue(rec["in_71"],
                                "%s est absent de 8.0 mais etait inconnu en 7.1"
                                % rec["symbol"])

    def test_les_cinq_depots_sont_documents(self):
        self.assertEqual(len(self.data["repos"]), 5)
        for repo in self.data["repos"]:
            self.assertTrue(repo["url"].startswith("https://github.com/"), repo["key"])
            self.assertEqual(len(repo["commit"]), 40, repo["key"])
            self.assertEqual(len(repo["sha256_corpus"]), 64, repo["key"])
            self.assertGreater(repo["files"], 0, repo["key"])
            self.assertEqual(repo["consulte_le"], "2026-11-14", repo["key"])


class TestTauxPublie(unittest.TestCase):
    """Le chiffre publie doit etre celui des donnees publiees."""

    def test_le_taux_du_markdown_vaut_le_taux_calcule(self):
        data = load_data()
        with open(MESURE_MD, encoding="utf-8") as fh:
            text = fh.read()
        m = re.search(r"\*\*Taux J4 = (\d+) % \((\d+) symboles resolus et cites "
                      r"sur (\d+)\)\.\*\*", text)
        self.assertIsNotNone(m, "le taux J4 n'est pas trouve dans docs/mesure-J4.md")
        taux_md, resolus, total = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calcule = mesure.taux(data["symbols"])
        self.assertEqual(taux_md, int(round(calcule)),
                         "le taux du Markdown ne vaut pas le taux calcule "
                         "sur les donnees publiees")
        self.assertEqual(resolus, data["principal"]["counts"][RESOLU])
        self.assertEqual(total, len(data["symbols"]))

    def test_le_taux_publie_franchit_le_seuil_j4(self):
        """Le critere J4 de la fiche : en dessous de 80 %, la piste change."""
        data = load_data()
        taux = mesure.taux(data["symbols"])
        self.assertGreaterEqual(
            taux, SEUIL_J4,
            "taux J4 de %.1f %% : sous le seuil de %.0f %%, la fiche doit changer "
            "de cap (voir section 2.6 et 2.7 de la fiche)" % (taux, SEUIL_J4))

    def test_les_pages_de_citations_contenent_chaque_symbole_resolu(self):
        data = load_data()
        textes = {}
        for name in sorted(os.listdir(MESURE_DIR)):
            if not name.startswith("citations-"):
                continue
            with open(os.path.join(MESURE_DIR, name), encoding="utf-8") as fh:
                textes[name] = fh.read()
        self.assertEqual(len(textes), 5)
        tout = "\n".join(textes.values())
        for rec in data["symbols"]:
            if rec["etat"] != RESOLU:
                continue
            self.assertIn("--- %s ---" % rec["symbol"], tout, rec["symbol"])
            self.assertIn(rec["page_sha256"], tout, rec["symbol"])


@unittest.skipUnless(os.path.isfile(os.path.join(default_corpus_dir(), "MANIFEST.json")),
                     CORPUS_ABSENT_MSG)
class TestMesureReproductible(unittest.TestCase):
    """Rejouer l'outil sur les 100 symboles doit redonner la mesure publiee."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.corpus = Corpus(default_corpus_dir())
        cls.classifier = Classifier(cls.corpus)

    def test_les_statuts_publies_sont_reproduits(self):
        symbols = [r["symbol"] for r in self.data["symbols"]]
        results = self.classifier.classify(symbols)
        par_symbole = {r.symbol: r for r in results}
        for rec in self.data["symbols"]:
            res = par_symbole[rec["symbol"]]
            self.assertEqual(res.status, rec["status"], rec["symbol"])
            self.assertEqual(res.url, rec["url"], rec["symbol"])
            self.assertEqual(res.citation_source, rec["citation_source"],
                             rec["symbol"])

    def test_les_pages_citees_sont_dans_le_corpus_fige(self):
        for rec in self.data["symbols"]:
            if rec["etat"] != RESOLU:
                continue
            page = self.corpus.find_url(rec["url"])
            self.assertIsNotNone(page, rec["symbol"])
            self.assertEqual(page.sha256, rec["page_sha256"], rec["symbol"])

    def test_le_taux_recalcule_vaut_le_taux_publie(self):
        symbols = [r["symbol"] for r in self.data["symbols"]]
        results = self.classifier.classify(symbols)
        records = []
        for res in results:
            page = self.corpus.find_url(res.url) if res.url else None
            records.append({"symbol": res.symbol, "status": res.status,
                            "etat": mesure.etat(res, page is not None)})
        self.assertAlmostEqual(mesure.taux(records),
                               self.data["principal"]["taux"], places=6)


if __name__ == "__main__":
    unittest.main()
