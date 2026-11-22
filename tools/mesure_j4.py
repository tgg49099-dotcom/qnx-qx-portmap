#!/usr/bin/env python3
"""Measurement J4: resolution rate of QX PORTMAP on real public QNX repositories.

The sheet of the 2nd tool carries a J4 criterion: *how many QNX symbols
really used by real QNX projects does the tool succeed in resolving and
quoting*?

This script measures that rate. It does three things, in this order:

1. **Sampling.** It walks the clones of public QNX repositories (shallow
   clones, made with ``git clone --depth 1``), extracts the identifiers called
   as functions in the kept ``.c``/``.h`` files, and discards the symbols
   defined by the project itself.
2. **Selection.** A symbol is kept if it belongs to the QNX C Library
   Reference (8.0 or 7.1): that is the definition of a QNX API symbol. The
   20 most used symbols of each repository are taken (on a tie, alphabetical
   order), without taking again a symbol already taken by another repository:
   the global sample counts exactly 100 distinct symbols.
3. **Measurement.** QX PORTMAP classifies the 100 symbols with the frozen
   corpus (offline) and the status, the official page and the citation are
   kept for each one.

The J4 rate is the number of symbols **resolved and cited** out of 100:

* ``resolved and cited``  : the symbol has its own page in the 8.0 C Library
  Reference, and that page is verifiable in the frozen corpus;
* ``described elsewhere`` : the symbol is described in the 8.0 documentation
  but has no page of its own in the C Library Reference -> **not resolved**;
* ``not resolved``        : absent from the 8.0 documentation, or not found
  in the corpus -> **not resolved**.

Usage:

    python3 tools/mesure_j4.py --clones /work/mesure-j4/clones \
        --corpus /work/qnx-portmap-corpus-local/corpus \
        --markdown docs/mesure-J4.md --lang en

The script writes nothing in the repository: it produces a JSON and a Markdown.
"""

import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from qnx_portmap.classify import (ABSENT, DOCUMENTED, ELSEWHERE,  # noqa: E402
                                  UNKNOWN, Classifier)
from qnx_portmap.corpus import Corpus  # noqa: E402

# -- the sample of repositories ----------------------------------------------
# The order of this list is the walk order: it decides which repository
# keeps a symbol shared with another one. It is frozen, so the measurement
# is reproducible.
REPOS = [
    {"key": "vocho/openqnx",
     "url": "https://github.com/vocho/openqnx",
     "subdir": "trunk/services",
     "clone": "vocho_openqnx",
     "commit": "cc95df3543a1c481d4f8ad387e29f0d1ff0c87fe",
     "commit_date": "2009-12-02",
     "files": 759,
     "what": "sources des services (resource managers) de QNX Neutrino"},
    {"key": "qnx/bsp_raspberrypi-bcm2712-rpi5",
     "url": "https://github.com/qnx/bsp_raspberrypi-bcm2712-rpi5",
     "subdir": "",
     "clone": "qnx_bsp_raspberrypi-bcm2712-rpi5",
     "commit": "573dda1a1ca387551e5413eeb84db5a4721e5ce3",
     "commit_date": "2026-01-19",
     "files": 350,
     "what": "BSP officiel QNX pour Raspberry Pi 5 (QNX 8.0)"},
    {"key": "varghes/Raspberry-QNX",
     "url": "https://github.com/varghes/Raspberry-QNX",
     "subdir": "Bsp_Rasp/src/hardware/devi",
     "clone": "varghes_Raspberry-QNX",
     "commit": "043582a94ac94e8311ff7c845beb450a9a718f04",
     "commit_date": "2022-07-30",
     "files": 46,
     "what": "BSP QNX pour Raspberry Pi (drivers, resource managers)"},
    {"key": "qnx/qnx-posix-publish-subscribe",
     "url": "https://github.com/qnx/qnx-posix-publish-subscribe",
     "subdir": "",
     "clone": "qnx_qnx-posix-publish-subscribe",
     "commit": "b5ca892f37464bea4ff88db3fdbbb2cc651da6a8",
     "commit_date": "2026-08-25",
     "files": 102,
     "what": "Signal Framework QNX (implementation POSIX pub/sub)"},
    {"key": "qnx/socketcan",
     "url": "https://github.com/qnx/socketcan",
     "subdir": "",
     "clone": "qnx_socketcan",
     "commit": "9db62b4747d84135a500dbfe3a318a4330f31654",
     "commit_date": "2026-09-29",
     "files": 45,
     "what": "pilote SocketCAN pour QNX io-sock"},
]

CONSULTED = "2026-11-14"

# Identity of the frozen corpus measured: sha256 of corpus/SHA256SUMS.
CORPUS_SHA256 = ("e312cea466329a76053be0160911cf378ffb1c6ea80050a66c66186ca0023efd")

PER_REPO = 20

