#!/usr/bin/env python3
"""Genere (ou verifie) ``MANIFESTE-PUBLIE.txt``.

Le manifeste liste chaque fichier publiable du depot : chemin, taille en
octets, SHA-256. Il est regenere apres chaque changement de l'arbre
publiable.

Usage :
    python3 scripts/manifeste_publie.py            # ecrit le manifeste
    python3 scripts/manifeste_publie.py --check    # verifie sans ecrire
    python3 scripts/manifeste_publie.py --out AUTRE-FICHIER

Code de sortie : 0 si tout va bien, 1 si le manifeste est obsolete.
"""

import argparse
import hashlib
import os
import sys
import time

IGNORED_DIRS = (".git", "__pycache__", "build", "dist", "qnx_portmap.egg-info",
                ".pytest_cache")
IGNORED_SUFFIX = (".pyc", ".pyo", ".orig", ".rej")
MANIFEST_NAME = "MANIFESTE-PUBLIE.txt"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def publishable_files(tree, manifest_path):
    out = []
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for fn in sorted(filenames):
            if fn.endswith(IGNORED_SUFFIX):
                continue
            full = os.path.join(dirpath, fn)
            if os.path.abspath(full) == os.path.abspath(manifest_path):
                continue          # le manifeste ne se liste pas lui-meme
            rel = os.path.relpath(full, tree).replace(os.sep, "/")
            out.append((rel, full))
    return sorted(out)


def render(tree, files):
    total = 0
    rows = []
    for rel, full in files:
        size = os.path.getsize(full)
        total += size
        rows.append((rel, size, sha256_file(full)))
    biggest = sorted(rows, key=lambda r: -r[1])[:3]
    out = []
    out.append("MANIFESTE DES FICHIERS PUBLIABLES - QX PORTMAP")
    out.append("")
    out.append("Arbre          : %s" % tree)
    out.append("Genere le      : %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    out.append("Fichiers       : %d" % len(rows))
    out.append("Taille totale  : %d octets" % total)
    out.append("")
    out.append("Les 3 plus gros fichiers :")
    for rel, size, _digest in biggest:
        out.append("  %9d octets  %s" % (size, rel))
    out.append("")
    out.append("Detail (chemin, taille en octets, SHA-256) :")
    out.append("")
    for rel, size, digest in rows:
        out.append("%s\t%d\t%s" % (rel, size, digest))
    out.append("")
    return "\n".join(out), len(rows), total, biggest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tree", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), help="arbre publiable")
    ap.add_argument("--out", default=None, help="fichier manifeste")
    ap.add_argument("--check", action="store_true",
                    help="verifie que le manifeste est a jour (n'ecrit rien)")
    args = ap.parse_args()

    tree = os.path.abspath(args.tree)
    out_path = os.path.abspath(args.out or os.path.join(tree, MANIFEST_NAME))
    files = publishable_files(tree, out_path)
    text, count, total, biggest = render(tree, files)

    if args.check:
        if not os.path.isfile(out_path):
            print("MANIFESTE-PUBLIE.txt absent : %s" % out_path)
            return 1
        with open(out_path, encoding="utf-8") as fh:
            current = fh.read()
        # on compare la partie "Detail", insensible a la date de generation
        def body(t):
            marker = "Detail (chemin, taille en octets, SHA-256) :"
            return t.split(marker, 1)[1] if marker in t else ""
        if body(current) != body(text):
            print("MANIFESTE-PUBLIE.txt est obsolete : regenerez-le.")
            return 1
        print("MANIFESTE-PUBLIE.txt est a jour : %d fichiers, %d octets."
              % (count, total))
        return 0

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("MANIFESTE-PUBLIE.txt ecrit : %s" % out_path)
    print("  fichiers      : %d" % count)
    print("  taille totale : %d octets" % total)
    for rel, size, _digest in biggest:
        print("  plus gros     : %9d octets  %s" % (size, rel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
