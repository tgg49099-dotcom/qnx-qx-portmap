#!/usr/bin/env python3
"""Measurement J5: resolution rate of QX PORTMAP, on the SAME sample as J4.

J5 adds **one single thing** to the J4 measurement. When a symbol is
"described elsewhere" (a "The following are described elsewhere" cross
reference of the 8.0 index), J5 looks for the **exact page of the QNX 8.0
book that describes it**, verifies that page in the frozen corpus (SHA-256
fingerprint of the page) and quotes that page. The symbols missing from the
8.0 documentation do not move.

The J4 rule (the symbol has its own page in the 8.0 C Library Reference)
stays the main rule; J5 does not change it. J5 adds one state:
"described elsewhere **and** resolved on the QNX 8.0 page that describes it".

Sample: the 100 symbols of the published J4 measurement
(``docs/mesure-J4/mesure-J4.json``), in the same order. With ``--clones``,
the sample is **re-derived** from the 5 public QNX repositories at the
commits pinned by J4 and compared symbol by symbol with the published sample:
that is the proof that the J5 rate and the J4 rate are comparable.

No code of ``qnx_portmap/`` is modified by this measurement: it only
measures, quotes and verifies.

Usage:

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
import time

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

# Date of THIS run of the measurement. CONSULTED (from mesure_j4) is the day
# the 5 repositories were consulted (2026-11-14): the sample does not change.
# The J5 report is dated with the day the tool actually measured it, so that
# a re-measurement after a rule change is visible as such.
MESURE_LE = time.strftime("%Y-%m-%d")

# -- English version of the report --------------------------------------------
# The public report is in English; the French version (output of the tool,
# `--lang fr`) is kept apart, byte-identical. The figures are the same in
# both versions: only the text changes.
# The kind of mention comes from the engine (in French): it is translated here.
KIND_EN = {
    "appel de fonction": "function call",
    "mention": "mention",
}

# Root of the QNX 8.0 documentation: a page that is not in it is not a QNX
# 8.0 page, even if the tool quotes it (case of the references to FreeBSD).
QNX_80 = "https://www.qnx.com/developers/docs/8.0/"


def est_url_qnx_80(url):
    """True if the URL is a page of the QNX 8.0 documentation."""
    return bool(url) and url.startswith(QNX_80) and "/topic/" in url


def pages_candidates(res):
    """QNX 8.0 pages candidate for a "described elsewhere" symbol."""
    out = []
    for url in list(res.see_urls) + [res.url] + list(res.migration_urls):
        if est_url_qnx_80(url) and url not in out:
            out.append(url)
    return out


def resoudre_page(corpus, res):
    """Exact page of the QNX 8.0 book that describes the symbol."""
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
    """J5 state of a symbol."""
    if res.status == DOCUMENTED and res.citation and page_found:
        return RESOLU
    if res.status == ELSEWHERE:
        return RESOLU if resolution else AILLEURS
    return NON_RESOLU


def taux(records):
    """J5 rate: fraction of the symbols resolved and cited."""
    total = len(records)
    if total == 0:
        raise ValueError("taux J5 : aucune mesure (division par zero)")
    ok = sum(1 for r in records if r["etat"] == RESOLU)
    return 100.0 * ok / total


def resume(records):
    """Counts the 3 states and the rate."""
    counts = collections.Counter(r["etat"] for r in records)
    return {
        "total": len(records),
        "counts": {RESOLU: counts[RESOLU], AILLEURS: counts[AILLEURS],
                   NON_RESOLU: counts[NON_RESOLU]},
        "taux": taux(records),
    }


def charger_echantillon(path):
    """Reads the sample published by the J4 measurement."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    choix = [{"symbol": r["symbol"], "repo": r["repo"], "calls": r["calls"],
              "famille": r["famille"]} for r in data["symbols"]]
    return choix, data


def comparer_echantillons(choix_a, choix_b):
    """Compares two samples symbol by symbol (order included)."""
    def clef(choix):
        return [(c["symbol"], c["repo"], c["calls"], c["famille"]) for c in choix]
    return clef(choix_a) == clef(choix_b)


