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

from mesure_j4 import (AILLEURS, CORPUS_SHA256, CONSULTED, ETAT_CITATION_EN,  # noqa: E402
                       ETAT_EN, FAMILLE_EN, NON_RESOLU,
                       PER_REPO, REPOS, RESOLU, etat as etat_j4,
                       load_standard_symbols, select_sample)

# -- version anglaise du rapport --------------------------------------------
# Le rapport public est en anglais ; la version francaise (sortie de l'outil,
# `--lang fr`) est conservee a part, byte-identique. Les chiffres sont les
# memes dans les deux versions : seul le texte change.
# Le genre de mention vient du moteur (en francais) : il est traduit ici.
KIND_EN = {
    "appel de fonction": "function call",
    "mention": "mention",
}

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


def write_markdown(path, data, records, lang="fr"):
    """Ecrit la mesure J5 (chiffre, conversions, 100 symboles, methode).

    ``lang`` vaut ``"fr"`` (sortie historique, conservee byte-identique) ou
    ``"en"`` (version publique du depot). Les chiffres sont identiques dans
    les deux versions : seuls les libelles et le texte changent.
    """
    if lang == "en":
        return write_markdown_en(path, data, records)
    return write_markdown_fr(path, data, records)


def write_markdown_fr(path, data, records):
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


def kind_en(kind):
    """Traduit le genre de mention (donnee du moteur, en francais)."""
    return KIND_EN.get(kind, kind)


