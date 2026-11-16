"""Command line interface of QX PORTMAP.

QX PORTMAP answers one single question: given a list of QNX symbols, where
does each one stand in the official 8.0 documentation?

By default, the tool never touches the network: it reads the frozen
documentation corpus of the repository.
"""

import argparse
import os
import sys

from .classify import Classifier
from .corpus import Corpus, CorpusError, default_corpus_dir, read_symbols
from .quick import apply_quick_limits, is_quick
from .report import render_json, render_markdown, render_text

# Help of the argument parser in the two output languages. English is the
# default language of the console; the French help is printed on demand
# (``--lang fr``) and states the same real default.
HELP_STRINGS = {
    "fr": {
        "description": "Etat des symboles QNX dans la documentation 8.0 "
                       "(corpus fige, hors ligne par defaut).",
        "epilog": "Exemples :\n"
                  "  qnx-portmap abort pthread_create bzero\n"
                  "  qnx-portmap --file symboles.txt --format markdown\n"
                  "  cat symbols.txt | qnx-portmap --stdin --format json\n"
                  "  qnx-portmap --verify-corpus\n",
        "symbols": "symboles a analyser",
        "file": "fichier contenant la liste des symboles",
        "stdin": "lire la liste sur l'entree standard",
        "format": "format de sortie (defaut : text)",
        "corpus": "repertoire du corpus fige (defaut : corpus du paquet)",
        "version_doc": "version de documentation visee",
        "previous_version": "version de reference pour la mise a niveau",
        "worklist": "n'affiche que la liste de travail de mise a niveau",
        "verify_corpus": "verifier le SHA-256 de chaque page du corpus et sortir",
        "stats": "afficher les statistiques du corpus et sortir",
        "fresh": "reconstruire le corpus depuis qnx.com avant l'analyse "
                 "(acces reseau ; jamais utilise par defaut)",
        "fresh_out": "repertoire du corpus reconstruit (defaut : <corpus>-fresh)",
        "fresh_cache": "repertoire du cache de telechargement (defaut : <fresh-out>/cache)",
        "fresh_max_pages": "limiter le nombre de pages par livre lors du rechargement",
        "fresh_only": "avec --fresh : reconstruire le corpus et sortir",
        "lang": "langue de sortie (defaut : en)",
        "quick": "mode rapide : telecharge seulement les index A-Z 8.0 et 7.1, "
                 "le guide de migration et les pages des symboles (environ 80 "
                 "requetes, quelques minutes) ; ne dit jamais \"absent\"",
        "quick_out": "repertoire du petit corpus du mode rapide (defaut : corpus-quick)",
    },
    "en": {
        "description": "Status of QNX symbols in the 8.0 documentation "
                       "(frozen corpus, offline by default).",
        "epilog": "Examples:\n"
                  "  qnx-portmap abort pthread_create bzero\n"
                  "  qnx-portmap --file symbols.txt --format markdown\n"
                  "  cat symbols.txt | qnx-portmap --stdin --format json\n"
                  "  qnx-portmap --verify-corpus\n",
        "symbols": "symbols to analyze",
        "file": "file containing the symbol list",
        "stdin": "read the list from standard input",
        "format": "output format (default: text)",
        "corpus": "frozen corpus directory (default: package corpus)",
        "version_doc": "target documentation version",
        "previous_version": "reference version for the upgrade",
        "worklist": "show only the upgrade worklist",
        "verify_corpus": "verify the SHA-256 of every corpus page and exit",
        "stats": "print corpus statistics and exit",
        "fresh": "rebuild the corpus from qnx.com before analysis "
                 "(network access; never used by default)",
        "fresh_out": "rebuilt corpus directory (default: <corpus>-fresh)",
        "fresh_cache": "download cache directory (default: <fresh-out>/cache)",
        "fresh_max_pages": "cap the number of pages per book during the reload",
        "fresh_only": "with --fresh: rebuild the corpus and exit",
        "lang": "output language (default: en)",
        "quick": "quick mode: download only the 8.0 and 7.1 A-Z indexes, the "
                 "migration guide and the pages of the symbols (about 80 "
                 "requests, a few minutes); never says \"absent\"",
        "quick_out": "directory of the small quick-mode corpus (default: corpus-quick)",
    },
}