def measure(classifier, corpus, choix, etats_publies=None):
    """Classifies a sample and returns the records (J5 states).

    ``etat_j4`` is the state PUBLISHED by the J4 measurement (a dated
    measurement: it is read as published, not re-derived), given by
    ``etats_publies`` ({symbol: state}). Without ``etats_publies`` the J4
    rule is replayed with the tool of the day (fallback for the tests).
    """
    symbols = [c["symbol"] for c in choix]
    results = classifier.classify(symbols)
    by_symbol = {r.symbol: r for r in results}
    records = []
    for c in choix:
        res = by_symbol[c["symbol"]]
        page = corpus.find_url(res.url) if res.url else None
        # the J5 resolution only concerns the "described elsewhere" symbols
        resolution = (resoudre_page(corpus, res) if res.status == ELSEWHERE
                      else None)
        etat_publie = (etats_publies or {}).get(c["symbol"])
        rec = {
            "symbol": c["symbol"],
            "repo": c["repo"],
            "calls": c["calls"],
            "famille": c["famille"],
            "status": res.status,
            "etat_j4": etat_publie or etat_j4(res, page is not None),
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
        if getattr(res, "removed_by_migration_guide", False):
            # published in the JSON too: the report quotes the sentence, so
            # the report must be re-writable from the published JSON alone
            rec["retrait"] = {"phrase": res.citation}
        records.append(rec)
    return records


def write_markdown(path, data, records, lang="fr"):
    """Writes the J5 measurement (figure, conversions, 100 symbols, method)."""
    if lang == "en":
        return write_markdown_en(path, data, records)
    return write_markdown_fr(path, data, records)


def write_markdown_fr(path, data, records):
    """Writes the J5 measurement (figure, conversions, 100 symbols, method)."""
    prim = data["principal"]
    j4 = data["mesure_j4"]
    convertis = [r for r in records if r.get("resolution_j5")]
    deja_absents = [r for r in records
                    if r["etat"] == NON_RESOLU and r["etat_j4"] == NON_RESOLU]
    retires = [r for r in records
               if r["etat"] == NON_RESOLU and r["etat_j4"] != NON_RESOLU]
    lignes = []
    lignes.append("# Mesure J5 - taux de resolution de QX PORTMAP, meme echantillon que J4")
    lignes.append("")
    lignes.append("Mesure faite le %s par `tools/mesure_j5.py` (reproductible : voir "
                 "la section Reproduire plus bas). Depots consultes le %s "
                 "(echantillon inchange)." % (MESURE_LE, CONSULTED))
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
    if retires:
        lignes.append("## Le retrait annonce par le guide officiel")
        lignes.append("")
        lignes.append("%d symbole de l'echantillon change d'etat d'une autre "
                      "maniere que par une conversion : le guide officiel de "
                      "migration vers QNX 8.0 annonce son retrait. L'outil ne "
                      "devine pas : il cite la phrase du guide."
                      % len(retires))
        lignes.append("")
        for rec in retires:
            lignes.append("- `%s` (%s) : `%s` en J4 (mesure datee), "
                          "**`%s` : retire en 8.0 selon le guide officiel de "
                          "migration** aujourd'hui, priorite 1."
                          % (rec["symbol"], rec["repo"], rec["etat_j4"],
                             rec["etat"]))
            lignes.append("  phrase du guide, citee par l'outil : \"%s\""
                          % (rec.get("retrait", {}).get("phrase")
                             or rec.get("citation") or ""))
            lignes.append("  page du guide : %s (SHA-256 `%s...`)"
                          % (rec["url"], rec["page_sha256"][:16]))
        lignes.append("")
        lignes.append("C'est le point voulu par la regle : un appel a une "
                      "fonction **retiree de la 8.0 selon le guide officiel** "
                      "reste trouve, cite et prioritaire dans la liste de "
                      "travail, meme si la fonction n'a plus de page dans la "
                      "C Library Reference 8.0.")
        lignes.append("")
    lignes.append("## Ce qui n'a pas bouge")
    lignes.append("")
    lignes.append("Les %d symboles « non resolu » de J4 le restent : ils avaient une "
                  "page dans la C Library Reference **7.1** et n'en ont plus dans la "
                  "8.0. Ils ne sont pas inventes, pas effaces :"
                  % len(deja_absents))
    lignes.append("")
    for rec in deja_absents:
        lignes.append("- `%s` (%s) : page 7.1 `%s` - absent de la 8.0."
                      % (rec["symbol"], rec["repo"], rec["url"]))
    lignes.append("")
    lignes.append("Les %d symboles « resolu et cite » de J4 sont **inchanges** : "
                  "meme page, meme SHA-256, meme citation. La mesure J4 reste "
                  "une mesure datee ; la seule regle de l'outil qui a change "
                  "depuis est le classement des retraits annonces par le guide "
                  "officiel de migration (section precedente)."
                  % j4["counts"][RESOLU])
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
                  "que seuls les symboles convertis et les retraits annonces "
                  "par le guide officiel ont change d'etat, et que "
                  "l'empreinte de chaque page citee est bien celle du corpus "
                  "fige. La preuve ROUGE -> VERT est dans "
                  "`docs/preuves/h-mesure-j5-rouge.txt`.")
    lignes.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes))


