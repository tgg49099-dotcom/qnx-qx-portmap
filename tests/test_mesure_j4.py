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
import collections
import json
import os
import re
import tempfile
import unittest

from qnx_portmap.classify import Classifier
from qnx_portmap.corpus import Corpus, default_corpus_dir

from .helpers import CORPUS_ABSENT_MSG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESURE_DIR = os.path.join(ROOT, "docs", "mesure-J4")
MESURE_JSON = os.path.join(MESURE_DIR, "mesure-J4.json")
MESURE_MD = os.path.join(ROOT, "docs", "mesure-J4.md")
MESURE_MD_FR = os.path.join(ROOT, "docs", "mesure-J4-FR.md")
SEUIL_J4 = 80.0

RESOLU = "resolu_et_cite"
AILLEURS = "resolu_mais_decrit_ailleurs"
NON_RESOLU = "non_resolu"

# Une ligne du tableau des 100 symboles du rapport anglais.
ROW_RE = re.compile(
    r"^\| (?P<num>\d+) \| `(?P<symbole>[^`]+)` \| `(?P<depot>[^`]+)` \| "
    r"(?P<famille>\w+) \| `(?P<statut>[^`]+)` \| (?P<etat>[^|]+?) \| "
    r"(?P<appels>\d+) \| (?P<page>[^|]+?) \| (?P<source>[^|]+?) \| "
    r"`(?P<sha>[^`]*)` \|$")


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