# Console messages (outside the renderings) in the two output languages.
CLI_STRINGS = {
    "fr": {
        "no_symbols": "qnx-portmap: aucun symbole donne (argument, --file ou --stdin)\n",
        "unreadable_file": "qnx-portmap: fichier illisible : %s",
        "error": "qnx-portmap: %s\n",
        "dir_searched": "  repertoire recherche : %s\n",
        "hints": "  solutions : QX_PORTMAP_CORPUS=/chemin/vers/corpus "
                 "qnx-portmap ...\n"
                 "              qnx-portmap --corpus /chemin/vers/corpus ...\n",
        "corpus_root": "corpus : %s",
        "pages_checked": "pages verifiees : %d",
        "sha_pages": "SHA-256 des pages : %s",
        "fail_detail": "  ECHEC %s\n    attendu %s\n    obtenu  %s",
        "sha_sums": "SHA256SUMS : %s (%d fichiers)",
        "stats_root": "racine      : %s",
        "stats_pages": "pages       : %s",
        "stats_version": "  %-6s   : %d pages",
        "stats_consulted": "consulte le : %s",
        "stats_books": "livres      :",
        "fresh_online": "qnx-portmap: rechargement en ligne du corpus vers %s\n",
        "fresh_version": "  version %s\n",
        "fresh_failed": "qnx-portmap: %d page(s) non telechargee(s)\n",
        "fresh_built": "qnx-portmap: corpus reconstruit : %d pages\n",
        "quick_online": "qnx-portmap: mode rapide, telechargement vers %s\n",
        "quick_failed": "qnx-portmap: mode rapide impossible : %s\n",
        "quick_built": "qnx-portmap: petit corpus pret : %d pages en %s s\n",
    },
    "en": {
        "no_symbols": "qnx-portmap: no symbol given (argument, --file or --stdin)\n",
        "unreadable_file": "qnx-portmap: unreadable file: %s",
        "error": "qnx-portmap: %s\n",
        "dir_searched": "  directory searched: %s\n",
        "hints": "  hints: QX_PORTMAP_CORPUS=/path/to/corpus "
                 "qnx-portmap ...\n"
                 "              qnx-portmap --corpus /path/to/corpus ...\n",
        "corpus_root": "corpus: %s",
        "pages_checked": "pages checked: %d",
        "sha_pages": "page SHA-256: %s",
        "fail_detail": "  FAIL %s\n    expected %s\n    got      %s",
        "sha_sums": "SHA256SUMS: %s (%d files)",
        "stats_root": "root        : %s",
        "stats_pages": "pages       : %s",
        "stats_version": "  %-6s   : %d pages",
        "stats_consulted": "consulted on: %s",
        "stats_books": "books       :",
        "fresh_online": "qnx-portmap: online corpus reload to %s\n",
        "fresh_version": "  version %s\n",
        "fresh_failed": "qnx-portmap: %d page(s) not downloaded\n",
        "fresh_built": "qnx-portmap: corpus rebuilt: %d pages\n",
        "quick_online": "qnx-portmap: quick mode, downloading to %s\n",
        "quick_failed": "qnx-portmap: quick mode not possible: %s\n",
        "quick_built": "qnx-portmap: small corpus ready: %d pages in %s s\n",
    },
}


def _early_lang(argv):
    """Language asked for before the parsing, to translate ``--help`` too."""
    for i, arg in enumerate(argv):
        if arg == "--lang" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--lang="):
            return arg.split("=", 1)[1]
    return "en"