def kind_en(kind):
    """Translates the kind of mention (data of the engine, in French)."""
    return KIND_EN.get(kind, kind)


def write_markdown_en(path, data, records):
    """Writes the J5 measurement in English (same figures as the fr version)."""
    prim = data["principal"]
    j4 = data["mesure_j4"]
    convertis = [r for r in records if r.get("resolution_j5")]
    absents = [r for r in records if r["etat"] == NON_RESOLU]
    deja_absents = [r for r in records
                    if r["etat"] == NON_RESOLU and r["etat_j4"] == NON_RESOLU]
    retires = [r for r in records
               if r["etat"] == NON_RESOLU and r["etat_j4"] != NON_RESOLU]
    lignes = []
    lignes.append("# Measurement J5 - QX PORTMAP resolution rate, same sample as "
                  "J4")
    lignes.append("")
    lignes.append("Measured on %s by `tools/mesure_j5.py` (reproducible: see "
                  "the \"Reproduce\" section below). Repositories consulted "
                  "on %s (sample unchanged). The French version of this "
                  "report is kept byte-identical in `docs/mesure-J5-FR.md`."
                  % (MESURE_LE, CONSULTED))
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
    if retires:
        lignes.append("## The removal announced by the official guide")
        lignes.append("")
        lignes.append("%d symbol of the sample changes state in another way "
                      "than a conversion: the official QNX 8.0 migration "
                      "guide announces its removal. The tool does not guess: "
                      "it quotes the sentence of the guide."
                      % len(retires))
        lignes.append("")
        for rec in retires:
            lignes.append("- `%s` (%s): `%s` in J4 (dated measurement), "
                          "**`%s`: removed in 8.0 according to the official "
                          "migration guide** today, priority 1."
                          % (rec["symbol"], rec["repo"],
                             ETAT_EN[rec["etat_j4"]], ETAT_EN[rec["etat"]]))
            lignes.append("  sentence of the guide, quoted by the tool: \"%s\""
                          % (rec.get("retrait", {}).get("phrase")
                             or rec.get("citation") or ""))
            lignes.append("  guide page: %s (SHA-256 `%s...`)"
                          % (rec["url"], rec["page_sha256"][:16]))
        lignes.append("")
        lignes.append("In a real public repository, the tool finds a call to a "
                      "function that the official guide says was **removed in "
                      "QNX 8.0**: still found, still quoted and at the top of "
                      "the work list, even though the function no longer has "
                      "a page in the 8.0 C Library Reference.")
        lignes.append("")
    lignes.append("## What has not changed")
    lignes.append("")
    lignes.append("The %d \"not resolved\" symbols of J4 remain so: they had a "
                  "page in the C Library Reference **7.1** and no longer have "
                  "one in 8.0. They are not invented, not erased:"
                  % len(deja_absents))
    lignes.append("")
    for rec in deja_absents:
        lignes.append("- `%s` (%s): 7.1 page `%s` - absent from 8.0."
                      % (rec["symbol"], rec["repo"], rec["url"]))
    lignes.append("")
    lignes.append("The %d \"resolved and cited\" symbols of J4 are "
                  "**unchanged**: same page, same SHA-256, same citation. The "
                  "J4 measurement remains a dated measurement; the only tool "
                  "rule that changed since is the classification of the "
                  "removals announced by the official migration guide "
                  "(section above)."
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
                  "fact that only the converted symbols and the removals "
                  "announced by the official guide changed state, and "
                  "that the fingerprint of each cited page is the one of the "
                  "frozen corpus. The RED -> GREEN proof is in "
                  "`docs/preuves/h-mesure-j5-rouge.txt`.")
    lignes.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes))


def write_citations(dir_path, data, records, lang="fr"):
    """Writes the literal citations, one page per repository (4,000-byte budget)."""
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
    """Writes the public JSON: everything except the text of the citations."""
    out = {
        "methode": data["methode"],
        "consulte_le": CONSULTED,
        "mesure_le": MESURE_LE,
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

    records = measure(classifier, corpus, choix,
                      etats_publies={r["symbol"]: r["etat"]
                                     for r in j4["symbols"]})
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
                   "empreinte SHA-256 ; un retrait annonce par le guide officiel "
                   "de migration 8.0 classe le symbole non resolu (priorite 1, "
                   "phrase du guide citee)",
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
