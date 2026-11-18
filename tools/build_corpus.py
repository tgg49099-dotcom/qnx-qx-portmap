#!/usr/bin/env python3
"""Freezes the QNX documentation corpus in the QX PORTMAP repository.

The corpus is a copy, page by page, of the official QNX documentation
(versions 7.1 and 8.0) as it was downloaded on the day of the build: the
frozen snapshot of the project was downloaded on 14/11/2026, a corpus rebuilt
by ``scripts/bootstrap_corpus.sh`` carries the date of its own download log.
Every page is stored compressed (gzip) as it was downloaded, and its SHA-256
fingerprint is written in ``corpus/index/pages.jsonl``.

Usage:
    python3 tools/build_corpus.py --cache /path/to/cache --out corpus

The script is deterministic: same cache, same corpus.  The date written in the
manifest is the date of the download log of that build (``download.log`` in
the output directory), the day of the build when there is no log.
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import time

OUT_RELPATH = re.compile(r'name="wh-out-relpath"\s+content="([^"]+)"')
VERSION_RE = re.compile(r"_docs_(\d+\.\d+)_")
DOCS_ROOT = "https://www.qnx.com/developers/docs/%s/"


def consulted_date(out_root):
    """Date on which the pages of this corpus were downloaded.

    The log of the download carries the real date of every page; the last one
    is the date of the corpus.  Without a log, the day of the build is used.
    A corpus rebuilt today must not claim the date of the frozen snapshot.
    """
    dates = []
    try:
        with open(os.path.join(out_root, "download.log"), encoding="utf-8") as fh:
            for line in fh:
                if "\tOK\t" in line:
                    dates.append(line[:10])
    except OSError:
        dates = []
    if dates:
        return max(dates)
    return time.strftime("%Y-%m-%d")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def relpath_of(raw_text, filename):
    """Relative path of the book/topic of the page, from the Oxygen tag.

    Fallback: rebuild it from the file name of the cache.
    """
    m = OUT_RELPATH.search(raw_text)
    if m:
        rel = m.group(1)
        if rel.endswith(".html"):
            return rel
    m = VERSION_RE.search(filename)
    rest = filename.split("_docs_", 1)[1]
    version, tail = rest.split("_", 1)
    book, _, topic = tail.partition("_topic_")
    return "%s/topic/%s" % (book, topic)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", required=True, help="repertoire du cache de telechargement")
    ap.add_argument("--out", default="corpus", help="repertoire du corpus a ecrire")
    args = ap.parse_args()

    out_root = os.path.abspath(args.out)
    os.makedirs(out_root, exist_ok=True)
    pages_dir = os.path.join(out_root, "pages")
    index_dir = os.path.join(out_root, "index")
    os.makedirs(index_dir, exist_ok=True)

    records = []
    skipped = []
    for name in sorted(os.listdir(args.cache)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(args.cache, name)
        m = VERSION_RE.search(name)
        if not m:
            skipped.append(name)
            continue
        version = m.group(1)
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", "replace")
        rel = relpath_of(text, name)
        dest = os.path.join(pages_dir, version, rel + ".gz")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # deterministic gzip (mtime=0) so that the corpus is reproducible
        with open(dest, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(raw)
        records.append({
            "version": version,
            "book": rel.split("/topic/")[0],
            "topic": rel.split("/topic/", 1)[1] if "/topic/" in rel else rel,
            "url": DOCS_ROOT % version + rel,
            "file": os.path.relpath(dest, out_root).replace(os.sep, "/"),
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
        })

    # --- index of the pages ------------------------------------------------
    pages_jsonl = os.path.join(index_dir, "pages.jsonl")
    with open(pages_jsonl, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    # --- SHA256SUMS (fingerprints of the stored files) ---------------------
    sums_path = os.path.join(out_root, "SHA256SUMS")
    entries = []
    for dirpath, dirnames, filenames in os.walk(out_root):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn == "SHA256SUMS" or fn == "MANIFEST.json":
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, out_root).replace(os.sep, "/")
            entries.append((rel, sha256_file(full)))
    with open(sums_path, "w", encoding="utf-8") as fh:
        for rel, digest in entries:
            fh.write("%s  %s\n" % (digest, rel))

    # --- manifeste ----------------------------------------------------------
    by_version = {}
    for rec in records:
        by_version.setdefault(rec["version"], {"pages": 0, "bytes": 0})
        by_version[rec["version"]]["pages"] += 1
        by_version[rec["version"]]["bytes"] += rec["bytes"]
    books = {}
    for rec in records:
        books[rec["book"]] = books.get(rec["book"], 0) + 1

    consulted = consulted_date(out_root)
    manifest = {
        "corpus": "QNX documentation (C Library Reference et livres lies)",
        "tool": "QX PORTMAP",
        "built": consulted,
        "consulted": consulted,
        "docs_root": {v: DOCS_ROOT % v for v in sorted(by_version)},
        "versions": sorted(by_version),
        "pages_total": len(records),
        "pages_by_version": {v: by_version[v]["pages"] for v in sorted(by_version)},
        "bytes_by_version": {v: by_version[v]["bytes"] for v in sorted(by_version)},
        "pages_by_book": dict(sorted(books.items(), key=lambda kv: (-kv[1], kv[0]))),
        "files": len(entries),
        "sha256sums": "SHA256SUMS",
        "pages_index": "index/pages.jsonl",
        "integrity": "sha256 dans index/pages.jsonl = empreinte des octets originaux "
                     "telecharges ; SHA256SUMS = empreinte des fichiers stockes (gzip)",
        "note": "Copie de pages de documentation QNX (c) QNX Software Systems Ltd / "
                "BlackBerry Limited. Non redistribuable sans autorisation : voir README.",
        "skipped_files": skipped,
    }
    with open(os.path.join(out_root, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    print("pages figees : %d" % len(records))
    for v in sorted(by_version):
        print("   %-5s %5d pages  %8.1f Mo" % (v, by_version[v]["pages"],
                                               by_version[v]["bytes"] / 1e6))
    print("fichiers dans corpus : %d" % len(entries))
    if skipped:
        print("fichiers ignores : %d" % len(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