def build_parser(lang="en"):
    h = HELP_STRINGS[lang if lang in HELP_STRINGS else "fr"]
    p = argparse.ArgumentParser(
        prog="qnx-portmap",
        description=h["description"],
        epilog=h["epilog"])
    p.add_argument("symbols", nargs="*", help=h["symbols"])
    p.add_argument("--file", "-f", help=h["file"])
    p.add_argument("--stdin", action="store_true", help=h["stdin"])
    p.add_argument("--format", choices=("text", "json", "markdown"), default="text",
                   help=h["format"])
    p.add_argument("--corpus", default=None,
                   help=h["corpus"])
    p.add_argument("--lang", choices=("fr", "en"), default="en",
                   help=h["lang"])
    p.add_argument("--version-doc", default="8.0", help=h["version_doc"])
    p.add_argument("--previous-version", default="7.1",
                   help=h["previous_version"])
    p.add_argument("--worklist", action="store_true",
                   help=h["worklist"])
    p.add_argument("--verify-corpus", action="store_true",
                   help=h["verify_corpus"])
    p.add_argument("--stats", action="store_true",
                   help=h["stats"])
    p.add_argument("--fresh", action="store_true",
                   help=h["fresh"])
    p.add_argument("--fresh-out", default=None,
                   help=h["fresh_out"])
    p.add_argument("--fresh-cache", default=None,
                   help=h["fresh_cache"])
    p.add_argument("--fresh-max-pages", type=int, default=None,
                   help=h["fresh_max_pages"])
    p.add_argument("--fresh-only", action="store_true",
                   help=h["fresh_only"])
    p.add_argument("--quick", action="store_true", help=h["quick"])
    p.add_argument("--quick-out", default="corpus-quick", help=h["quick_out"])
    return p


def _collect_symbols(args, s):
    symbols = list(args.symbols)
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                symbols.extend(read_symbols(fh.read()))
        except OSError as exc:
            raise SystemExit(s["unreadable_file"] % exc)
    if args.stdin:
        symbols.extend(read_symbols(sys.stdin.read()))
    out = []
    for sym in symbols:
        sym = sym.strip()
        if sym and sym not in out:
            out.append(sym)
    return out


def _do_fresh(args, corpus_dir, s):
    """Reloads the corpus from qnx.com. The frozen corpus is never touched."""
    from .refresh import (BOOKS, BOOKS_71, Downloader, build_corpus_from_cache)

    out_dir = args.fresh_out or (os.path.abspath(corpus_dir) + "-fresh")
    cache_dir = args.fresh_cache or os.path.join(out_dir, "cache")
    sys.stderr.write(s["fresh_online"] % out_dir)
    dl = Downloader(cache_dir)
    for version, books in (("8.0", BOOKS), ("7.1", BOOKS_71)):
        sys.stderr.write(s["fresh_version"] % version)
        dl.crawl(version, books, args.fresh_max_pages,
                 progress=lambda line: sys.stderr.write("  %s\n" % line))
    if dl.failed:
        sys.stderr.write(s["fresh_failed"] % len(dl.failed))
        for url, err in dl.failed[:5]:
            sys.stderr.write("  %s : %s\n" % (url, err))
    manifest = build_corpus_from_cache(cache_dir, out_dir)
    sys.stderr.write(s["fresh_built"] % manifest["pages_total"])
    return out_dir


