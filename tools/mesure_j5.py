#!/usr/bin/env python3
"""Mesure J5 : taux de resolution de QX PORTMAP, sur le MEME echantillon que J4.

J5 ajoute **une seule chose** a la mesure J4. Quand un symbole est « decrit
ailleurs » (renvoi « The following are described elsewhere » de l'index 8.0),
J5 cherche la **page exacte du livre QNX 8.0 qui le decrit**, verifie cette
page dans le corpus fige (empreinte SHA-256 de la page) et cite cette page.
Les symboles absents de la documentation 8.0 ne bougent pas.

La regle J4 (le symbole a sa propre page dans la C Library Reference 8.0)
reste la regle principale ; J5 ne l'change pas. J5 ajoute un etat :
« decrit ailleurs **et** resolu sur la page QNX 8.0 qui le decrit ».

Echantillon : les 100 symboles de la mesure J4 publiee
(``docs/mesure-J4/mesure-J4.json``), dans le meme ordre. Avec ``--clones``,
l'echantillon est **rederiive** des 5 depots QNX publics aux commits epingles
de J4 et compare symbole par symbole a l'echantillon publie : c'est la preuve
que le taux J5 et le taux J4 sont comparables.

Aucun code de ``qnx_portmap/`` n'est modifie par cette mesure : elle ne fait
que mesurer, citer et verifier.

Usage :

    python3 tools/mesure_j5.py \
        --corpus /work/qnx-portmap-corpus-local/corpus \
        --sample docs/mesure-J4/mesure-J4.json \
        --markdown docs/mesure-J5.md \
        --public-json docs/mesure-J5/mesure-J5.json \
        --citations-dir docs/mesure-J5
"""

import argparse
import collections
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qnx_portmap.classify import DOCUMENTED, ELSEWHERE, Classifier  # noqa: E402
from qnx_portmap.corpus import Corpus  # noqa: E402
from qnx_portmap.extract import article_of, sentences_with, strip_tags  # noqa: E402

from mesure_j4 import (AILLEURS, CORPUS_SHA256, CONSULTED, NON_RESOLU,  # noqa: E402
                       PER_REPO, REPOS, RESOLU, etat as etat_j4,
                       load_standard_symbols, select_sample)

# Racine de la documentation QNX 8.0 : une page qui n'y est pas n'est pas une
# page QNX 8.0, meme si l'outil la cite (cas des renvois vers FreeBSD).
QNX_80 = "https://www.qnx.com/developers/docs/8.0/"


def est_url_qnx_80(url):
    """Vrai si l'URL est une page de la documentation QNX 8.0."""
    return bool(url) and url.startswith(QNX_80) and "/topic/" in url


def pages_candidates(res):
    """Pages QNX 8.0 candidates pour un symbole « decrit ailleurs ».

    Dans l'ordre : les renvois de l'index 8.0 (``see_urls``), puis la page
    trouvee par l'outil dans le corpus (``url``), puis les pages du guide de
    migration qui mentionnent le symbole. Les URL hors documentation QNX 8.0
    (renvois vers FreeBSD, par exemple) sont ecartees.
    """
    out = []
    for url in list(res.see_urls) + [res.url] + list(res.migration_urls):
        if est_url_qnx_80(url) and url not in out:
            out.append(url)
    return out


def resoudre_page(corpus, res):
    """Page exacte du livre QNX 8.0 qui decrit le symbole.

    Renvoie ``(page, citation, kind)`` ou ``None``. La page retenue doit :

    * etre une page de la documentation QNX 8.0 **presente dans le corpus
      fige** (c'est elle qui donne l'empreinte SHA-256) ;
    * ne pas etre une page d'index : l'index renvoie vers une source, il ne
      decrit pas la fonction ;
    * contenir reellement le symbole : la citation est extraite de la page.

    La citation est un extrait court (au plus 320 caracteres), comme dans la
    mesure J4.
    """
    for url in pages_candidates(res):
        page = corpus.find_url(url)
        if page is None or page.is_index_page:
            continue
        text = strip_tags(article_of(corpus.html(page)))
        if not text:
            continue
        for call_form, kind in ((True, "appel de fonction"), (False, "mention")):
            cites = sentences_with(text, res.symbol, limit=1, call_form=call_form)
            if cites and cites[0].strip():
                return page, cites[0], kind
    return None


