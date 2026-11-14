"""La mesure J5 doit etre vraie, pas seulement ecrite.

J5 porte le taux de resolution de QX PORTMAP de 93/100 a 96/100 **sur le meme
echantillon** que J4 : les 3 symboles « decrit ailleurs » deviennent « resolu
et cite », chacun avec la **page exacte du livre QNX 8.0 qui le decrit** et
l'empreinte SHA-256 de cette page. Les 4 symboles absents de la 8.0 ne
bougent pas.

Un taux se peut etre maquiller de trois manieres :

* en changeant l'echantillon (le taux J5 ne serait plus comparable a J4) ;
* en comptant comme « resolu » des symboles qui ne le sont pas (une page
  externe, une page d'index, une page absente du corpus ne comptent pas) ;
* en declarant « resolu » un symbole sans citation verifiable.

Les tests de ce fichier ferment ces trois portes :

1. **Meme echantillon** : la liste des 100 symboles de J5 est strictement
   egale a celle de J4 (memes symboles, memes depots, meme ordre) ;
2. **Meme resultat** : le taux calcule par le script est identique au taux
   compte a la main sur dix symboles donnes dans le test ;
3. **Conversions reelles** : les 3 symboles convertis ont une page de la
   documentation QNX 8.0, presente dans le corpus fige, dont l'empreinte
   SHA-256 est verifiee, et une citation extraite de cette page ;
4. **Rien d'autre ne bouge** : les 97 autres symboles ont le meme etat qu'en
   J4, et le statut de l'outil lui-meme est inchange (aucune fonction de
   ``qnx_portmap/`` n'a ete ajoutee ni modifiee).

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
from qnx_portmap.extract import article_of, sentences_with, strip_tags

from .helpers import CORPUS_ABSENT_MSG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESURE_DIR = os.path.join(ROOT, "docs", "mesure-J5")
MESURE_JSON = os.path.join(MESURE_DIR, "mesure-J5.json")
MESURE_MD = os.path.join(ROOT, "docs", "mesure-J5.md")
J4_JSON = os.path.join(ROOT, "docs", "mesure-J4", "mesure-J4.json")
QNX_80 = "https://www.qnx.com/developers/docs/8.0/"

RESOLU = "resolu_et_cite"
AILLEURS = "resolu_mais_decrit_ailleurs"
NON_RESOLU = "non_resolu"

# Les 3 symboles « decrit ailleurs » de la mesure J4, et les 4 « non resolu ».
CONVERTIS = ("InterruptAttach", "if_freenameindex", "setsockopt")
ABSENTS = ("ND_NODE_CMP", "pthread_sleepon_lock", "pthread_sleepon_unlock",
           "fcfgopen")
TAUX_J5 = 96.0

# Les dix symboles du controle a la main. Chacun a ete relu dans la
# documentation QNX 8.0 (voir docs/mesure-J5.md et les pages de citations
# docs/mesure-J5/citations-*.txt) : neuf sont resolus et cites - dont les
# trois converts en J5 - et un a disparu de la reference 8.0. Le taux compte
# a la main est donc 9 / 10 = 90 % (il etait de 70 % en J4).
MAIN_DIX = [
    ("GETIOVLEN", RESOLU),
    ("resmgr_attach", RESOLU),
    ("iofunc_open", RESOLU),
    ("ThreadCtl", RESOLU),
    ("devctl", RESOLU),
    ("slogf", RESOLU),
    ("ConnectAttach", RESOLU),
    ("InterruptAttach", RESOLU),
    ("setsockopt", RESOLU),
    ("fcfgopen", NON_RESOLU),
]
TAUX_MAIN = 90.0


def load_mesure_module():
    """Charge ``tools/mesure_j5.py`` (le dossier tools/ n'est pas un paquet)."""
    path = os.path.join(ROOT, "tools", "mesure_j5.py")
    spec = importlib.util.spec_from_file_location("mesure_j5", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mesure = load_mesure_module()


def load_data():
    with open(MESURE_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def load_j4():
    with open(J4_JSON, encoding="utf-8") as fh:
        return json.load(fh)


class TestEchantillonJ5(unittest.TestCase):
    """J5 doit mesurer le meme echantillon que J4, sinon le taux ment."""

    def setUp(self):
        self.data = load_data()
        self.j4 = load_j4()

    def test_echantillon_identique_a_j4(self):
        """Memes 100 symboles, meme ordre, meme depot, meme nombre d'appels."""
        j5 = [(r["symbol"], r["repo"], r["calls"], r["famille"])
              for r in self.data["symbols"]]
        j4 = [(r["symbol"], r["repo"], r["calls"], r["famille"])
              for r in self.j4["symbols"]]
        self.assertEqual(len(j5), 100)
        self.assertEqual(j5, j4,
                         "l'echantillon J5 n'est pas celui de la mesure J4 : "
                         "les taux ne sont pas comparables")

    def test_cent_symbols_et_vingt_par_depot(self):
        symbols = [r["symbol"] for r in self.data["symbols"]]
        self.assertEqual(len(symbols), 100)
        self.assertEqual(len(set(symbols)), 100, "doublon dans l'echantillon")
        par_depot = {}
        for rec in self.data["symbols"]:
            par_depot.setdefault(rec["repo"], []).append(rec["symbol"])
        self.assertEqual(len(par_depot), 5)
        for depot, symbols in par_depot.items():
            self.assertEqual(len(symbols), 20, depot)

    def test_les_etats_sont_exclusifs_et_complets(self):
        compte = {}
        for rec in self.data["symbols"]:
            self.assertIn(rec["etat"], (RESOLU, AILLEURS, NON_RESOLU), rec["symbol"])
            compte[rec["etat"]] = compte.get(rec["etat"], 0) + 1
        self.assertEqual(sum(compte.values()), 100)
        publie = self.data["principal"]["counts"]
        self.assertEqual(compte.get(RESOLU, 0), publie[RESOLU])
        self.assertEqual(compte.get(AILLEURS, 0), publie[AILLEURS])
        self.assertEqual(compte.get(NON_RESOLU, 0), publie[NON_RESOLU])

    def test_le_taux_publie_est_96_pour_cent(self):
        """Le but de la tranche J5 : 96 symboles resolus et cites sur 100."""
        self.assertEqual(compte_resolu(self.data), 96)
        self.assertAlmostEqual(mesure.taux(self.data["symbols"]), TAUX_J5,
                               places=6,
                               msg="le taux J5 publie n'est pas 96 %% "
                                   "(%.1f %%)" % mesure.taux(self.data["symbols"]))
        self.assertAlmostEqual(self.data["principal"]["taux"], TAUX_J5, places=6)

    def test_plus_aucun_symbole_decrit_ailleurs(self):
        for rec in self.data["symbols"]:
            self.assertNotEqual(rec["etat"], AILLEURS,
                                "%s est encore 'decrit ailleurs'" % rec["symbol"])

    def test_seul_les_trois_symboles_convertis_ont_change_d_etat(self):
        """Les 97 autres symboles ont exactement l'etat qu'ils avaient en J4."""
        par_symbole = {r["symbol"]: r for r in self.data["symbols"]}
        j4 = {r["symbol"]: r for r in self.j4["symbols"]}
        changes = []
        for symbole, rec in par_symbole.items():
            etat_j4 = j4[symbole]["etat"]
            self.assertEqual(rec["etat_j4"], etat_j4,
                             "l'etat J4 recopie est faux pour %s" % symbole)
            if rec["etat"] != etat_j4:
                changes.append(symbole)
                self.assertEqual(etat_j4, AILLEURS, symbole)
                self.assertEqual(rec["etat"], RESOLU, symbole)
        self.assertEqual(sorted(changes), sorted(CONVERTIS),
                         "les seuls symboles qui peuvent changer d'etat en J5 "
                         "sont %s" % (CONVERTIS,))

    def test_les_quatre_absents_restent_absents(self):
        par_symbole = {r["symbol"]: r for r in self.data["symbols"]}
        for symbole in ABSENTS:
            self.assertIn(symbole, par_symbole, symbole)
            rec = par_symbole[symbole]
            self.assertEqual(rec["etat"], NON_RESOLU,
                             "%s a disparu de la 8.0 : il doit rester absent" % symbole)
            self.assertTrue(rec["in_71"],
                            "%s etait inconnu en 7.1 : il ne peut pas etre absent"
                            % symbole)
            self.assertIn("/7.1/", rec["url"], symbole)

    def test_les_trois_convertis_ont_une_page_qnx_8_0_et_son_sha256(self):
        par_symbole = {r["symbol"]: r for r in self.data["symbols"]}
        for symbole in CONVERTIS:
            rec = par_symbole[symbole]
            self.assertEqual(rec["etat"], RESOLU, symbole)
            self.assertTrue(rec["url"].startswith(QNX_80),
                            "%s : page hors documentation QNX 8.0 (%s)"
                            % (symbole, rec["url"]))
            self.assertIn("/topic/", rec["url"], symbole)
            self.assertEqual(len(rec["page_sha256"]), 64, symbole)
            self.assertRegex(rec["page_sha256"], r"^[0-9a-f]{64}$", symbole)
            self.assertEqual(len(rec["citation_sha256"]), 64, symbole)
            self.assertGreater(rec["citation_octets"], 0, symbole)
            self.assertIsNotNone(rec["resolution_j5"], symbole)
            self.assertTrue(rec["resolution_j5"]["book"], symbole)
            self.assertTrue(rec["resolution_j5"]["topic"], symbole)
            self.assertTrue(rec["citation_source"].startswith(rec["resolution_j5"]["book"]),
                            symbole)

    def test_les_pages_des_trois_convertis_sont_des_livres_qnx(self):
        """Chaque conversion cite un livre QNX 8.0, pas un index ni FreeBSD."""
        par_symbole = {r["symbol"]: r for r in self.data["symbols"]}
        for symbole in CONVERTIS:
            rec = par_symbole[symbole]
            self.assertIsNotNone(rec["resolution_j5"],
                                 "%s : aucune resolution J5" % symbole)
            livre = rec["resolution_j5"]["book"]
            self.assertTrue(livre.startswith("com.qnx.doc."), symbole)
            self.assertNotIn("man.freebsd.org", rec["url"], symbole)
            self.assertTrue(rec["citation_source"].startswith(livre), symbole)
            self.assertIn(rec["resolution_j5"]["topic"], rec["citation_source"],
                          symbole)

    def test_le_taux_du_markdown_vaut_le_taux_calcule(self):
        with open(MESURE_MD, encoding="utf-8") as fh:
            text = fh.read()
        m = re.search(r"\*\*Taux J5 = (\d+) % \((\d+) symboles resolus et cites "
                      r"sur (\d+)\)\.\*\*", text)
        self.assertIsNotNone(m, "le taux J5 n'est pas trouve dans docs/mesure-J5.md")
        taux_md, resolus, total = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calcule = mesure.taux(self.data["symbols"])
        self.assertEqual(taux_md, int(round(calcule)),
                         "le taux du Markdown ne vaut pas le taux calcule sur les "
                         "donnees publiees")
        self.assertEqual(resolus, self.data["principal"]["counts"][RESOLU])
        self.assertEqual(total, len(self.data["symbols"]))
        self.assertEqual(total, 100)

    def test_les_pages_de_citations_contiennent_chaque_symbole_resolu(self):
        textes = {}
        for name in sorted(os.listdir(MESURE_DIR)):
            if not name.startswith("citations-"):
                continue
            with open(os.path.join(MESURE_DIR, name), encoding="utf-8") as fh:
                textes[name] = fh.read()
        self.assertEqual(len(textes), 5)
        tout = "\n".join(textes.values())
        for rec in self.data["symbols"]:
            if rec["etat"] != RESOLU:
                continue
            self.assertIn("--- %s ---" % rec["symbol"], tout, rec["symbol"])
            self.assertIn(rec["page_sha256"], tout, rec["symbol"])

    def test_un_taux_sur_zero_leve_une_erreur(self):
        with self.assertRaises(ValueError):
            mesure.taux([])


def compte_resolu(data):
    """Nombre de symboles « resolu et cite » dans une mesure publiee."""
    return sum(1 for r in data["symbols"] if r["etat"] == RESOLU)


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
        calcule = mesure.taux(records)
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


@unittest.skipUnless(os.path.isfile(os.path.join(default_corpus_dir(), "MANIFEST.json")),
                     CORPUS_ABSENT_MSG)
class TestMesureReproductible(unittest.TestCase):
    """Rejouer la mesure J5 sur le corpus fige doit redonner le chiffre publie."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.j4 = load_j4()
        cls.corpus = Corpus(default_corpus_dir())
        cls.classifier = Classifier(cls.corpus)

    def _choix(self):
        return [{"symbol": r["symbol"], "repo": r["repo"], "calls": r["calls"],
                 "famille": r["famille"]} for r in self.j4["symbols"]]

    def test_le_taux_recalcule_vaut_le_taux_publie(self):
        records = mesure.measure(self.classifier, self.corpus, self._choix())
        self.assertAlmostEqual(mesure.taux(records),
                               self.data["principal"]["taux"], places=6)
        self.assertEqual(mesure.taux(records), TAUX_J5)

    def test_les_statuts_de_l_outil_sont_inchanges(self):
        """J5 ne touche pas l'outil : les statuts sont ceux de J4."""
        symbols = [r["symbol"] for r in self.j4["symbols"]]
        results = {r.symbol: r for r in self.classifier.classify(symbols)}
        j4 = {r["symbol"]: r for r in self.j4["symbols"]}
        for symbole, rec in results.items():
            self.assertEqual(rec.status, j4[symbole]["status"], symbole)
            self.assertEqual(rec.url, j4[symbole]["url"], symbole)

    def test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256(self):
        par_symbole = {r["symbol"]: r for r in self.data["symbols"]}
        for symbole in CONVERTIS:
            rec = par_symbole[symbole]
            page = self.corpus.find_url(rec["url"])
            self.assertIsNotNone(page,
                                 "%s : page absente du corpus fige (%s)"
                                 % (symbole, rec["url"]))
            self.assertEqual(page.sha256, rec["page_sha256"], symbole)
            self.assertEqual(page.version, "8.0", symbole)
            self.assertFalse(page.is_index_page,
                             "%s : une page d'index ne decrit pas la fonction"
                             % symbole)

    def test_la_citation_vient_de_la_page_citee(self):
        """La citation publiee est bien un extrait de la page citee."""
        import hashlib
        par_symbole = {r["symbol"]: r for r in self.data["symbols"]}
        for symbole in CONVERTIS:
            rec = par_symbole[symbole]
            page = self.corpus.find_url(rec["url"])
            self.assertIsNotNone(page, symbole)
            text = strip_tags(article_of(self.corpus.html(page)))
            cites = sentences_with(text, symbole, limit=1, call_form=True)
            if not cites:
                cites = sentences_with(text, symbole, limit=1, call_form=False)
            self.assertTrue(cites, symbole)
            self.assertNotIn("man.freebsd.org", cites[0],
                             "%s : la citation renvoie a FreeBSD, pas a un "
                             "livre QNX 8.0" % symbole)
            empreinte = hashlib.sha256(cites[0].encode("utf-8")).hexdigest()
            self.assertEqual(empreinte, rec["citation_sha256"],
                             "%s : la citation publiee n'est pas celle de la page "
                             "citee" % symbole)


if __name__ == "__main__":
    unittest.main()