def _do_quick(args, symbols, s):
    """Builds the small corpus of the quick mode. Returns its directory."""
    from .quick import QuickError, build_quick_corpus

    out_dir = os.path.abspath(args.quick_out)
    sys.stderr.write(s["quick_online"] % out_dir)
    try:
        manifest = build_quick_corpus(
            out_dir, symbols, version=args.version_doc,
            previous=args.previous_version,
            progress=lambda line: sys.stderr.write("  %s\n" % line))
    except (QuickError, OSError) as exc:     # network down, directory not writable
        sys.stderr.write(s["quick_failed"] % exc)
        return None
    sys.stderr.write(s["quick_built"] % (manifest["pages_total"],
                                         manifest["quick"]["seconds"]))
    return out_dir


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser(_early_lang(argv)).parse_args(argv)
    s = CLI_STRINGS[args.lang]
    corpus_dir = args.corpus or default_corpus_dir()
    quick_symbols = None
    if args.quick:
        quick_symbols = _collect_symbols(args, s)
        if not quick_symbols:
            sys.stderr.write(s["no_symbols"])
            return 2
        corpus_dir = _do_quick(args, quick_symbols, s)
        if corpus_dir is None:
            return 2
    elif args.fresh:
        corpus_dir = _do_fresh(args, corpus_dir, s)
        if args.fresh_only:
            return 0
    try:
        corpus = Corpus(corpus_dir, lang=args.lang)
    except CorpusError as exc:
        sys.stderr.write(s["error"] % exc)
        if not os.path.isfile(os.path.join(corpus_dir, "MANIFEST.json")):
            sys.stderr.write(s["dir_searched"] % corpus_dir)
            sys.stderr.write(s["hints"])
        return 2

    if args.verify_corpus:
        res = corpus.verify()
        sums = corpus.verify_sha256sums()
        print(s["corpus_root"] % corpus.root)
        print(s["pages_checked"] % res["checked"])
        print(s["sha_pages"] % ("OK" if res["ok"] else "ECHEC" if args.lang == "fr"
                                else "FAIL"))
        for url, expected, got in res["failed"][:20]:
            print(s["fail_detail"] % (url, expected, got))
        print(s["sha_sums"] % ("OK" if sums["ok"] else "ECHEC" if args.lang == "fr"
                               else "FAIL", sums["checked"]))
        for rel, expected, got in sums["failed"][:20]:
            print(s["fail_detail"] % (rel, expected, got))
        return 0 if (res["ok"] and sums["ok"]) else 1

    if args.stats:
        man = corpus.manifest
        print(s["stats_root"] % corpus.root)
        print(s["stats_pages"] % man.get("pages_total"))
        for v, n in sorted(man.get("pages_by_version", {}).items()):
            print(s["stats_version"] % (v, n))
        print(s["stats_consulted"] % man.get("consulted"))
        print(s["stats_books"])
        for book, n in sorted(man.get("pages_by_book", {}).items()):
            print("  %-42s %d" % (book, n))
        return 0

    symbols = quick_symbols or _collect_symbols(args, s)
    if not symbols:
        sys.stderr.write(s["no_symbols"])
        return 2

    classifier = Classifier(corpus, version=args.version_doc,
                            previous=args.previous_version, lang=args.lang)
    results = classifier.classify(symbols)
    if is_quick(corpus):
        apply_quick_limits(results, version=args.version_doc,
                           previous=args.previous_version, lang=args.lang)
    worklist = Classifier.worklist(results)

    if args.format == "json":
        sys.stdout.write(render_json(results, worklist, corpus,
                                     version=args.version_doc,
                                     previous=args.previous_version))
    elif args.format == "markdown":
        sys.stdout.write(render_markdown(results, worklist, corpus,
                                         version=args.version_doc,
                                         previous=args.previous_version,
                                         lang=args.lang))
    else:
        if args.worklist:
            sys.stdout.write(render_text(results, worklist, corpus,
                                         version=args.version_doc,
                                         previous=args.previous_version,
                                         lang=args.lang))
        else:
            sys.stdout.write(render_text(results, worklist, corpus,
                                         version=args.version_doc,
                                         previous=args.previous_version,
                                         lang=args.lang))

    # exit code: 0 if everything is fine, 1 if a symbol is absent or unknown
    from .classify import ABSENT, UNKNOWN
    return 1 if any(r.status in (ABSENT, UNKNOWN) for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
