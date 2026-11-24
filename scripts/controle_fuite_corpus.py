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
    """Text of every page of the corpus, concatenated (one single string).

    The pages are joined by chunks of about 4 MB, so the temporary strings
    are released before the final concatenation.  The result is the same
    string as before, but the peak of memory is lower.
    """
    chunks = []
    chunk = []
    chunk_len = 0
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
            chunk.append(text)
            chunk_len += len(text)
            if chunk_len >= 4 * 1024 * 1024:
                chunks.append("\n".join(chunk))
                chunk = []
                chunk_len = 0
    if chunk:
        chunks.append("\n".join(chunk))
    blob = "\n".join(chunks)
    del chunks
    return blob


def longest_verbatim_run_reference(line, corpus_line_list):
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


class CorpusText(object):
    """The distinct long lines of the corpus joined by newlines, searched at once.

    No corpus line and no probed line holds a newline (both come from
    ``splitlines``), so a 40-character window never spans two corpus lines and
    the extension to the left and to the right stops at the newline exactly
    where it stopped at the edges of one corpus line. The result is therefore
    the one of ``longest_verbatim_run_reference``, without one ``find`` per
    corpus line (measured on 23 November 2026: the control no longer fits in
    230 s with the per-line loop).
    """

    # Pieces of GRAM characters, taken every STEP characters inside each corpus
    # line: a window of LINE_MIN characters found in a corpus line always holds
    # one of them whole (STEP + GRAM - 1 == LINE_MIN), so a window none of
    # whose pieces is known cannot be in the corpus and is not searched (a
    # collision only costs one useless search; the result never changes).
    GRAM = 30
    STEP = LINE_MIN - GRAM + 1

    # The prefilter is a Bloom filter of 64 MiB, not a set of the 27 684 783
    # distinct pieces of the corpus (1.70 GB measured on 19 November 2026).
    # A Bloom filter has no false negative: every piece of the corpus is
    # inserted in it, so a window that is in the corpus is always searched.
    # A false positive only costs one useless search in the same text, so the
    # control can be stricter than before, never more lenient.  The searched
    # text is built in ONE allocation ("\n".join): the concatenation
    # "\n" + join + "\n" copied the 350 MB three times.
    BLOOM_BITS = 1 << 29          # 64 Mio de bits
    BLOOM_K = 4                  # empreintes par piece
    BLOOM_MASK64 = (1 << 64) - 1

    def __init__(self, corpus_line_list):
        self.text = "\n".join([""] + list(corpus_line_list) + [""])
        g, step = self.GRAM, self.STEP
        mask64 = self.BLOOM_MASK64
        bits = bytearray(self.BLOOM_BITS // 8)
        mask = self.BLOOM_BITS - 1
        k = self.BLOOM_K
        for line in corpus_line_list:
            for q in range(0, len(line) - g + 1, step):
                h = hash(line[q:q + g]) & mask64
                h2 = (h * 0x9E3779B97F4A7C15) & mask64
                for j in range(k):
                    pos = ((h + j * h2) & mask64) & mask
                    bits[pos >> 3] |= 1 << (pos & 7)
        self.bits = bits
        self.mask = mask
        self.k = k
        self.memo = {}

    def may_contain(self, window):
        g = self.GRAM
        bits = self.bits
        mask = self.mask
        k = self.k
        mask64 = self.BLOOM_MASK64
        for i in range(self.STEP):
            h = hash(window[i:i + g]) & mask64
            h2 = (h * 0x9E3779B97F4A7C15) & mask64
            for j in range(k):
                pos = ((h + j * h2) & mask64) & mask
                if not (bits[pos >> 3] >> (pos & 7)) & 1:
                    break
            else:
                return True
        return False


def longest_verbatim_run(line, corpus):
    """Longest fragment of ``line`` present word for word in the corpus.

    ``corpus`` is a ``CorpusText`` (fast) or a list of lines (reference).
    """
    if not isinstance(corpus, CorpusText):
        return longest_verbatim_run_reference(line, corpus)
    known = corpus.memo.get(line)
    if known is not None:
        return known
    run = _longest_run_fast(line, corpus)
    corpus.memo[line] = run
    return run


def _longest_run_fast(line, corpus):
    n = len(line)
    if n < LINE_MIN:
        return 0
    text = corpus.text
    mid = (n - LINE_MIN) // 2
    probes = []
    for start in (mid, 0):
        if start not in probes:
            probes.append(start)
    best = 0
    for start in probes:
        window = line[start:start + LINE_MIN]
        if not corpus.may_contain(window):
            continue
        tail = start + LINE_MIN
        pos = text.find(window)
        while pos != -1:
            # Longest common extension, by halving on slice equality (the
            # corpus text has a newline at both ends and between lines, and
            # the probed line has none, so it never crosses a corpus line).
            lo, hi = 0, min(start, pos)
            while lo < hi:
                mid_k = (lo + hi + 1) // 2
                if line[start - mid_k:start] == text[pos - mid_k:pos]:
                    lo = mid_k
                else:
                    hi = mid_k - 1
            left = lo
            end = pos + LINE_MIN
            lo, hi = 0, n - tail
            while lo < hi:
                mid_k = (lo + hi + 1) // 2
                if line[tail:tail + mid_k] == text[end:end + mid_k]:
                    lo = mid_k
                else:
                    hi = mid_k - 1
            right = lo
            best = max(best, left + LINE_MIN + right)
            if best >= n:
                return best
            pos = text.find(window, pos + 1)
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

    # The complete text of the corpus is built only for the test "the whole
    # content of the file is in the corpus", then it is released before the
    # search index is built: the two memory peaks do not add up.  The result
    # is printed in the same place as before.
    blob = corpus_blob(corpus_dir, index_path)
    corpus_text_length = len(blob)
    whole_file_hits = []
    for rel, full in files:
        text = texts.get(rel)
        if not text:
            continue
        stripped = text.strip()
        if stripped and len(stripped) >= LINE_MIN and blob.find(stripped) != -1:
            whole_file_hits.append((rel, len(stripped)))
    del blob

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
    print("   texte du corpus             : %d caracteres" % corpus_text_length)
    corpus_line_list = list(corpus_line_set.keys())
    corpus_text = CorpusText(corpus_line_list)
    # les lignes distinctes du corpus sont copiees dans le texte de recherche
    # et dans le filtre : elles ne servent plus.
    del corpus_line_set, corpus_line_list
    fragment_bytes = {}
    fragment_detail = {}
    for rel, full in files:
        text = texts.get(rel)
        if not text:
            continue
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
            run = longest_verbatim_run(line, corpus_text)
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