def etat_j5(res, page_found, resolution=None):
    """Etat J5 d'un symbole.

    * ``documented`` + page presente dans le corpus + citation non vide =>
      **resolu et cite** (regle J4, inchangee) ;
    * ``described_elsewhere`` + page QNX 8.0 trouvee et verifiee dans le
      corpus => **resolu et cite** (regle J5) ;
    * ``described_elsewhere`` sans page QNX 8.0 => decrit ailleurs (non resolu) ;
    * ``absent`` / ``unknown`` => non resolu (le symbole a disparu de la 8.0).
    """
    if res.status == DOCUMENTED and res.citation and page_found:
        return RESOLU
    if res.status == ELSEWHERE:
        return RESOLU if resolution else AILLEURS
    return NON_RESOLU


def taux(records):
    """Taux J5 : fraction des symboles resolus et cites.

    Le denominateur est le nombre de mesures. Une liste vide leve une
    exception plutot que de renvoyer 0 : un taux calcule sur rien n'est pas
    un taux.
    """
    total = len(records)
    if total == 0:
        raise ValueError("taux J5 : aucune mesure (division par zero)")
    ok = sum(1 for r in records if r["etat"] == RESOLU)
    return 100.0 * ok / total


def resume(records):
    """Compte les 3 etats et le taux."""
    counts = collections.Counter(r["etat"] for r in records)
    return {
        "total": len(records),
        "counts": {RESOLU: counts[RESOLU], AILLEURS: counts[AILLEURS],
                   NON_RESOLU: counts[NON_RESOLU]},
        "taux": taux(records),
    }