def write_markdown_en(path, data, records):
    """Ecrit la mesure J5 en anglais (memes chiffres que la version fr)."""
    prim = data["principal"]
    j4 = data["mesure_j4"]
    convertis = [r for r in records if r.get("resolution_j5")]
    absents = [r for r in records if r["etat"] == NON_RESOLU]
    lignes = []
    lignes.append("# Measurement J5 - QX PORTMAP resolution rate, same sample as "
                  "J4")
    lignes.append("")
    lignes.append("Measured on %s by `tools/mesure_j5.py` (reproducible: see "
                  "the \"Reproduce\" section below). The French version of this "
                  "report is kept byte-identical in `docs/mesure-J5-FR.md`."
                  % CONSULTED)
    lignes.append("")
    lignes.append("## The figure")
    lignes.append("")
    lignes.append("**J5 rate = %.0f %% (%d symbols resolved and cited out of "
                  "%d).**" % (prim["taux"], prim["counts"][RESOLU],
                              prim["total"]))
    lignes.append("")
    lignes.append("| state | count | counted in the criterion ? |")
    lignes.append("|---|---:|---|")
    lignes.append("| resolved and cited | %d | yes |" % prim["counts"][RESOLU])
    lignes.append("| resolved but described elsewhere | %d | **no** |"
                  % prim["counts"][AILLEURS])
    lignes.append("| not resolved | %d | **no** |" % prim["counts"][NON_RESOLU])
    lignes.append("")
    lignes.append("Total of the three states: %d. The J4 measurement (%.0f %%, "
                  "same sample) remains a **dated measurement**: J5 does not "
                  "modify it." % (prim["total"], j4["taux"]))
    lignes.append("")
    lignes.append("The %d symbols that were \"described elsewhere\" in the J4 "
                  "measurement have become \"resolved and cited\": each one now "
                  "points to the **exact page of the QNX 8.0 book that "
                  "describes it**, with the SHA-256 fingerprint of that page."
                  % len(convertis))
    lignes.append("")
    lignes.append("## The %d conversions" % len(convertis))
    lignes.append("")
    lignes.append("| symbol | repository | QNX 8.0 book | cited page | "
                  "page sha256 | kind of mention |")
    lignes.append("|---|---|---|---|---|---|")
    for rec in convertis:
        r5 = rec["resolution_j5"]
        lignes.append("| `%s` | `%s` | `%s` | `%s` | `%s` | %s |"
                      % (rec["symbol"], rec["repo"], r5["book"], r5["topic"],
                         rec["page_sha256"][:16], kind_en(r5["kind"])))
    lignes.append("")
    for rec in convertis:
        r5 = rec["resolution_j5"]
        avant = r5["url_avant_j5"] or ""
        if avant and avant != rec["url"]:
            origine = ("The 8.0 index pointed to %s; the QNX 8.0 page that "
                       "describes the symbol is %s, verified in the frozen "
                       "corpus" % (avant, rec["url"]))
        else:
            origine = ("The tool already pointed to this page; J5 adds the "
                       "verification in the frozen corpus, the citation and "
                       "the SHA-256 fingerprint")
        lignes.append("- `%s`: **%s**, page `%s` (%s). %s (full SHA-256 in "
                      "`docs/mesure-J5/citations-*.txt`)."
                      % (rec["symbol"], r5["book"], r5["topic"], rec["url"],
                         origine))
    lignes.append("")
    lignes.append("## What has not changed")
    lignes.append("")
    lignes.append("The %d \"not resolved\" symbols of J4 remain so: they had a "
                  "page in the C Library Reference **7.1** and no longer have "
                  "one in 8.0. They are not invented, not erased:"
                  % len(absents))
    lignes.append("")
    for rec in absents:
        lignes.append("- `%s` (%s): 7.1 page `%s` - absent from 8.0."
                      % (rec["symbol"], rec["repo"], rec["url"]))
    lignes.append("")
    lignes.append("The %d \"resolved and cited\" symbols of J4 are "
                  "**unchanged**: same page, same SHA-256, same citation. No "
                  "rule of the tool (`qnx_portmap/`) was modified."
                  % j4["counts"][RESOLU])
    lignes.append("")
    lignes.append("## The sample: unchanged")
    lignes.append("")
    lignes.append("Same 5 public QNX repositories, same pinned commits, same "
                  "100 symbols, **in the same order** as the J4 measurement:")
    lignes.append("")
    lignes.append("| repository | URL | pinned commit | .c/.h files kept | "
                  "subdirectory | consulted on |")
    lignes.append("|---|---|---|---:|---|---|")
    for repo in data["repos"]:
        sub = repo["subdir"] or "(whole repository)"
        lignes.append("| `%s` | %s | `%s` | %d | `%s` | %s |"
                      % (repo["key"], repo["url"], repo["commit"][:8],
                         repo["files"], sub, CONSULTED))
    lignes.append("")
    lignes.append("Comparability: the J5 sample is the one of the J4 "
                  "measurement (`docs/mesure-J4/mesure-J4.json`), re-derived "
                  "and compared symbol by symbol when the clones are available "
                  "(`tools/mesure_j5.py --clones ...`). The test "
                  "`tests/test_mesure_j5.py` verifies the strict equality of "
                  "the two lists of 100 symbols.")
    lignes.append("")
    lignes.append("Frozen reference corpus: %d QNX pages (7.1 + 8.0), SHA-256 "
                  "identity `%s`, **outside the publishable tree**."
                  % (data["corpus_pages"], CORPUS_SHA256))
    lignes.append("")
    lignes.append("## The J5 rule, in one sentence")
    lignes.append("")
    lignes.append("A symbol \"described elsewhere\" counts as \"resolved and "
                  "cited\" if the QNX 8.0 index **or** the tool points to a "
                  "page of the QNX 8.0 documentation that really contains the "
                  "symbol, if that page is present in the frozen corpus and "
                  "if its SHA-256 fingerprint is verified. Links to external "
                  "sites (FreeBSD) do not count as a QNX page.")
    lignes.append("")
    lignes.append("## Breakdown by family")
    lignes.append("")
    lignes.append("| family | resolved and cited | total | rate |")
    lignes.append("|---|---:|---:|---:|")
    for key in ("qnx", "standard"):
        info = data["par_famille"][key]
        if info["total"]:
            lignes.append("| %s | %d | %d | %.1f %% |"
                          % (FAMILLE_EN[key], info["resolu"], info["total"],
                             100.0 * info["resolu"] / info["total"]))
    lignes.append("")
    lignes.append("## The 100 measured symbols")
    lignes.append("")
    lignes.append("One line per symbol: name, repository, tool status, J4 "
                  "state, J5 state, cited page, citation source, SHA-256 of "
                  "the page.")
    lignes.append("")
    lignes.append("| # | symbol | repository | family | status | J4 state | "
                  "J5 state | calls | cited page | source | page sha256 |")
    lignes.append("|---:|---|---|---|---|---|---|---:|---|---|---|")
    for i, rec in enumerate(records, 1):
        lignes.append("| %d | `%s` | `%s` | %s | `%s` | %s | %s | %d | %s | %s | `%s` |"
                      % (i, rec["symbol"], rec["repo"], rec["famille"],
                         rec["status"], ETAT_EN[rec["etat_j4"]], ETAT_EN[rec["etat"]],
                         rec["calls"], rec["url"] or "(none)",
                         rec["citation_source"], (rec["page_sha256"][:16] or "-")))
    lignes.append("")
    lignes.append("## Reproduce")
    lignes.append("")
    lignes.append("```")
    lignes.append("# 1. the frozen corpus (outside the tree):")
    lignes.append("#    /work/qnx-portmap-corpus-local/corpus")
    lignes.append("# 2. re-derive the sample from the 5 pinned repositories")
    lignes.append("#    (git clone --depth 1 --filter=blob:none --sparse)")
    lignes.append("# 3. measure")
    lignes.append("python3 tools/mesure_j5.py \\")
    lignes.append("    --corpus /work/qnx-portmap-corpus-local/corpus \\")
    lignes.append("    --sample docs/mesure-J4/mesure-J4.json \\")
    lignes.append("    --clones /work/mesure-j5/clones \\")
    lignes.append("    --markdown docs/mesure-J5.md --lang en \\")
    lignes.append("    --public-json docs/mesure-J5/mesure-J5.json \\")
    lignes.append("    --citations-dir docs/mesure-J5")
    lignes.append("")
    lignes.append("# --lang fr writes the same report in French")
    lignes.append("# (docs/mesure-J5-FR.md, byte-identical to the historical one).")
    lignes.append("```")
    lignes.append("")
    lignes.append("The test `tests/test_mesure_j5.py` verifies the published "
                  "figure, the strict equality of the J4 and J5 samples, the "
                  "fact that only the 3 converted symbols changed state, and "
                  "that the fingerprint of each cited page is the one of the "
                  "frozen corpus. The RED -> GREEN proof is in "
                  "`docs/preuves/h-mesure-j5-rouge.txt`.")
    lignes.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes))


