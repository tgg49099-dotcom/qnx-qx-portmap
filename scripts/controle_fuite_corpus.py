#!/usr/bin/env python3
"""Anti-leak control: the publishable repository contains no QNX page.

The control compares, by SHA-256:

1. every file of the publishable tree with the list of the SHA-256 of the
   pages of the reference corpus (``corpus/index/pages.jsonl``);
2. every file of the publishable tree with the list of the SHA-256 of the
   files stored in the corpus (``corpus/SHA256SUMS``, compressed pages);
3. the decompressed content of every gzip file of the publishable tree with
   the SHA-256 of the pages;
4. every git object of the publishable tree (raw content and decompressed
   content) with the SHA-256 of the pages.

It adds three controls stronger than the plain comparison of fingerprints:

5. the line by line overlap: which lines of the publishable tree appear word
   for word in the corpus, and of how many bytes;
6. the overlap by fragments: for every file, the longest verbatim fragment
   present in the corpus (longest common substring search), and the total
   number of QNX bytes the file contains;
7. the copy budget: no file of the publishable tree must contain more than
   4,000 bytes of verbatim QNX text.

Usage:
    python3 scripts/controle_fuite_corpus.py \
        --tree . --corpus /work/qnx-portmap-corpus-local/corpus

Exit code: 0 if no match, 1 otherwise, 2 if the reference corpus cannot be
found (the control is then not possible).
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
LINE_MIN = 40          # minimal length of a line kept as verbatim
COPY_BUDGET = 4000     # maximum bytes of verbatim QNX text per file
# Tags of the Oxygen (DITA-OT) markup of the QNX pages: a file that contains
# them is analysed fragment by fragment, even if none of its lines is
# identical to a line of the corpus.
QNX_MARKERS = ("<article", "role=\"treeitem\"", "apiname", "varname",
               "<var class", "<span class")
# Directories whose every file is analysed fragment by fragment, even if it
# carries no Oxygen tag: the test extracts and the citation files of the
# J4 and J5 measurements (docs/mesure-J4/citations-*.txt,
# docs/mesure-J5/citations-*.txt) contain QNX text without markup.
FRAGMENT_DIRS = ("tests/fixtures", "docs/mesure-J4", "docs/mesure-J5")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def publishable_files(tree):
    """Files of the publishable tree (outside .git, caches, builds)."""
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
    """Reference fingerprints: pages (decompressed) and stored files."""
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
    """Distinct long lines of the corpus, with their length."""
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
    """All the distinct long lines of the corpus, in order."""
    return list(corpus_lines(corpus_dir, index_path).keys())


def corpus_blob(corpus_dir, index_path):
    """Text of every page of the corpus, concatenated (one single string)."""
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
    """Longest fragment of ``line`` present word for word in the corpus.

    The window of the middle is probed first, then the beginning of the
    line; at every step the window is reduced by one character.
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
    """Content of every blob object of the repository (raw, then decompressed)."""
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
