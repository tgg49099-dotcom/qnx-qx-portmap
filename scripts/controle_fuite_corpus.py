#!/usr/bin/env python3
"""Controle anti-fuite : le depot publiable ne contient aucune page QNX.

Le controle compare, par SHA-256 :

1. chaque fichier de l'arbre publiable avec la liste des SHA-256 des pages
   du corpus de reference (``corpus/index/pages.jsonl``) ;
2. chaque fichier de l'arbre publiable avec la liste des SHA-256 des fichiers
   stockes dans le corpus (``corpus/SHA256SUMS``, pages compressees) ;
3. le contenu decompresse de chaque fichier gzip de l'arbre publiable avec
   les SHA-256 des pages ;
4. chaque objet git de l'arbre publiable (contenu brut et contenu decompresse)
   avec les SHA-256 des pages.

Il ajoute trois controles plus forts que la simple comparaison d'empreintes :

5. le recouvrement ligne a ligne : quelles lignes de l'arbre publiable
   apparaissent mot pour mot dans le corpus, et de combien d'octets ;
6. le recouvrement par fragments : pour chaque fichier, le plus long fragment
   verbatim present dans le corpus (recherche par plus longue sous-chaine
   commune), et le nombre total d'octets QNX que le fichier contient ;
7. le budget de copie : aucun fichier de l'arbre publiable ne doit contenir
   plus de 4 000 octets de texte QNX verbatim.

Usage :
    python3 scripts/controle_fuite_corpus.py \
        --tree . --corpus /work/qnx-portmap-corpus-local/corpus

Code de sortie : 0 si aucune correspondance, 1 sinon, 2 si le corpus de
reference est introuvable (le controle n'est alors pas realisable).
"""

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

IGNORED_DIRS = (".git", "__pycache__", "build", "dist", ".pylocal", ".npm",
                "qnx_portmap.egg-info")
IGNORED_SUFFIX = (".pyc", ".pyo")
LINE_MIN = 40          # longueur minimale d'une ligne retenue comme verbatim
COPY_BUDGET = 4000     # octets de texte QNX verbatim maximum par fichier
# Balises du balisage Oxygen (DITA-OT) des pages QNX : un fichier qui les
# contient est analyse fragment par fragment, meme si aucune de ses lignes
# n'est identique a une ligne du corpus.
QNX_MARKERS = ("<article", "role=\"treeitem\"", "apiname", "varname",
               "<var class", "<span class")
# Dossiers dont chaque fichier est analyse fragment par fragment, meme
# s'il ne porte aucune balise Oxygen : les extraits de test et les fichiers
# de citations des mesures J4 et J5 (docs/mesure-J4/citations-*.txt,
# docs/mesure-J5/citations-*.txt) contiennent du texte QNX sans balisage.
FRAGMENT_DIRS = ("tests/fixtures", "docs/mesure-J4", "docs/mesure-J5")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def publishable_files(tree):
    """Fichiers de l'arbre publiable (hors .git, caches, builds)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for fn in sorted(filenames):
            if fn.endswith(IGNORED_SUFFIX):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, tree).replace(os.sep, "/")
            out.append((rel, full))
    return out


def load_corpus_hashes(corpus_dir):
    """Empreintes de reference : pages (decompressees) et fichiers stockes."""
    index = os.path.join(corpus_dir, "index", "pages.jsonl")
    sums = os.path.join(corpus_dir, "SHA256SUMS")
    if not os.path.isfile(index) or not os.path.isfile(sums):
        return None
    pages = set()
    with open(index, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                pages.add(json.loads(line)["sha256"])
    stored = set()
    with open(sums, encoding="utf-8") as fh:
        for line in fh:
            digest, _, _rel = line.strip().partition("  ")
            if digest:
                stored.add(digest)
    return {"pages": pages, "stored": stored}


def corpus_lines(corpus_dir, index_path):
    """Lignes longues distinctes du corpus, avec leur longueur."""
    lines = {}
    with open(index_path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            path = os.path.join(corpus_dir, rec["file"])
            if not os.path.isfile(path):
                continue
            try:
                with gzip.open(path, "rb") as gz:
                    text = gz.read().decode("utf-8", "replace")
            except (OSError, EOFError):
                continue
            for line in text.splitlines():
                line = line.strip()
                if len(line) >= LINE_MIN:
                    lines.setdefault(line, len(line))
    return lines


def corpus_line_list(corpus_dir, index_path):
    """Toutes les lignes longues distinctes du corpus, dans l'ordre."""
    return list(corpus_lines(corpus_dir, index_path).keys())