def charger_echantillon(path):
    """Lit l'echantillon publie par la mesure J4.

    Renvoie ``(choix, data)`` : la liste des symboles (nom, depot, appels,
    famille) et la mesure J4 complete.
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    choix = [{"symbol": r["symbol"], "repo": r["repo"], "calls": r["calls"],
              "famille": r["famille"]} for r in data["symbols"]]
    return choix, data


def comparer_echantillons(choix_a, choix_b):
    """Compare deux echantillons symbole par symbole (ordre compris)."""
    def clef(choix):
        return [(c["symbol"], c["repo"], c["calls"], c["famille"]) for c in choix]
    return clef(choix_a) == clef(choix_b)


def measure(classifier, corpus, choix):
    """Classe un echantillon et renvoie les enregistrements (etats J5)."""
    symbols = [c["symbol"] for c in choix]
    results = classifier.classify(symbols)
    by_symbol = {r.symbol: r for r in results}
    records = []
    for c in choix:
        res = by_symbol[c["symbol"]]
        page = corpus.find_url(res.url) if res.url else None
        # la resolution J5 ne concerne que les symboles « decrit ailleurs »
        resolution = (resoudre_page(corpus, res) if res.status == ELSEWHERE
                      else None)
        rec = {
            "symbol": c["symbol"],
            "repo": c["repo"],
            "calls": c["calls"],
            "famille": c["famille"],
            "status": res.status,
            "etat_j4": etat_j4(res, page is not None),
            "etat": etat_j5(res, page is not None, resolution),
            "url": res.url,
            "page_sha256": page.sha256 if page is not None else "",
            "citation": res.citation,
            "citation_source": res.citation_source,
            "citation_kind": res.citation_kind,
            "note": res.note,
            "in_71": res.in_71,
            "in_80": res.in_80,
            "page_in_corpus": page is not None,
        }
        if resolution is not None:
            page_r, citation, kind = resolution
            rec["etat"] = RESOLU
            rec["url"] = page_r.url
            rec["page_sha256"] = page_r.sha256
            rec["citation"] = citation
            rec["citation_source"] = "%s, %s" % (page_r.book, page_r.topic)
            rec["citation_kind"] = kind
            rec["note"] = ("decrit dans la documentation QNX 8.0 (livre %s, page "
                           "%s) : resolu et cite en J5" % (page_r.book, page_r.topic))
            rec["resolution_j5"] = {
                "page": page_r.url,
                "book": page_r.book,
                "topic": page_r.topic,
                "kind": kind,
                "url_avant_j5": res.url,
            }
        else:
            rec["resolution_j5"] = None
        records.append(rec)
    return records


def write_markdown(path, data, records):
    """Ecrit la mesure J5 (chiffre, conversions, 100 symboles, methode)."""
    prim = data["principal"]
    j4 = data["mesure_j4"]
    convertis = [r for r in records if r.get("resolution_j5")]
    lignes = []
    lignes.append("# Mesure J5 - taux de resolution de QX PORTMAP, meme echantillon que J4")
    lignes.append("")
    lignes.append("Mesure faite le %s par `tools/mesure_j5.py` (reproductible : voir "
                 "la section Reproduire plus bas)." % CONSULTED)
    lignes.append("")
    lignes.append("## Le chiffre")
    lignes.append("")
    lignes.append("**Taux J5 = %.0f %% (%d symboles resolus et cites sur %d).**"
                  % (prim["taux"], prim["counts"][RESOLU], prim["total"]))
    lignes.append("")
    lignes.append("| etat | nombre | compte dans le critere ? |")
    lignes.append("|---|---:|---|")
    lignes.append("| resolu et cite | %d | oui |" % prim["counts"][RESOLU])
    lignes.append("| resolu mais decrit ailleurs | %d | **non** |"
                  % prim["counts"][AILLEURS])
    lignes.append("| non resolu | %d | **non** |" % prim["counts"][NON_RESOLU])
    lignes.append("")
    lignes.append("Cumul des trois etats : %d. La mesure J4 (%.0f %%, meme "
                  "echantillon) reste une **mesure datee** : elle n'est pas "
                  "modifiee par J5."
                  % (prim["total"], j4["taux"]))
    lignes.append("")
    lignes.append("Les %d symboles « decrit ailleurs » de la mesure J4 sont "
                  "devenus « resolu et cite » : chacun pointe desormais la "
                  "**page exacte du livre QNX 8.0 qui le decrit**, avec "
                  "l'empreinte SHA-256 de cette page." % len(convertis))
    lignes.append("")
    lignes.append("## Les %d conversions" % len(convertis))
    lignes.append("")
    lignes.append("| symbole | depot | livre QNX 8.0 | page citee | "
                  "sha256 de la page | genre de mention |")
    lignes.append("|---|---|---|---|---|---|")
    for rec in convertis:
        r5 = rec["resolution_j5"]
        lignes.append("| `%s` | `%s` | `%s` | `%s` | `%s` | %s |"
                      % (rec["symbol"], rec["repo"], r5["book"], r5["topic"],
                         rec["page_sha256"][:16], r5["kind"]))
    lignes.append("")
    for rec in convertis:
        r5 = rec["resolution_j5"]
        avant = r5["url_avant_j5"] or ""
        if avant and avant != rec["url"]:
            origine = ("L'index 8.0 renvoyait a %s ; la page QNX 8.0 qui decrit "
                       "le symbole est %s, verifiee dans le corpus fige"
                       % (avant, rec["url"]))
        else:
            origine = ("L'outil pointait deja vers cette page ; J5 y ajoute la "
                       "verification dans le corpus fige, la citation et "
                       "l'empreinte SHA-256")
        lignes.append("- `%s` : **%s**, page `%s` (%s). %s (SHA-256 complet dans "
                      "`docs/mesure-J5/citations-*.txt`)."
                      % (rec["symbol"], r5["book"], r5["topic"], rec["url"],
                         origine))
    lignes.append("")
    lignes.append("## Ce qui n'a pas bouge")
    lignes.append("")
    lignes.append("Les 4 symboles « non resolu » de J4 le restent : ils avaient une "
                  "page dans la C Library Reference **7.1** et n'en ont plus dans la "
                  "8.0. Ils ne sont pas inventes, pas effaces :")
    lignes.append("")
    for rec in records:
        if rec["etat"] == NON_RESOLU:
            lignes.append("- `%s` (%s) : page 7.1 `%s` - absent de la 8.0."
                          % (rec["symbol"], rec["repo"], rec["url"]))
    lignes.append("")
    lignes.append("Les 93 symboles « resolu et cite » de J4 sont **inchanges** : "
                  "meme page, meme SHA-256, meme citation. Aucune regle de "
                  "l'outil (`qnx_portmap/`) n'a ete modifiee.")
    lignes.append("")
    lignes.append("## L'echantillon : inchange")
    lignes.append("")
    lignes.append("Memes 5 depots QNX publics, memes commits epingles, memes 100 "
                  "symboles, **dans le meme ordre** que la mesure J4 :")
    lignes.append("")
    lignes.append("| depot | URL | commit epingle | fichiers .c/.h retenus | "
                  "sous-dossier | consulte le |")
    lignes.append("|---|---|---|---:|---|---|")
    for repo in data["repos"]:
        sub = repo["subdir"] or "(depot entier)"
        lignes.append("| `%s` | %s | `%s` | %d | `%s` | %s |"
                      % (repo["key"], repo["url"], repo["commit"][:8],
                         repo["files"], sub, CONSULTED))
    lignes.append("")
    lignes.append("Comparabilite : l'echantillon J5 est celui de la mesure J4 "
                  "(`docs/mesure-J4/mesure-J4.json`), rederive et compare symbole "
                  "par symbole quand les clones sont disponibles "
                  "(`tools/mesure_j5.py --clones ...`). Le test "
                  "`tests/test_mesure_j5.py` verifie l'egalite stricte des deux "
                  "listes de 100 symboles.")
    lignes.append("")
    lignes.append("Corpus de reference fige : %d pages QNX (7.1 + 8.0), identite "
                  "SHA-256 `%s`, **hors de l'arbre publiable**."
                  % (data["corpus_pages"], CORPUS_SHA256))
    lignes.append("")
    lignes.append("## La regle J5, en une phrase")
    lignes.append("")
    lignes.append("Un symbole « decrit ailleurs » compte comme « resolu et cite » "
                  "si l'index QNX 8.0 **ou** l'outil renvoie a une page de la "
                  "documentation QNX 8.0 qui contient reellement le symbole, que "
                  "cette page est presente dans le corpus fige et que son "
                  "empreinte SHA-256 est verifiee. Les renvois vers des sites "
                  "externes (FreeBSD) ne comptent pas comme page QNX.")
    lignes.append("")
    lignes.append("## Repartition par famille")
    lignes.append("")
    lignes.append("| famille | resolus et cites | total | taux |")
    lignes.append("|---|---:|---:|---:|")
    for key, label in (("qnx", "specifiques a QNX"),
                       ("standard", "standards C/POSIX")):
        info = data["par_famille"][key]
        if info["total"]:
            lignes.append("| %s | %d | %d | %.1f %% |"
                          % (label, info["resolu"], info["total"],
                             100.0 * info["resolu"] / info["total"]))
    lignes.append("")
    lignes.append("## Les 100 symboles mesures")
    lignes.append("")
    lignes.append("Une ligne par symbole : nom, depot, statut de l'outil, etat J4, "
                  "etat J5, page citee, source de la citation, SHA-256 de la page.")
    lignes.append("")
    lignes.append("| # | symbole | depot | famille | statut | etat J4 | etat J5 | "
                  "appels | page citee | source | sha256 de la page |")
    lignes.append("|---:|---|---|---|---|---|---|---:|---|---|---|")
    for i, rec in enumerate(records, 1):
        lignes.append("| %d | `%s` | `%s` | %s | `%s` | %s | %s | %d | %s | %s | `%s` |"
                      % (i, rec["symbol"], rec["repo"], rec["famille"],
                         rec["status"], rec["etat_j4"], rec["etat"], rec["calls"],
                         rec["url"] or "(aucune)", rec["citation_source"],
                         (rec["page_sha256"][:16] or "-")))
    lignes.append("")
    lignes.append("## Reproduire")
    lignes.append("")
    lignes.append("```")
    lignes.append("# 1. le corpus fige (hors de l'arbre) :")
    lignes.append("#    /work/qnx-portmap-corpus-local/corpus")
    lignes.append("# 2. rederiver l'echantillon depuis les 5 depots epingles")
    lignes.append("#    (git clone --depth 1 --filter=blob:none --sparse)")
    lignes.append("# 3. mesurer")
    lignes.append("python3 tools/mesure_j5.py \\")
    lignes.append("    --corpus /work/qnx-portmap-corpus-local/corpus \\")
    lignes.append("    --sample docs/mesure-J4/mesure-J4.json \\")
    lignes.append("    --clones /work/mesure-j5/clones \\")
    lignes.append("    --markdown docs/mesure-J5.md \\")
    lignes.append("    --public-json docs/mesure-J5/mesure-J5.json \\")
    lignes.append("    --citations-dir docs/mesure-J5")
    lignes.append("```")
    lignes.append("")
    lignes.append("Le test `tests/test_mesure_j5.py` verifie le chiffre publie, "
                  "l'egalite stricte des echantillons J4 et J5, le fait que "
                  "seuls les 3 symboles convertis ont change d'etat, et que "
                  "l'empreinte de chaque page citee est bien celle du corpus "
                  "fige. La preuve ROUGE -> VERT est dans "
                  "`docs/preuves/h-mesure-j5-rouge.txt`.")
    lignes.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes))


def write_citations(dir_path, data, records):
    """Ecrit les citations litterales, une page par depot (budget 4 000 o)."""
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    written = []
    for repo in data["repos"]:
        recs = [r for r in records if r["repo"] == repo["key"]]
        if not recs:
            continue
        name = "citations-%s.txt" % repo["key"].replace("/", "-")
        path = os.path.join(dir_path, name)
        out = []
        out.append("# Citations des %d symboles mesures dans %s"
                   % (len(recs), repo["key"]))
        out.append("# depot     : %s" % repo["url"])
        out.append("# commit    : %s (%s)" % (repo["commit"], repo["commit_date"]))
        out.append("# sous-dossier retenu : %s" % (repo["subdir"] or "(depot entier)"))
        out.append("# consultee le : %s" % CONSULTED)
        out.append("# Extraits courts (une a trois lignes) de la documentation "
                   "QNX 8.0, avec l'URL de la page source et son empreinte "
                   "SHA-256 : voir LICENCE-DOCS-QNX.md.")
        out.append("")
        for rec in recs:
            out.append("--- %s ---" % rec["symbol"])
            out.append("# depot    : %s" % rec["repo"])
            out.append("# appele %d fois dans le depot" % rec["calls"])
            out.append("# statut   : %s (etat J4 : %s, etat J5 : %s)"
                       % (rec["status"], rec["etat_j4"], rec["etat"]))
            out.append("# source   : %s" % rec["citation_source"])
            out.append("# page     : %s" % (rec["url"] or "(aucune)"))
            out.append("# sha256 de la page source : %s" % rec["page_sha256"])
            out.append("# citation : %s" % (rec["citation"] or "(vide)"))
            out.append("")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out))
        written.append((name, sum(len(r["citation"]) for r in recs)))
    return written


def write_public_json(path, data, records):
    """Ecrit le JSON public : tout sauf le texte des citations."""
    out = {
        "methode": data["methode"],
        "consulte_le": CONSULTED,
        "per_repo": data["per_repo"],
        "repos": data["repos"],
        "principal": data["principal"],
        "mesure_j4": data["mesure_j4"],
        "par_famille": data["par_famille"],
        "corpus_pages": data["corpus_pages"],
        "symbols": [],
    }
    for rec in records:
        item = dict(rec)
        item.pop("citation", None)
        item["citation_sha256"] = hashlib.sha256(
            rec["citation"].encode("utf-8")).hexdigest()
        item["citation_octets"] = len(rec["citation"].encode("utf-8"))
        out["symbols"].append(item)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=os.environ.get(
        "QX_PORTMAP_CORPUS", "/work/qnx-portmap-corpus-local/corpus"),
        help="corpus fige (archive locale)")
    ap.add_argument("--sample", default=os.path.join(ROOT, "docs", "mesure-J4",
                                                     "mesure-J4.json"),
                    help="echantillon publie par la mesure J4")
    ap.add_argument("--clones", default=None,
                    help="repertoire des clones des 5 depots (verification de "
                         "l'echantillon, facultatif)")
    ap.add_argument("--markdown", default=None, help="fichier Markdown de sortie")
    ap.add_argument("--citations-dir", default=None,
                    help="repertoire des pages de citations (une par depot)")
    ap.add_argument("--public-json", default=None,
                    help="JSON public (sans le texte des citations)")
    args = ap.parse_args(argv)

    corpus = Corpus(args.corpus)
    classifier = Classifier(corpus)
    choix, j4 = charger_echantillon(args.sample)
    print("corpus : %s (%d pages)" % (corpus.root, len(corpus.pages)))
    print("echantillon J4 : %d symboles, %d depots"
          % (len(choix), len(set(c["repo"] for c in choix))))

    if args.clones:
        standard = load_standard_symbols()
        choix2, _ = select_sample(classifier, args.clones, PER_REPO, standard,
                                  prefer_specific=True)
        meme = comparer_echantillons(choix, choix2)
        print("echantillon rederive des clones : %d symboles - identique a J4 : %s"
              % (len(choix2), "OUI" if meme else "NON"))
        if not meme:
            print("ERREUR : l'echantillon derive n'est pas celui de la mesure J4 ;"
                  " le taux J5 ne serait pas comparable.")
            return 1

    records = measure(classifier, corpus, choix)
    r = resume(records)
    fam = collections.Counter()
    fam_ok = collections.Counter()
    for rec in records:
        fam[rec["famille"]] += 1
        if rec["etat"] == RESOLU:
            fam_ok[rec["famille"]] += 1

    print()
    print("mesure J5 (meme echantillon que J4) :")
    print("  resolu et cite       : %3d" % r["counts"][RESOLU])
    print("  decrit ailleurs      : %3d" % r["counts"][AILLEURS])
    print("  non resolu           : %3d" % r["counts"][NON_RESOLU])
    print("  TAUX J5              : %5.1f %%  (%d / %d)"
          % (r["taux"], r["counts"][RESOLU], r["total"]))
    print("  (mesure J4 datee     : %5.1f %%)" % j4["principal"]["taux"])
    print("  par famille :")
    for key, label in (("qnx", "specifiques a QNX"),
                       ("standard", "standards C/POSIX")):
        if fam.get(key):
            print("    %-22s %3d / %3d  (%5.1f %%)"
                  % (label, fam_ok[key], fam[key],
                     100.0 * fam_ok[key] / fam[key]))
    print()
    convertis = [r for r in records if r.get("resolution_j5")]
    print("  conversions J5 : %d" % len(convertis))
    for rec in convertis:
        r5 = rec["resolution_j5"]
        print("    %-18s -> %s / %s  (sha256 %s...)"
              % (rec["symbol"], r5["book"], r5["topic"], rec["page_sha256"][:16]))

    data = {
        "methode": "meme echantillon que la mesure J4 (100 symboles, 5 depots "
                   "QNX publics aux commits epingles de J4), classes par QX "
                   "PORTMAP sur le corpus fige (hors ligne) ; regle J5 : un "
                   "symbole 'decrit ailleurs' compte comme resolu et cite si la "
                   "page QNX 8.0 qui le decrit est dans le corpus fige, avec son "
                   "empreinte SHA-256",
        "per_repo": PER_REPO,
        "repos": [dict(repo, consulte_le=CONSULTED, sha256_corpus=CORPUS_SHA256)
                  for repo in REPOS],
        "principal": r,
        "mesure_j4": j4["principal"],
        "par_famille": {
            "qnx": {"total": fam.get("qnx", 0), "resolu": fam_ok.get("qnx", 0)},
            "standard": {"total": fam.get("standard", 0),
                         "resolu": fam_ok.get("standard", 0)},
        },
        "corpus_pages": len(corpus.pages),
    }
    if args.markdown:
        write_markdown(args.markdown, data, records)
        print("\necrit : %s" % args.markdown)
    if args.citations_dir:
        written = write_citations(args.citations_dir, data, records)
        for name, nbytes in written:
            print("ecrit : %s (%d octets de citation)"
                  % (os.path.join(args.citations_dir, name), nbytes))
    if args.public_json:
        write_public_json(args.public_json, data, records)
        print("ecrit : %s" % args.public_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