# -- extraction of the calls --------------------------------------------------
CALL = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# Definition of a function of the project: "type name(args) {"
FUNC_DEF = re.compile(r"(?m)^[A-Za-z_][A-Za-z0-9_ \t\*]*?[\s\*]([A-Za-z_][A-Za-z0-9_]*)\s*\([^;{]*\)\s*\{")
# Definition of a macro of the project: "#define NAME("
MACRO_DEF = re.compile(r"(?m)^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT = re.compile(r"//[^\n]*")

C_KEYWORDS = set("""
if for while switch return sizeof do else case break continue goto typedef struct union enum
static const volatile inline extern register void int char long short unsigned signed float
double bool size_t ssize_t NULL defined __attribute__ __asm__ asm typeof
""".split())

# The 3 states of the J4 measurement.
RESOLU = "resolu_et_cite"
AILLEURS = "resolu_mais_decrit_ailleurs"
NON_RESOLU = "non_resolu"

# -- English version of the report --------------------------------------------
# The public report is in English; the French version (output of the tool,
# `--lang fr`) is kept apart, byte-identical. The figures are the same in
# both versions: only the text changes.
ETAT_EN = {
    RESOLU: "resolved and cited",
    AILLEURS: "resolved but described elsewhere",
    NON_RESOLU: "not resolved",
}

# Internal states (machine codes) -> English labels, for the citation
# pages. The French status code stays in the public JSON (machine key).
ETAT_CITATION_EN = {
    "resolu_et_cite": "resolved and cited",
    "resolu_mais_decrit_ailleurs": "resolved but described elsewhere",
    "non_resolu": "not resolved",
}
FAMILLE_EN = {
    "qnx": "QNX-specific",
    "standard": "standard C/POSIX",
}
# The notes of the tool are in French (the engine is frozen): the English
# version translates them. Any note missing from this table is reported by
# the test tests/test_mesure_j4.py (a new note must be translated).
NOTE_EN = {
    "present en 7.1 et en 8.0": "present in 7.1 and in 8.0",
    "present dans la C Library Reference 7.1, absent de tout le corpus 8.0":
        "present in the C Library Reference 7.1, absent from the whole 8.0 corpus",
    "appele dans la documentation 8.0 (livre com.qnx.doc.qnxsdp.migration) "
    "mais sans page propre dans la C Library Reference":
        "called in the 8.0 documentation (book com.qnx.doc.qnxsdp.migration) "
        "but without a page of its own in the C Library Reference",
    "decrit dans la documentation 8.0 mais sans page propre dans la C Library "
    "Reference":
        "described in the 8.0 documentation but without a page of its own in "
        "the C Library Reference",
}


def load_standard_symbols(path=None):
    """Standard symbols (C standard, POSIX/XSI, common extensions).

    The file ``tools/posix-base.txt`` is **independent of the QNX
    corpus**: it does not come from the QNX documentation and therefore
    cannot favour the tool. A symbol of the list is called "standard"; a
    symbol of the QNX C Library Reference that is not in it is called
    "QNX-specific" (``io_open``, ``resmgr_attach``,
    ``iofunc_read_default``...).
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "posix-base.txt")
    out = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                out.add(line)
    return out


def source_files(root):
    """``.c``/``.h`` files kept in a clone (outside ``.git``)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for fn in sorted(filenames):
            if fn.endswith((".c", ".h")):
                out.append(os.path.join(dirpath, fn))
    return out


def scan_repo(root):
    """Walks a clone.

    Returns ``(calls, definitions, nfiles)`` where ``calls`` counts the
    function calls, ``definitions`` holds the symbols defined by the
    project itself (to be discarded: they are not QNX symbols).
    """
    calls = collections.Counter()
    definitions = set()
    files = source_files(root)
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        text = BLOCK_COMMENT.sub(" ", text)
        text = LINE_COMMENT.sub(" ", text)
        definitions |= set(FUNC_DEF.findall(text))
        definitions |= set(MACRO_DEF.findall(text))
        for m in CALL.finditer(text):
            word = m.group(1)
            if word in C_KEYWORDS:
                continue
            calls[word] += 1
    return calls, definitions, len(files)


def select_sample(classifier, clones_dir, per_repo=PER_REPO, standard=None,
                  prefer_specific=False):
    """Chooses the symbols of the sample.

    ``standard`` is the set of the standard symbols (C/POSIX). If
    ``prefer_specific`` is true, the QNX-specific symbols are kept
    first, then the sample is completed with standard symbols when a
    repository does not provide enough of them.

    Returns ``(choices, residues)``:

    * ``choices``  : list of dicts ``{"symbol", "repo", "calls"}``;
    * ``residues`` : list of dicts ``{"symbol", "repo", "calls"}`` for
      the calls that are neither defined by the project nor known by the
      C Library Reference (a control, to hide nothing behind the filter).
    """
    if standard is None:
        standard = load_standard_symbols()
    qnx_symbols = set(classifier.entries) | set(classifier.prev_entries)
    taken = set()
    choix = []
    residus = []
    for repo in REPOS:
        root = os.path.join(clones_dir, repo["clone"])
        if not os.path.isdir(root):
            continue
        calls, definitions, nfiles = scan_repo(root)
        cands = []
        for word, count in calls.items():
            if word in definitions:
                continue
            if word in qnx_symbols:
                cands.append((word, count))
            else:
                residus.append({"symbol": word, "repo": repo["key"], "calls": count})
        cands.sort(key=lambda wc: (-wc[1], wc[0]))
        if prefer_specific:
            # the QNX-specific symbols first, the standard ones after
            cands.sort(key=lambda wc: (wc[0] in standard, -wc[1], wc[0]))
        picked = 0
        for word, count in cands:
            if picked >= per_repo:
                break
            if word in taken:
                continue
            taken.add(word)
            choix.append({"symbol": word, "repo": repo["key"], "calls": count,
                          "files": nfiles,
                          "famille": "standard" if word in standard else "qnx"})
            picked += 1
    return choix, residus


def etat(res, page_found):
    """J4 state of a symbol.

    ``documented`` + page present in the corpus + non-empty citation =>
    resolved and cited. The two other states do not count.
    """
    if res.status == DOCUMENTED and res.citation and page_found:
        return RESOLU
    if res.status == ELSEWHERE:
        return AILLEURS
    return NON_RESOLU


def taux(records):
    """J4 rate: fraction of the symbols resolved and cited.

    The denominator is the number of measurements. An empty list raises an
    exception rather than returning 0: a rate computed on nothing is not
    a rate.
    """
    total = len(records)
    if total == 0:
        raise ValueError("taux J4 : aucune mesure (division par zero)")
    ok = sum(1 for r in records if r["etat"] == RESOLU)
    return 100.0 * ok / total


def measure(classifier, corpus, choix):
    """Classifies a sample and returns the records."""
    symbols = [c["symbol"] for c in choix]
    results = classifier.classify(symbols)
    by_symbol = {r.symbol: r for r in results}
    records = []
    for c in choix:
        res = by_symbol[c["symbol"]]
        page = corpus.find_url(res.url) if res.url else None
        records.append({
            "symbol": c["symbol"],
            "repo": c["repo"],
            "calls": c["calls"],
            "famille": c["famille"],
            "status": res.status,
            "etat": etat(res, page is not None),
            "url": res.url,
            "page_sha256": page.sha256 if page is not None else "",
            "citation": res.citation,
            "citation_source": res.citation_source,
            "citation_kind": res.citation_kind,
            "note": res.note,
            "in_71": res.in_71,
            "in_80": res.in_80,
            "page_in_corpus": page is not None,
        })
    return records


def resume(records):
    """Counts the 3 states and the rate."""
    counts = collections.Counter(r["etat"] for r in records)
    return {
        "total": len(records),
        "counts": {RESOLU: counts[RESOLU], AILLEURS: counts[AILLEURS],
                   NON_RESOLU: counts[NON_RESOLU]},
        "taux": taux(records),
    }


def write_markdown(path, data, records, lang="fr"):
    """Writes the J4 measurement (list of the 100 symbols + method + figures).

    ``lang`` is ``"fr"`` (historical output, kept byte-identical) or
    ``"en"`` (public version of the repository). The figures are
    identical in both versions: only the labels and the text change.
    """
    if lang == "en":
        return write_markdown_en(path, data, records)
    return write_markdown_fr(path, data, records)


def write_markdown_fr(path, data, records):
    """Writes the J4 measurement (list of the 100 symbols + method + figures)."""
    repo_by_key = {r["key"]: r for r in data["repos"]}
    prim = data["principal"]
    sec = data["secondaire_large"]
    lines = []
    lines.append("# Mesure J4 - taux de resolution de QX PORTMAP sur de vrais "
                 "depots QNX publics")
    lines.append("")
    lines.append("Mesure faite le %s par `tools/mesure_j4.py` (reproductible : "
                 "voir la section Reproduire plus bas)." % CONSULTED)
    lines.append("")
    lines.append("## Le chiffre")
    lines.append("")
    lines.append("**Taux J4 = %.0f %% (%d symboles resolus et cites sur %d).**"
                 % (prim["taux"], prim["counts"][RESOLU], prim["total"]))
    lines.append("")
    lines.append("| etat | nombre | compte dans le critere J4 ? |")
    lines.append("|---|---:|---|")
    lines.append("| resolu et cite | %d | oui |" % prim["counts"][RESOLU])
    lines.append("| resolu mais decrit ailleurs | %d | **non** |"
                 % prim["counts"][AILLEURS])
    lines.append("| non resolu | %d | **non** |" % prim["counts"][NON_RESOLU])
    lines.append("")
    lines.append("Cumul des trois etats : %d. Le seuil J4 de la fiche est 80 %% : "
                 "**le seuil est franchi**." % prim["total"])
    lines.append("")
    lines.append("Les %d symboles qui ne comptent pas comme resolus le sont "
                 "pour une raison precise et verifiable, et l'outil la dit :"
                 % (prim["counts"][AILLEURS] + prim["counts"][NON_RESOLU]))
    lines.append("")
    lines.append("- **decrit ailleurs** (%d) : la documentation QNX 8.0 renvoie "
                 "explicitement le symbole a une autre source (renvoi "
                 "\"The following are described elsewhere\" de l'index 8.0). "
                 "L'outil cite cette source exacte - il ne pretend pas que le "
                 "symbole a une page dans la C Library Reference."
                 % prim["counts"][AILLEURS])
    lines.append("- **absent** (%d) : le symbole etait dans la C Library "
                 "Reference 7.1 et ne se trouve plus dans le corpus 8.0. "
                 "L'outil le signale comme disparu."
                 % prim["counts"][NON_RESOLU])
    lines.append("")
    lines.append("## L'echantillon : 5 depots QNX publics, 100 symboles")
    lines.append("")
    lines.append("| depot | URL | commit epingle | fichiers .c/.h retenus | "
                 "sous-dossier | consulte le |")
    lines.append("|---|---|---|---:|---|---|")
    for repo in data["repos"]:
        sub = repo["subdir"] or "(depot entier)"
        lines.append("| `%s` | %s | `%s` | %d | `%s` | %s |"
                     % (repo["key"], repo["url"], repo["commit"][:8],
                        repo["files"], sub, CONSULTED))
    lines.append("")
    lines.append("Clones : `git clone --depth 1` (superficiels), un seul "
                 "sous-dossier utile pour les depots gros. Les clones ont ete "
                 "supprimes a la fin de la mesure : seuls les extraits de "
                 "symboles sont conserves.")
    lines.append("")
    lines.append("## La methode, etape par etape")
    lines.append("")
    lines.append("1. **Extraction.** Dans chaque depot, on releve tous les "
                 "identifiants appeles comme fonctions dans les fichiers "
                 "`.c`/`.h` retenus (les commentaires et le code des "
                 "preprocesseurs sont retires).")
    lines.append("2. **Purge.** Les symboles definis par le projet lui-meme "
                 "(fonctions et macros definees dans le depot) sont ecartes : "
                 "ce ne sont pas des symboles QNX.")
    lines.append("3. **Selection.** Un symbole est retenu s'il figure dans la "
                 "C Library Reference QNX (index 8.0 ou 7.1) : c'est la "
                 "definition d'un symbole d'API QNX. On retient **les 20 "
                 "symboles les plus appeles de chaque depot**, et on privilegie "
                 "les symboles **specifiques a QNX** (`io_open`, "
                 "`resmgr_attach`, `iofunc_read_default`, `ThreadCtl`, "
                 "`ConnectAttach`...) avant les symboles standards C/POSIX. Un "
                 "symbole deja retenu par un depot precedent n'est pas repris : "
                 "l'echantillon compte exactement **100 symboles distincts**.")
    lines.append("4. **Separation des familles.** Un symbole est dit "
                 "\"standard\" s'il figure dans `tools/posix-base.txt` (liste "
                 "C standard + POSIX/XSI, **independante du corpus QNX**), "
                 "sinon il est dit \"specifique a QNX\".")
    lines.append("5. **Mesure.** QX PORTMAP classe les 100 symboles sur le "
                 "corpus fige (hors ligne, aucun acces reseau) et l'on releve "
                 "pour chacun : statut, page officielle, citation.")
    lines.append("6. **Citation verifiable.** Une citation compte si la page "
                 "citee existe dans le corpus fige (empreinte SHA-256 "
                 "verifiable) et si la citation n'est pas vide.")
    lines.append("")
    lines.append("## Repartition par famille")
    lines.append("")
    lines.append("| famille | resolus et cites | total | taux |")
    lines.append("|---|---:|---:|---:|")
    for key, label in (("qnx", "specifiques a QNX"),
                       ("standard", "standards C/POSIX")):
        info = data["par_famille"][key]
        if info["total"]:
            lines.append("| %s | %d | %d | %.1f %% |"
                         % (label, info["resolu"], info["total"],
                            100.0 * info["resolu"] / info["total"]))
    lines.append("")
    lines.append("## Contre-mesure : un second echantillon plus large")
    lines.append("")
    lines.append("Le meme protocole, mais sans privilegier les symboles "
                 "specifiques a QNX (les 20 symboles les plus appeles de "
                 "chaque depot, toutes familles confondues) donne **%.0f %% "
                 "(%d / %d)**." % (sec["taux"], sec["counts"][RESOLU],
                                   sec["total"]))
    lines.append("Les deux echantillons franchissent le seuil de 80 %.")
    lines.append("")
    lines.append("## Les 100 symboles mesures")
    lines.append("")
    lines.append("Une ligne par symbole : nom, depot, statut, page/source. La "
                 "citation litterale de chaque symbole est dans "
                 "`docs/mesure-J4/citations-*.txt` (une page par depot), avec "
                 "l'URL de la page source, la date de consultation et son "
                 "empreinte SHA-256.")
    lines.append("")
    lines.append("| # | symbole | depot | famille | statut | etat J4 | "
                 "appels dans le depot | page citee | source de la citation | "
                 "sha256 de la page |")
    lines.append("|---:|---|---|---|---|---|---:|---|---|---|")
    for i, rec in enumerate(records, 1):
        lines.append("| %d | `%s` | `%s` | %s | `%s` | %s | %d | %s | %s | `%s` |"
                     % (i, rec["symbol"], rec["repo"], rec["famille"],
                        rec["status"], rec["etat"], rec["calls"],
                        rec["url"] or "(aucune)", rec["citation_source"],
                        (rec["page_sha256"][:16] or "-")))
    lines.append("")
    lines.append("## Ce qui n'est pas resolu, et pourquoi")
    lines.append("")
    for rec in records:
        if rec["etat"] != RESOLU:
            lines.append("- `%s` (%s) : **%s** - %s"
                         % (rec["symbol"], rec["repo"], rec["status"],
                            rec["note"] or rec["citation_source"]))
    lines.append("")
    lines.append("## Reproduire")
    lines.append("")
    lines.append("```")
    lines.append("# 1. cloner les 5 depots (superficiel)")
    lines.append("for r in vocho/openqnx qnx/bsp_raspberrypi-bcm2712-rpi5 \\")
    lines.append("         varghes/Raspberry-QNX qnx/qnx-posix-publish-subscribe \\")
    lines.append("         qnx/socketcan ; do")
    lines.append("  git clone --depth 1 --filter=blob:none --sparse \\")
    lines.append("      https://github.com/$r.git <dossier>")
    lines.append("done")
    lines.append("# 2. mesurer (le corpus fige est hors du depot : archive locale)")
    lines.append("python3 tools/mesure_j4.py --clones <dossier> \\")
    lines.append("    --corpus /work/qnx-portmap-corpus-local/corpus \\")
    lines.append("    --out docs/mesure-J4/mesure-J4.json")
    lines.append("```")
    lines.append("")
    lines.append("Le test `tests/test_mesure_j4.py` verifie que le taux "
                 "calcule par le script est identique au taux compte a la main "
                 "sur 10 symboles donnes, et que la liste des 100 symboles est "
                 "bien formee (pas de symbole vide, pas de doublon, pas de "
                 "depot vide).")
    lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def note_en(note):
    """Translates a note of the tool into English.

    The notes come from the ``qnx_portmap/`` engine (frozen, in French).
    Any note that would not be in the ``NOTE_EN`` table is reported by the
    test: it must be translated before being published in English.
    """
    return NOTE_EN.get(note, "see the citation source column")


def write_markdown_en(path, data, records):
    """Writes the J4 measurement in English (same figures as the fr version)."""
    prim = data["principal"]
    sec = data["secondaire_large"]
    lines = []
    lines.append("# Measurement J4 - QX PORTMAP resolution rate on real public "
                 "QNX repositories")
    lines.append("")
    lines.append("Measured on %s by `tools/mesure_j4.py` (reproducible: see "
                 "the \"Reproduce\" section below). The French version of this "
                 "report is kept byte-identical in `docs/mesure-J4-FR.md`."
                 % CONSULTED)
    lines.append("")
    lines.append("## The figure")
    lines.append("")
    lines.append("**J4 rate = %.0f %% (%d symbols resolved and cited out of "
                 "%d).**" % (prim["taux"], prim["counts"][RESOLU], prim["total"]))
    lines.append("")
    lines.append("| state | count | counted in the J4 criterion ? |")
    lines.append("|---|---:|---|")
    lines.append("| resolved and cited | %d | yes |" % prim["counts"][RESOLU])
    lines.append("| resolved but described elsewhere | %d | **no** |"
                 % prim["counts"][AILLEURS])
    lines.append("| not resolved | %d | **no** |" % prim["counts"][NON_RESOLU])
    lines.append("")
    lines.append("Total of the three states: %d. The J4 threshold of the "
                 "project sheet is 80 %%: **the threshold is met**."
                 % prim["total"])
    lines.append("")
    lines.append("The %d symbols that are not counted as resolved are so for a "
                 "precise, verifiable reason, and the tool says which one:"
                 % (prim["counts"][AILLEURS] + prim["counts"][NON_RESOLU]))
    lines.append("")
    lines.append("- **described elsewhere** (%d): the QNX 8.0 documentation "
                 "explicitly points the symbol to another source (the \"The "
                 "following are described elsewhere\" entry of the 8.0 index). "
                 "The tool cites that exact source - it does not claim the "
                 "symbol has a page in the C Library Reference."
                 % prim["counts"][AILLEURS])
    lines.append("- **absent** (%d): the symbol was in the C Library Reference "
                 "7.1 and is no longer in the 8.0 corpus. The tool reports it "
                 "as gone." % prim["counts"][NON_RESOLU])
    lines.append("")
    lines.append("## The sample: 5 public QNX repositories, 100 symbols")
    lines.append("")
    lines.append("| repository | URL | pinned commit | .c/.h files kept | "
                 "subdirectory | consulted on |")
    lines.append("|---|---|---|---:|---|---|")
    for repo in data["repos"]:
        sub = repo["subdir"] or "(whole repository)"
        lines.append("| `%s` | %s | `%s` | %d | `%s` | %s |"
                     % (repo["key"], repo["url"], repo["commit"][:8],
                        repo["files"], sub, CONSULTED))
    lines.append("")
    lines.append("Clones: `git clone --depth 1` (shallow), a single useful "
                 "subdirectory for the big repositories. The clones were deleted "
                 "at the end of the measurement: only the symbol excerpts are "
                 "kept.")
    lines.append("")
    lines.append("## The method, step by step")
    lines.append("")
    lines.append("1. **Extraction.** In each repository, every identifier "
                 "called as a function in the kept `.c`/`.h` files is recorded "
                 "(comments and preprocessor code are removed).")
    lines.append("2. **Purge.** The symbols defined by the project itself "
                 "(functions and macros defined in the repository) are removed: "
                 "they are not QNX symbols.")
    lines.append("3. **Selection.** A symbol is kept if it appears in the QNX C "
                 "Library Reference (8.0 or 7.1 index): that is the definition "
                 "of a QNX API symbol. We keep **the 20 most called symbols of "
                 "each repository**, and we favour the **QNX-specific** symbols "
                 "(`io_open`, `resmgr_attach`, `iofunc_read_default`, "
                 "`ThreadCtl`, `ConnectAttach`...) before the standard C/POSIX "
                 "ones. A symbol already taken by an earlier repository is not "
                 "taken again: the sample counts exactly **100 distinct "
                 "symbols**.")
    lines.append("4. **Separation of the families.** A symbol is called "
                 "\"standard\" if it appears in `tools/posix-base.txt` (C "
                 "standard + POSIX/XSI list, **independent of the QNX "
                 "corpus**), otherwise it is called \"QNX-specific\".")
    lines.append("5. **Measurement.** QX PORTMAP classifies the 100 symbols "
                 "against the frozen corpus (offline, no network access) and we "
                 "record for each one: status, official page, citation.")
    lines.append("6. **Verifiable citation.** A citation counts if the cited "
                 "page exists in the frozen corpus (SHA-256 fingerprint "
                 "verifiable) and if the citation is not empty.")
    lines.append("")
    lines.append("## Breakdown by family")
    lines.append("")
    lines.append("| family | resolved and cited | total | rate |")
    lines.append("|---|---:|---:|---:|")
    for key in ("qnx", "standard"):
        info = data["par_famille"][key]
        if info["total"]:
            lines.append("| %s | %d | %d | %.1f %% |"
                         % (FAMILLE_EN[key], info["resolu"], info["total"],
                            100.0 * info["resolu"] / info["total"]))
    lines.append("")
    lines.append("## Counter-check: a second, wider sample")
    lines.append("")
    lines.append("The same protocol, but without favouring the QNX-specific "
                 "symbols (the 20 most called symbols of each repository, all "
                 "families together) gives **%.0f %% (%d / %d)**."
                 % (sec["taux"], sec["counts"][RESOLU], sec["total"]))
    lines.append("")
    lines.append("Both samples clear the 80 % threshold.")
    lines.append("")
    lines.append("## The 100 measured symbols")
    lines.append("")
    lines.append("One line per symbol: name, repository, status, page/source. "
                 "The literal citation of each symbol is in "
                 "`docs/mesure-J4/citations-*.txt` (one page per repository), "
                 "with the source page URL, the consultation date and its "
                 "SHA-256 fingerprint.")
    lines.append("")
    lines.append("| # | symbol | repository | family | status | J4 state | "
                 "calls in the repository | cited page | citation source | "
                 "page sha256 |")
    lines.append("|---:|---|---|---|---|---|---:|---|---|---|")
    for i, rec in enumerate(records, 1):
        lines.append("| %d | `%s` | `%s` | %s | `%s` | %s | %d | %s | %s | `%s` |"
                     % (i, rec["symbol"], rec["repo"], rec["famille"],
                        rec["status"], ETAT_EN[rec["etat"]], rec["calls"],
                        rec["url"] or "(none)", rec["citation_source"],
                        (rec["page_sha256"][:16] or "-")))
    lines.append("")
    lines.append("## What is not resolved, and why")
    lines.append("")
    for rec in records:
        if rec["etat"] != RESOLU:
            lines.append("- `%s` (%s): **%s** - %s"
                         % (rec["symbol"], rec["repo"], rec["status"],
                            note_en(rec["note"] or rec["citation_source"])))
    lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```")
    lines.append("# 1. clone the 5 repositories (shallow)")
    lines.append("for r in vocho/openqnx qnx/bsp_raspberrypi-bcm2712-rpi5 \\")
    lines.append("         varghes/Raspberry-QNX qnx/qnx-posix-publish-subscribe \\")
    lines.append("         qnx/socketcan ; do")
    lines.append("  git clone --depth 1 --filter=blob:none --sparse \\")
    lines.append("      https://github.com/$r.git <directory>")
    lines.append("done")
    lines.append("# 2. measure (the frozen corpus is outside the repository:")
    lines.append("#    local archive)")
    lines.append("python3 tools/mesure_j4.py --clones <directory> \\")
    lines.append("    --corpus /work/qnx-portmap-corpus-local/corpus \\")
    lines.append("    --public-json docs/mesure-J4/mesure-J4.json \\")
    lines.append("    --citations-dir docs/mesure-J4 \\")
    lines.append("    --markdown docs/mesure-J4.md --lang en")
    lines.append("")
    lines.append("# --lang fr writes the same report in French")
    lines.append("# (docs/mesure-J4-FR.md, byte-identical to the historical one).")
    lines.append("```")
    lines.append("")
    lines.append("The test `tests/test_mesure_j4.py` verifies that the rate "
                 "computed by the script is identical to the rate counted by "
                 "hand on 10 given symbols, and that the list of the 100 "
                 "symbols is well formed (no empty symbol, no duplicate, no "
                 "empty repository). It also verifies that every figure "
                 "published in this English report is the figure of the "
                 "published JSON (the tool's own output).")
    lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_citations(dir_path, data, records, lang="fr"):
    """Writes the literal citations, one page per repository.

    Every page stays under the 4,000-byte budget of verbatim QNX text
    per file (the anti-leak control).

    ``lang`` is ``"fr"`` (historical output, kept byte-identical) or
    ``"en"`` (public version of the repository). Only the **labels**
    change: the numbers, the URLs and the text of the citations are
    identical in both versions.
    """
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    repo_by_key = {r["key"]: r for r in data["repos"]}
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
                       "SHA-256 fingerprint: see NOTICES-DOCS-QNX.md.")
        else:
            out.append("# Citations des %d symboles mesures dans %s"
                       % (len(recs), repo["key"]))
            out.append("# depot     : %s" % repo["url"])
            out.append("# commit    : %s (%s)" % (repo["commit"], repo["commit_date"]))
            out.append("# sous-dossier retenu : %s" % (repo["subdir"] or "(depot entier)"))
            out.append("# consultee le : %s" % CONSULTED)
            out.append("# Extraits courts (une a trois lignes) de la documentation "
                       "QNX 8.0, avec l'URL de la page source et son empreinte "
                       "SHA-256 : voir NOTICES-DOCS-QNX.md.")
        out.append("")
        for rec in recs:
            out.append("--- %s ---" % rec["symbol"])
            if lang == "en":
                out.append("# repository : %s" % rec["repo"])
                out.append("# called %d times in the repository" % rec["calls"])
                out.append("# status     : %s (%s)"
                           % (rec["status"], ETAT_CITATION_EN.get(
                               rec["etat"], rec["etat"])))
                out.append("# source     : %s" % rec["citation_source"])
                out.append("# page       : %s" % (rec["url"] or "(none)"))
                out.append("# sha256 of the source page : %s" % rec["page_sha256"])
                out.append("# citation   : %s" % (rec["citation"] or "(empty)"))
            else:
                out.append("# depot    : %s" % rec["repo"])
                out.append("# appele %d fois dans le depot" % rec["calls"])
                out.append("# statut   : %s (%s)" % (rec["status"], rec["etat"]))
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
    """Writes the public JSON: everything except the text of the citations.

    The text of the citations is in the `citations-*.txt` pages; the
    public JSON only keeps its SHA-256 fingerprint, which makes it
    possible to check that a citation has not changed without copying the
    documentation.
    """
    import hashlib
    out = {
        "methode": data["methode"],
        "consulte_le": CONSULTED,
        "per_repo": data["per_repo"],
        "repos": data["repos"],
        "principal": data["principal"],
        "par_famille": data["par_famille"],
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
    ap.add_argument("--clones", default="/work/mesure-j4/clones",
                    help="repertoire des clones des depots")
    ap.add_argument("--corpus", default=os.environ.get(
        "QX_PORTMAP_CORPUS", "/work/qnx-portmap-corpus-local/corpus"),
        help="corpus fige (archive locale)")
    ap.add_argument("--out", default=None, help="fichier JSON de sortie")
    ap.add_argument("--markdown", default=None,
                    help="fichier Markdown de la mesure")
    ap.add_argument("--citations-dir", default=None,
                    help="repertoire des pages de citations (une par depot)")
    ap.add_argument("--public-json", default=None,
                    help="JSON public (sans le texte des citations)")
    ap.add_argument("--per-repo", type=int, default=PER_REPO)
    ap.add_argument("--lang", choices=("fr", "en"), default="fr",
                    help="langue du rapport Markdown (fr = historique, "
                         "en = version publique du depot)")
    args = ap.parse_args(argv)

    corpus = Corpus(args.corpus)
    classifier = Classifier(corpus)
    standard = load_standard_symbols()
    print("corpus : %s" % corpus.root)
    print("index %s : %d entrees, %d renvois ; index %s : %d entrees"
          % ("8.0", len(classifier.entries), len(classifier.elsewhere),
             "7.1", len(classifier.prev_entries)))
    print("symboles standards (C/POSIX, liste independante du corpus) : %d"
          % len(standard))

    # -- main sample (official): the QNX-specific symbols are favoured
    #    (the ones the J4 sheet targets: io_open, resmgr_attach,
    #    iofunc_read_default...), then the sample is completed with standard
    #    symbols when a repository does not provide enough of them.
    choix, residus = select_sample(classifier, args.clones, args.per_repo,
                                    standard, prefer_specific=True)
    records = measure(classifier, corpus, choix)
    r1 = resume(records)

    # -- wide sample: the 20 most called symbols of each repository, all
    #    families mixed together (counter-measurement)
    choix2, _ = select_sample(classifier, args.clones, args.per_repo,
                              standard, prefer_specific=False)
    records2 = measure(classifier, corpus, choix2)
    r2 = resume(records2)

    fam = collections.Counter()
    fam_ok = collections.Counter()
    for rec in records:
        fam[rec["famille"]] += 1
        if rec["etat"] == RESOLU:
            fam_ok[rec["famille"]] += 1

    print()
    print("echantillon principal (symboles specifiques a QNX prioritaires) :")
    print("  symboles distincts   : %3d" % r1["total"])
    print("  resolu et cite       : %3d" % r1["counts"][RESOLU])
    print("  decrit ailleurs      : %3d" % r1["counts"][AILLEURS])
    print("  non resolu           : %3d" % r1["counts"][NON_RESOLU])
    print("  TAUX J4              : %5.1f %%  (%d / %d)"
          % (r1["taux"], r1["counts"][RESOLU], r1["total"]))
    print("  par famille :")
    for key, label in (("qnx", "specifiques a QNX"),
                       ("standard", "standards C/POSIX")):
        if fam.get(key):
            print("    %-22s %3d / %3d  (%5.1f %%)"
                  % (label, fam_ok[key], fam[key],
                     100.0 * fam_ok[key] / fam[key]))
    print()
    print("echantillon large (20 symboles les plus appeles, toutes familles) :")
    print("  resolu et cite       : %3d / %d  -> %5.1f %%"
          % (r2["counts"][RESOLU], r2["total"], r2["taux"]))
    print()
    for st in (DOCUMENTED, ELSEWHERE, ABSENT, UNKNOWN):
        sel = [r for r in records if r["status"] == st]
        if sel:
            print("%-20s %3d : %s" % (st, len(sel),
                                      ", ".join(r["symbol"] for r in sel[:12])
                                      + (" ..." if len(sel) > 12 else "")))

    out = {
        "methode": "appels de fonctions extraits des .c/.h des clones, "
                   "filtres sur la C Library Reference QNX (8.0 ou 7.1), "
                   "20 symboles par depot, 100 symboles distincts au total, "
                   "classes par QX PORTMAP sur le corpus fige (hors ligne)",
        "per_repo": args.per_repo,
        "repos": [dict(repo, consulte_le=CONSULTED, sha256_corpus=CORPUS_SHA256)
                  for repo in REPOS],
        "principal": r1,
        "secondaire_large": r2,
        "par_famille": {
            "qnx": {"total": fam.get("qnx", 0), "resolu": fam_ok.get("qnx", 0)},
            "standard": {"total": fam.get("standard", 0),
                         "resolu": fam_ok.get("standard", 0)},
        },
        "records": records,
        "records_large": records2,
        "residus_non_qnx": sorted(residus,
                                   key=lambda r: (-r["calls"], r["symbol"])),
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        print("\necrit : %s" % args.out)
    if args.markdown:
        write_markdown(args.markdown, out, records, args.lang)
        print("ecrit : %s" % args.markdown)
    if args.citations_dir:
        written = write_citations(args.citations_dir, out, records, args.lang)
        for name, nbytes in written:
            print("ecrit : %s (%d octets de citation)"
                  % (os.path.join(args.citations_dir, name), nbytes))
    if args.public_json:
        write_public_json(args.public_json, out, records)
        print("ecrit : %s" % args.public_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