def lire(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def nombres_du_rapport(texte):
    """Nombres d'un rapport, hors noms de fichiers (``mesure-J4``, ``J4``...).

    Les deux versions du rapport (anglaise et francaise) doivent contenir
    **exactement les memes nombres** : c'est la regle "les chiffres ne bougent
    pas". Les mentions de nom de fichier (``docs/mesure-J4-FR.md``) sont
    retirees : elles ne sont pas des chiffres de la mesure.
    """
    texte = re.sub(r"[A-Za-z0-9_./-]*mesure[-_]J[45][A-Za-z0-9_./-]*", "X", texte)
    texte = re.sub(r"\bJ[45]\b", "X", texte)
    return collections.Counter(re.findall(r"\d+(?:[.,]\d+)?", texte))


def pages_de_citations():
    """Les pages de citations, en anglais et en francais.

    Les pages publiees sont anglaises (``citations-<depot>.txt``) ; l'original
    francais est conserve byte-identique (``citations-<depot>-FR.txt``).
    """
    en, fr = {}, {}
    for name in sorted(os.listdir(MESURE_DIR)):
        if not name.startswith("citations-"):
            continue
        texte = lire(os.path.join(MESURE_DIR, name))
        if name.endswith("-FR.txt"):
            fr[name[:-len("-FR.txt")] + ".txt"] = texte
        else:
            en[name] = texte
    return en, fr


def lignes_de_citation(texte):
    """Le texte des citations (les lignes ``# citation ...``), sans etiqueta."""
    out = []
    for ligne in texte.splitlines():
        if ligne.startswith("# citation"):
            out.append(ligne.split(":", 1)[1].strip())
    return out


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
        """Le chiffre publie doit etre celui des donnees publiees.

        Le test verifie les **deux** versions du rapport : l'anglaise (le
        fichier public) et la francaise (conservee byte-identique).
        """
        data = load_data()
        calcule = mesure.taux(data["symbols"])
        for chemin, motif, nom in (
                (MESURE_MD,
                 r"\*\*J4 rate = (\d+) % \((\d+) symbols resolved and cited "
                 r"out of (\d+)\)\.\*\*",
                 "docs/mesure-J4.md"),
                (MESURE_MD_FR,
                 r"\*\*Taux J4 = (\d+) % \((\d+) symboles resolus et cites "
                 r"sur (\d+)\)\.\*\*",
                 "docs/mesure-J4-FR.md")):
            text = lire(chemin)
            m = re.search(motif, text)
            self.assertIsNotNone(m, "le taux J4 n'est pas trouve dans %s" % nom)
            taux_md, resolus, total = (int(m.group(1)), int(m.group(2)),
                                       int(m.group(3)))
            self.assertEqual(taux_md, int(round(calcule)),
                             "le taux du Markdown (%s) ne vaut pas le taux "
                             "calcule sur les donnees publiees" % nom)
            self.assertEqual(resolus, data["principal"]["counts"][RESOLU], nom)
            self.assertEqual(total, len(data["symbols"]), nom)

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
        en, fr = pages_de_citations()
        self.assertEqual(len(en), 5)
        self.assertEqual(len(fr), 5)
        tout = "\n".join(en.values())
        for rec in data["symbols"]:
            if rec["etat"] != RESOLU:
                continue
            self.assertIn("--- %s ---" % rec["symbol"], tout, rec["symbol"])
            self.assertIn(rec["page_sha256"], tout, rec["symbol"])

    def test_les_pages_de_citations_en_et_fr_ont_les_memes_nombres(self):
        """La traduction des etiquettes ne doit pas bouger un chiffre."""
        en, fr = pages_de_citations()
        for nom in sorted(en):
            self.assertEqual(nombres_du_rapport(en[nom]),
                             nombres_du_rapport(fr[nom]),
                             "les nombres de la page %s ont change" % nom)

    def test_le_texte_des_citations_est_identique_en_anglais_et_en_francais(self):
        """Les extraits QNX cites sont byte-identiques dans les deux versions."""
        en, fr = pages_de_citations()
        for nom in sorted(en):
            self.assertEqual(lignes_de_citation(en[nom]),
                             lignes_de_citation(fr[nom]),
                             "le texte des citations de %s a change" % nom)

    def test_les_pages_de_citations_publiees_sont_en_anglais(self):
        """Aucune etiquette francaise ne doit rester dans les pages publiees."""
        interdits = ("# appele ", "# depot ", "# depot     :", "# sous-dossier ",
                     "# consultee le", "# statut   :", "# sha256 de la page ",
                     "(depot entier)", "(aucune)", "(vide)")
        en, fr = pages_de_citations()
        for nom in sorted(en):
            for etiquette in interdits:
                self.assertNotIn(etiquette, en[nom],
                                 "l'etiquette francaise %r reste dans %s"
                                 % (etiquette, nom))


class TestRapportAnglais(unittest.TestCase):
    """Le rapport anglais doit porter exactement les chiffres de l'outil.

    Le rapport public est en anglais (``docs/mesure-J4.md``) ; le rapport
    francais est conserve byte-identique (``docs/mesure-J4-FR.md``). Les
    chiffres, eux, ne doivent pas bouger : ce fichier verifie que

    1. les deux versions contiennent **exactement les memes nombres** ;
    2. chaque nombre du rapport anglais est celui du JSON publie, c'est-a-dire
       de la sortie de l'outil ;
    3. chaque note de loutil a bien une traduction anglaise (une note
       nouvelle, venue du moteur gele, doit etre traduite avant publication).
    """

    def setUp(self):
        self.data = load_data()
        self.en = lire(MESURE_MD)
        self.fr = lire(MESURE_MD_FR)

    def test_les_deux_versions_ont_exactement_les_memes_nombres(self):
        self.assertEqual(nombres_du_rapport(self.en),
                         nombres_du_rapport(self.fr),
                         "les chiffres du rapport anglais ne sont pas ceux du "
                         "rapport francais")

    def test_le_chiffre_anglais_est_celui_du_json_publie(self):
        m = re.search(r"\*\*J4 rate = (\d+) % \((\d+) symbols resolved and "
                      r"cited out of (\d+)\)\.\*\*", self.en)
        self.assertIsNotNone(m, "le taux J4 n'est pas trouve dans le rapport "
                                "anglais")
        taux_md, resolus, total = (int(m.group(1)), int(m.group(2)),
                                   int(m.group(3)))
        calcule = mesure.taux(self.data["symbols"])
        self.assertEqual(taux_md, int(round(calcule)))
        self.assertEqual(resolus, self.data["principal"]["counts"][RESOLU])
        self.assertEqual(total, self.data["principal"]["total"])

    def test_le_tableau_des_etats_anglais_est_celui_du_json_publie(self):
        counts = self.data["principal"]["counts"]
        for label, cle in (("resolved and cited", RESOLU),
                           ("resolved but described elsewhere", AILLEURS),
                           ("not resolved", NON_RESOLU)):
            m = re.search(r"\| %s \| (\d+) \|" % re.escape(label), self.en)
            self.assertIsNotNone(m, "ligne %s absente du rapport anglais"
                                % label)
            self.assertEqual(int(m.group(1)), counts[cle], label)

    def test_le_tableau_des_familles_anglais_est_celui_du_json_publie(self):
        for cle, label in (("qnx", "QNX-specific"),
                           ("standard", "standard C/POSIX")):
            info = self.data["par_famille"][cle]
            m = re.search(r"\| %s \| (\d+) \| (\d+) \| ([\d.]+) %% \|"
                          % re.escape(label), self.en)
            self.assertIsNotNone(m, "famille %s absente du rapport anglais"
                                % label)
            self.assertEqual(int(m.group(1)), info["resolu"], label)
            self.assertEqual(int(m.group(2)), info["total"], label)
            self.assertAlmostEqual(float(m.group(3)),
                                   100.0 * info["resolu"] / info["total"],
                                   places=1, msg=label)

    def test_les_100_lignes_du_rapport_anglais_sont_celles_du_json(self):
        lignes = {}
        for line in self.en.splitlines():
            m = ROW_RE.match(line)
            if m:
                lignes[int(m.group("num"))] = m
        self.assertEqual(len(lignes), 100,
                         "le rapport anglais ne liste pas les 100 symboles")
        for i, rec in enumerate(self.data["symbols"], 1):
            m = lignes.get(i)
            self.assertIsNotNone(m, "symbole %d absent du rapport anglais" % i)
            self.assertEqual(m.group("symbole"), rec["symbol"])
            self.assertEqual(m.group("depot"), rec["repo"])
            self.assertEqual(m.group("famille"), rec["famille"])
            self.assertEqual(m.group("statut"), rec["status"])
            self.assertEqual(m.group("etat").strip(),
                             mesure.ETAT_EN[rec["etat"]], rec["symbol"])
            self.assertEqual(int(m.group("appels")), rec["calls"], rec["symbol"])
            self.assertEqual(m.group("page").strip(),
                             rec["url"] or "(none)", rec["symbol"])
            self.assertEqual(m.group("source").strip(),
                             rec["citation_source"], rec["symbol"])
            self.assertEqual(m.group("sha"),
                             rec["page_sha256"][:16] or "-", rec["symbol"])

    def test_la_liste_des_symboles_non_resolus_anglais_est_complete(self):
        non_resolus = [r["symbol"] for r in self.data["symbols"]
                       if r["etat"] != RESOLU]
        self.assertTrue(non_resolus)
        section = self.en.split("## What is not resolved, and why", 1)[1]
        section = section.split("## Reproduce", 1)[0]
        for symbole in non_resolus:
            self.assertIn("`%s`" % symbole, section,
                          "%s n'est pas dans la liste des symboles non "
                          "resolus" % symbole)

    def test_chaque_note_de_l_outil_est_traduite_en_anglais(self):
        notes = set()
        for rec in self.data["symbols"]:
            if rec.get("note"):
                notes.add(rec["note"])
        self.assertTrue(notes, "aucune note dans le JSON publie")
        for note in sorted(notes):
            self.assertIn(note, mesure.NOTE_EN,
                          "note de l'outil sans traduction anglaise : %r" % note)

    def test_le_rapport_anglais_est_celui_produit_par_l_outil(self):
        """Le rapport publie est celui que l'outil ecrit, octet pour octet.

        Le JSON publie est la sortie de l'outil. Le seul chiffre qui n'y est
        pas est celui du **contre-echantillon** (l'echantillon large) : il
        est pris dans le rapport francais, qui est lui-meme la sortie de
        l'outil (`--lang fr`). Le rapport anglais est alors recompose a
        partir de ces donnees et compare octet par octet.
        """
        m = re.search(r"donne \*\*(\d+) % \((\d+) / (\d+)\)\*\*", self.fr)
        self.assertIsNotNone(m, "le contre-echantillon n'est pas dans le "
                                "rapport francais")
        taux, resolus, total = int(m.group(1)), int(m.group(2)), int(m.group(3))
        data = dict(self.data)
        data["secondaire_large"] = {"total": total, "taux": float(taux),
                                    "counts": {RESOLU: resolus}}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = os.path.join(tmp, "mesure-J4.md")
            mesure.write_markdown_en(chemin, data, data["symbols"])
            with open(chemin, "rb") as fh:
                regenere = fh.read()
        with open(MESURE_MD, "rb") as fh:
            publie = fh.read()
        self.assertEqual(regenere, publie,
                         "le rapport anglais publie n'est pas celui que "
                         "l'outil produit a partir des donnees publiees")


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