def corpus_blob(corpus_dir, index_path):
    """Texte de toutes les pages du corpus, concatene (une seule chaine)."""
    parts = []
    with open(index_path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            path = os.path.join(corpus_dir, rec["file"])
            if not os.path.isfile(path):
                continue
            try:
                with gzip.open(path, "rb") as gz:
                    parts.append(gz.read().decode("utf-8", "replace"))
            except (OSError, EOFError):
                continue
    blob = "\n".join(parts)
    del parts
    return blob


def longest_verbatim_run(line, corpus_line_list):
    """Plus long fragment de ``line`` present mot pour mot dans le corpus.

    On sonde la fenetre du milieu puis le debut de la ligne ; a chaque
    occurrence trouvee dans une ligne du corpus, on etend la correspondance
    a gauche et a droite tant que les caracteres coincident. Le resultat ne
    depend que du corpus et de la ligne : il est reproductible.
    """
    n = len(line)
    if n < LINE_MIN:
        return 0
    mid = (n - LINE_MIN) // 2
    probes = []
    for start in (mid, 0):
        if start not in probes:
            probes.append(start)
    best = 0
    for start in probes:
        window = line[start:start + LINE_MIN]
        for corpus_line in corpus_line_list:
            pos = corpus_line.find(window)
            while pos != -1:
                left = 0
                while (start - left - 1 >= 0 and pos - left - 1 >= 0
                       and line[start - left - 1] == corpus_line[pos - left - 1]):
                    left += 1
                right = 0
                while (start + LINE_MIN + right < n
                       and pos + LINE_MIN + right < len(corpus_line)
                       and line[start + LINE_MIN + right]
                       == corpus_line[pos + LINE_MIN + right]):
                    right += 1
                best = max(best, left + LINE_MIN + right)
                if best >= n:
                    return best
                pos = corpus_line.find(window, pos + 1)
        if best >= n:
            break
    return best


def git_blobs(repo):
    """Contenu de tous les objets blob du depot (brut, puis decompresse)."""
    blobs = []
    try:
        names = subprocess.run(
            ["git", "-C", repo, "cat-file", "--batch-all-objects",
             "--batch-check=%(objectname) %(objecttype)"],
            capture_output=True, text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return blobs
    for line in names:
        parts = line.split()
        if len(parts) != 2 or parts[1] != "blob":
            continue
        oid = parts[0]
        data = subprocess.run(["git", "-C", repo, "cat-file", "blob", oid],
                              capture_output=True, check=True).stdout
        blobs.append((oid, data))
    return blobs


def has_qnx_marker(text):
    return any(marker in text for marker in QNX_MARKERS)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tree", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), help="arbre publiable a controler")
    ap.add_argument("--corpus", default=os.environ.get(
        "QX_PORTMAP_CORPUS", "/work/qnx-portmap-corpus-local/corpus"),
        help="corpus de reference (archive locale)")
    ap.add_argument("--repo", default=None,
                    help="depot git a controler (defaut : <tree> si c'est un depot)")
    ap.add_argument("--verbose", action="store_true", help="detaille les correspondances")
    args = ap.parse_args()

    tree = os.path.abspath(args.tree)
    corpus_dir = os.path.abspath(args.corpus)
    repo = args.repo or tree
    started = time.time()

    print("CONTROLE ANTI-FUITE DU CORPUS QNX")
    print("  date              : %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("  arbre publiable   : %s" % tree)
    print("  corpus de ref.    : %s" % corpus_dir)

    index_path = os.path.join(corpus_dir, "index", "pages.jsonl")
    hashes = load_corpus_hashes(corpus_dir)
    if hashes is None:
        print("  ERREUR : corpus de reference introuvable (%s)" % corpus_dir)
        print("  Le controle n'est pas realisable sans les empreintes des pages.")
        print("  Reconstruire le corpus : bash scripts/bootstrap_corpus.sh --out <dir>")
        return 2
    print("  pages de reference: %d (empreintes de contenu)" % len(hashes["pages"]))
    print("  fichiers stockes  : %d (empreintes gzip)" % len(hashes["stored"]))
    print()

    files = publishable_files(tree)
    page_matches = []
    file_matches = []
    gzip_matches = []
    total_bytes = 0
    texts = {}
    for rel, full in files:
        with open(full, "rb") as fh:
            data = fh.read()
        total_bytes += len(data)
        digest = sha256_bytes(data)
        if digest in hashes["pages"]:
            page_matches.append((rel, "page QNX identique"))
        if digest in hashes["stored"]:
            file_matches.append((rel, "fichier du corpus identique"))
        if data[:2] == b"\x1f\x8b":
            try:
                plain = gzip.decompress(data)
            except OSError:
                plain = b""
            if plain and sha256_bytes(plain) in hashes["pages"]:
                gzip_matches.append((rel, "page QNX compressee a l'identique"))
        try:
            texts[rel] = data.decode("utf-8")
        except UnicodeDecodeError:
            texts[rel] = None

    print("1. SHA-256 des fichiers de l'arbre publiable")
    print("   fichiers analyses          : %d (%d octets)" % (len(files), total_bytes))
    print("   correspondances page QNX   : %d" % len(page_matches))
    print("   correspondances fichier    : %d" % len(file_matches))
    for rel, why in page_matches + file_matches:
        print("     FUITE %s : %s" % (rel, why))
    print()

    print("2. Contenu decompresse des fichiers gzip de l'arbre")
    print("   correspondances page QNX   : %d" % len(gzip_matches))
    for rel, why in gzip_matches:
        print("     FUITE %s : %s" % (rel, why))
    print()

    print("3. Objets git du depot publiable")
    blobs = git_blobs(repo)
    blob_hits = []
    for oid, data in blobs:
        if sha256_bytes(data) in hashes["pages"] or sha256_bytes(data) in hashes["stored"]:
            blob_hits.append((oid, "contenu brut"))
        if data[:2] == b"\x1f\x8b":
            try:
                plain = gzip.decompress(data)
            except OSError:
                plain = b""
            if plain and sha256_bytes(plain) in hashes["pages"]:
                blob_hits.append((oid, "contenu decompresse"))
    print("   objets blob                : %d" % len(blobs))
    print("   correspondances            : %d" % len(blob_hits))
    for oid, why in blob_hits:
        print("     FUITE %s : %s" % (oid, why))
    print()

    print("4. Recouvrement ligne a ligne (lignes de %d caracteres ou plus)" % LINE_MIN)
    corpus_line_set = corpus_lines(corpus_dir, index_path)
    print("   lignes distinctes du corpus : %d" % len(corpus_line_set))
    line_hits = {}
    for rel, full in files:
        text = texts.get(rel)
        if text is None:
            continue
        hits = []
        for line in text.splitlines():
            line = line.strip()
            if len(line) >= LINE_MIN and line in corpus_line_set:
                hits.append(line)
        if hits:
            line_hits[rel] = hits
    print("   fichiers avec lignes identiques : %d" % len(line_hits))
    print("   lignes identiques au corpus     : %d"
          % sum(len(v) for v in line_hits.values()))
    for rel, hits in sorted(line_hits.items()):
        print("     %-46s %2d ligne(s) %5d octet(s)"
              % (rel, len(hits), sum(len(h) for h in hits)))
        if args.verbose:
            for line in hits:
                print("        > %s" % line[:120])
    print()

    print("5. Recouvrement par fragments (plus longue sous-chaine commune)")
    blob = corpus_blob(corpus_dir, index_path)
    print("   texte du corpus             : %d caracteres" % len(blob))
    corpus_line_list = list(corpus_line_set.keys())
    whole_file_hits = []
    fragment_bytes = {}
    fragment_detail = {}
    for rel, full in files:
        text = texts.get(rel)
        if not text:
            continue
        stripped = text.strip()
        if stripped and len(stripped) >= LINE_MIN and blob.find(stripped) != -1:
            whole_file_hits.append((rel, len(stripped)))
        interesting = rel.startswith(FRAGMENT_DIRS) or has_qnx_marker(text)
        if not interesting:
            continue
        total = 0
        best = 0
        detail = []
        for line in text.splitlines():
            line = line.strip()
            if len(line) < LINE_MIN:
                continue
            run = longest_verbatim_run(line, corpus_line_list)
            if run:
                total += run
                best = max(best, run)
                detail.append((run, line))
        if total:
            fragment_bytes[rel] = total
            fragment_detail[rel] = (best, detail)
    print("   fichiers dont le contenu entier est dans le corpus : %d"
          % len(whole_file_hits))
    for rel, size in whole_file_hits:
        print("     FUITE %s : %d octets verbatim" % (rel, size))
    print("   fichiers analyses fragment par fragment            : %d"
          % len(fragment_bytes))
    print("   octets de texte QNX verbatim (fragments) total    : %d"
          % sum(fragment_bytes.values()))
    for rel, total in sorted(fragment_bytes.items()):
        best, detail = fragment_detail[rel]
        print("     %-46s %5d octet(s), plus long fragment %5d octet(s)"
              % (rel, total, best))
        if args.verbose:
            for run, line in sorted(detail, reverse=True)[:5]:
                print("        > [%d] %s" % (run, line[:110]))
    print()

    print("6. Budget de copie (%d octets de texte QNX verbatim par fichier)"
          % COPY_BUDGET)
    over_budget = []
    for rel in sorted(set(list(line_hits) + list(fragment_bytes))):
        exact = sum(len(h) for h in line_hits.get(rel, []))
        frag = fragment_bytes.get(rel, 0)
        worst = max(exact, frag)
        if worst > COPY_BUDGET:
            over_budget.append((rel, exact, frag, worst))
    print("   fichiers avec du texte verbatim QNX : %d"
          % len(set(list(line_hits) + list(fragment_bytes))))
    print("   octets verbatim QNX dans l'arbre   : %d"
          % sum(max(sum(len(h) for h in line_hits.get(rel, [])),
                    fragment_bytes.get(rel, 0))
                for rel in set(list(line_hits) + list(fragment_bytes))))
    print("   fichiers au-dessus du budget        : %d" % len(over_budget))
    for rel, exact, frag, worst in over_budget:
        print("     TROP %s : %d octets (lignes %d, fragments %d)"
              % (rel, worst, exact, frag))
    print()

    leaks = (len(page_matches) + len(file_matches) + len(gzip_matches)
             + len(blob_hits) + len(whole_file_hits))
    if leaks == 0 and not over_budget:
        print("RESULTAT : 0 correspondance. L'arbre publiable ne contient aucune")
        print("           page de la documentation QNX.")
        print("Duree du controle : %.1f s" % (time.time() - started))
        return 0
    print("RESULTAT : %d correspondance(s) detectee(s)." % (leaks + len(over_budget)))
    return 1


if __name__ == "__main__":
    sys.exit(main())
