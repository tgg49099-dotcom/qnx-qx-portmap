"""Interface en ligne de commande de QX PORTMAP.

QX PORTMAP repond a une seule question : etant donne une liste de symboles
QNX, ou en est chacun dans la documentation officielle 8.0 ?

Par defaut, l'outil ne touche pas au reseau : il lit le corpus de
documentation fige dans le depot.
"""

import argparse
import os
import sys

from .classify import Classifier
from .corpus import Corpus, CorpusError, default_corpus_dir, read_symbols
from .report import render_json, render_markdown, render_text


def build_parser():
    p = argparse.ArgumentParser(
        prog="qnx-portmap",
        description="Etat des symboles QNX dans la documentation 8.0 "
                    "(corpus fige, hors ligne par defaut).",
        epilog="Exemples :\n"
               "  qnx-portmap abort pthread_create bzero\n"
               "  qnx-portmap --file symboles.txt --format markdown\n"
               "  cat symbols.txt | qnx-portmap --stdin --format json\n"
               "  qnx-portmap --verify-corpus\n")
    p.add_argument("symbols", nargs="*", help="symboles a analyser")
    p.add_argument("--file", "-f", help="fichier contenant la liste des symboles")
    p.add_argument("--stdin", action="store_true", help="lire la liste sur l'entree standard")
    p.add_argument("--format", choices=("text", "json", "markdown"), default="text",
                   help="format de sortie (defaut : text)")
    p.add_argument("--corpus", default=None,
                   help="repertoire du corpus fige (defaut : corpus du paquet)")
    p.add_argument("--version-doc", default="8.0", help="version de documentation visee")
    p.add_argument("--previous-version", default="7.1",
                   help="version de reference pour la mise a niveau")
    p.add_argument("--worklist", action="store_true",
                   help="n'afficher que la liste de travail de mise a niveau")
    p.add_argument("--verify-corpus", action="store_true",
                   help="verifier le SHA-256 de chaque page du corpus et sortir")
    p.add_argument("--stats", action="store_true",
                   help="afficher les statistiques du corpus et sortir")
    p.add_argument("--fresh", action="store_true",
                   help="reconstruire le corpus depuis qnx.com avant l'analyse "
                        "(acces reseau ; jamais utilise par defaut)")
    p.add_argument("--fresh-out", default=None,
                   help="repertoire du corpus reconstruit (defaut : <corpus>-fresh)")
    p.add_argument("--fresh-cache", default=None,
                   help="repertoire du cache de telechargement (defaut : <fresh-out>/cache)")
    p.add_argument("--fresh-max-pages", type=int, default=None,
                   help="limiter le nombre de pages par livre lors du rechargement")
    p.add_argument("--fresh-only", action="store_true",
                   help="avec --fresh : reconstruire le corpus et sortir")
    return p


def _collect_symbols(args):
    symbols = list(args.symbols)
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                symbols.extend(read_symbols(fh.read()))
        except OSError as exc:
            raise SystemExit("qnx-portmap: fichier illisible : %s" % exc)
    if args.stdin:
        symbols.extend(read_symbols(sys.stdin.read()))
    out = []
    for sym in symbols:
        sym = sym.strip()
        if sym and sym not in out:
            out.append(sym)
    return out


def _do_fresh(args, corpus_dir):
    """Recharge le corpus depuis qnx.com. Le corpus fige n'est pas touche."""
    from .refresh import (BOOKS, BOOKS_71, Downloader, build_corpus_from_cache)

    out_dir = args.fresh_out or (os.path.abspath(corpus_dir) + "-fresh")
    cache_dir = args.fresh_cache or os.path.join(out_dir, "cache")
    sys.stderr.write("qnx-portmap: rechargement en ligne du corpus vers %s\n" % out_dir)
    dl = Downloader(cache_dir)
    for version, books in (("8.0", BOOKS), ("7.1", BOOKS_71)):
        sys.stderr.write("  version %s\n" % version)
        dl.crawl(version, books, args.fresh_max_pages,
                 progress=lambda line: sys.stderr.write("  %s\n" % line))
    if dl.failed:
        sys.stderr.write("qnx-portmap: %d page(s) non telechargee(s)\n" % len(dl.failed))
        for url, err in dl.failed[:5]:
            sys.stderr.write("  %s : %s\n" % (url, err))
    manifest = build_corpus_from_cache(cache_dir, out_dir)
    sys.stderr.write("qnx-portmap: corpus reconstruit : %d pages\n"
                     % manifest["pages_total"])
    return out_dir


def main(argv=None):
    args = build_parser().parse_args(argv)
    corpus_dir = args.corpus or default_corpus_dir()
    if args.fresh:
        corpus_dir = _do_fresh(args, corpus_dir)
        if args.fresh_only:
            return 0
    try:
        corpus = Corpus(corpus_dir)
    except CorpusError as exc:
        sys.stderr.write("qnx-portmap: %s\n" % exc)
        return 2

    if args.verify_corpus:
        res = corpus.verify()
        sums = corpus.verify_sha256sums()
        print("corpus : %s" % corpus.root)
        print("pages verifiees : %d" % res["checked"])
        print("SHA-256 des pages : %s" % ("OK" if res["ok"] else "ECHEC"))
        for url, expected, got in res["failed"][:20]:
            print("  ECHEC %s\n    attendu %s\n    obtenu  %s" % (url, expected, got))
        print("SHA256SUMS : %s (%d fichiers)" % ("OK" if sums["ok"] else "ECHEC", sums["checked"]))
        for rel, expected, got in sums["failed"][:20]:
            print("  ECHEC %s\n    attendu %s\n    obtenu  %s" % (rel, expected, got))
        return 0 if (res["ok"] and sums["ok"]) else 1

    if args.stats:
        man = corpus.manifest
        print("racine      : %s" % corpus.root)
        print("pages       : %s" % man.get("pages_total"))
        for v, n in sorted(man.get("pages_by_version", {}).items()):
            print("  %-6s   : %d pages" % (v, n))
        print("consulte le : %s" % man.get("consulted"))
        print("livres      :")
        for book, n in sorted(man.get("pages_by_book", {}).items()):
            print("  %-42s %d" % (book, n))
        return 0

    symbols = _collect_symbols(args)
    if not symbols:
        sys.stderr.write("qnx-portmap: aucun symbole donne "
                         "(argument, --file ou --stdin)\n")
        return 2

    classifier = Classifier(corpus, version=args.version_doc, previous=args.previous_version)
    results = classifier.classify(symbols)
    worklist = Classifier.worklist(results)

    if args.format == "json":
        sys.stdout.write(render_json(results, worklist, corpus,
                                     version=args.version_doc,
                                     previous=args.previous_version))
    elif args.format == "markdown":
        sys.stdout.write(render_markdown(results, worklist, corpus,
                                          version=args.version_doc,
                                          previous=args.previous_version))
    else:
        if args.worklist:
            sys.stdout.write(render_text(results, worklist, corpus,
                                         version=args.version_doc,
                                         previous=args.previous_version))
        else:
            sys.stdout.write(render_text(results, worklist, corpus,
                                         version=args.version_doc,
                                         previous=args.previous_version))

    # code de sortie : 0 si tout va bien, 1 si un symbole est absent ou inconnu
    from .classify import ABSENT, UNKNOWN
    return 1 if any(r.status in (ABSENT, UNKNOWN) for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