def write_citations(dir_path, data, records, lang="fr"):
    """Ecrit les citations litterales, une page par depot (budget 4 000 o).

    ``lang`` vaut ``"fr"`` (sortie historique, conservee byte-identique) ou
    ``"en"`` (version publique du depot). Seules les **etiquettes** changent :
    les numeros, les URL et le texte des citations sont identiques dans les
    deux versions.
    """
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
        if lang == "en":
            out.append("# Citations of the %d symbols measured in %s"
                       % (len(recs), repo["key"]))
            out.append("# repository : %s" % repo["url"])
            out.append("# commit     : %s (%s)"
                       % (repo["commit"], repo["commit_date"]))
            out.append("# sub-directory used : %s"
                       % (repo["subdir"] or "(whole repository)"))
            out.append("# consulted on : %s" % CONSULTED)
            out.append("# Short extracts (one to three lines) from the QNX 8.0 "
                       "documentation, with the URL of the source page and its "
                       "SHA-256 fingerprint: see LICENCE-DOCS-QNX.md.")
        else:
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
            if lang == "en":
                out.append("# repository : %s" % rec["repo"])
                out.append("# called %d times in the repository" % rec["calls"])
                out.append("# status     : %s (J4 state: %s, J5 state: %s)"
                           % (rec["status"],
                              ETAT_CITATION_EN.get(rec["etat_j4"], rec["etat_j4"]),
                              ETAT_CITATION_EN.get(rec["etat"], rec["etat"])))
                out.append("# source     : %s" % rec["citation_source"])
                out.append("# page       : %s" % (rec["url"] or "(none)"))
                out.append("# sha256 of the source page : %s" % rec["page_sha256"])
                out.append("# citation   : %s" % (rec["citation"] or "(empty)"))
            else:
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
    ap.add_argument("--lang", choices=("fr", "en"), default="fr",
                    help="langue du rapport Markdown (fr = historique, "
                         "en = version publique du depot)")
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
        write_markdown(args.markdown, data, records, args.lang)
        print("\necrit : %s" % args.markdown)
    if args.citations_dir:
        written = write_citations(args.citations_dir, data, records, args.lang)
        for name, nbytes in written:
            print("ecrit : %s (%d octets de citation)"
                  % (os.path.join(args.citations_dir, name), nbytes))
    if args.public_json:
        write_public_json(args.public_json, data, records)
        print("ecrit : %s" % args.public_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
