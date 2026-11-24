"""Quick mode (option ``--quick``): a first answer in minutes, not hours.

The full corpus holds about 3,400 pages and takes about two hours to download
at one request per second. Most of the answers of the tool only need a small
part of it:

* the 26 A-Z index pages of the 8.0 C Library Reference say whether a symbol
  has a page of its own (``documented``) or is in the "described elsewhere"
  table of the index (``described_elsewhere``);
* the 26 A-Z index pages of the 7.1 C Library Reference say whether a symbol
  existed in 7.1;
* the official migration guide to 8.0 (one book, about 20 pages) gives the
  migration citations;
* the own page of each ``documented`` symbol gives the detail sentence.

So the quick mode downloads only these pages (about 80 requests for a short
list) into a small corpus with the same format as the full one, and runs the
same classifier on it.

What the quick mode can NOT say: ``absent`` and "mentioned in another 8.0
book" are statements about the WHOLE 8.0 documentation. Without the other
books, the quick mode prints ``absent`` only for a symbol that the official
migration guide (read in full) says was removed, quoting that sentence; any
other symbol found only in the
7.1 index, or in no index at all, is reported ``unknown`` with a note that
says why and how to get the definitive answer (the full corpus). The quick
mode therefore never contradicts the full mode: each ``documented`` or
``described elsewhere`` answer of the quick mode is also the answer of the
full mode (checked on the frozen corpus by ``tests/test_quick.py`` when the
corpus is present).
"""

import json
import os
import string
import time

from .classify import ABSENT, UNKNOWN, Classifier
from .corpus import LIB_REF_BOOK, MIGRATION_BOOK, Corpus
from .refresh import Downloader, build_corpus_from_cache

DOCS = "https://www.qnx.com/developers/docs/%s/%s/topic/"
INDEX_LETTERS = string.ascii_lowercase
QUICK_MODE = "quick"

QUICK_NOTES = {
    "fr": {
        "absent": "mode rapide : present dans l'index de la C Library Reference %s, "
                  "absent de l'index %s ; les autres livres %s n'ont pas ete lus, "
                  "donc absent ou decrit ailleurs reste a trancher par le corpus "
                  "complet (scripts/bootstrap_corpus.sh)",
        "unknown": "mode rapide : absent des index %s et %s ; les autres livres %s "
                   "n'ont pas ete lus (corpus complet : scripts/bootstrap_corpus.sh)",
    },
    "en": {
        "absent": "quick mode: in the %s C Library Reference index, not in the %s "
                  "index; the other %s books were not read, so absent or described "
                  "elsewhere is decided by the full corpus (scripts/bootstrap_corpus.sh)",
        "unknown": "quick mode: in neither the %s nor the %s index; the other %s "
                   "books were not read (full corpus: scripts/bootstrap_corpus.sh)",
    },
}


class QuickError(Exception):
    """A page needed by the quick mode could not be downloaded."""


def index_urls(version):
    """URLs of the 26 A-Z index pages of the C Library Reference."""
    base = DOCS % (version, LIB_REF_BOOK)
    return [base + "lib-%s.html" % letter for letter in INDEX_LETTERS]


def is_quick(corpus):
    return (corpus.manifest or {}).get("mode") == QUICK_MODE


def build_quick_corpus(out_dir, symbols, version="8.0", previous="7.1",
                       delay=1.0, downloader=None, progress=None):
    """Downloads the pages of the quick mode and writes a small corpus.

    Returns the manifest. Raises QuickError if an index page or a page of
    the migration guide is missing: an incomplete index would turn real
    answers into ``unknown``, so the quick mode refuses to answer.
    """
    say = progress or (lambda line: None)
    cache = os.path.join(out_dir, "cache")
    dl = downloader or Downloader(cache, delay=delay)
    t0 = time.time()
    for v in (version, previous):
        for url in index_urls(v):
            if not dl.fetch(url):
                raise QuickError("index page not downloaded: %s" % url)
        say("index %s: %d pages" % (v, len(INDEX_LETTERS)))
    migration = dl.crawl_book(version, MIGRATION_BOOK, "about.html")
    if not migration:
        raise QuickError("migration guide not downloaded: %s"
                         % (DOCS % (version, MIGRATION_BOOK) + "about.html"))
    say("migration guide %s: %d pages" % (version, len(migration)))
    build_corpus_from_cache(cache, out_dir, versions=(version, previous))

    # own page of each documented symbol (detail sentence)
    classifier = Classifier(Corpus(out_dir), version=version, previous=previous)
    own = []
    seen_own = set()
    for sym in symbols:
        entry = classifier.entries.get(sym)
        if entry:
            base_url = entry["url"].split("#")[0]
            if base_url not in seen_own:
                seen_own.add(base_url)
                own.append(base_url)
    for url in own:
        dl.fetch(url)          # a missing own page only loses the detail line
    say("own pages of the documented symbols: %d" % len(own))

    manifest = build_corpus_from_cache(cache, out_dir, versions=(version, previous))
    manifest["mode"] = QUICK_MODE
    manifest["quick"] = {
        "symbols": list(symbols),
        "requests": getattr(dl, "fetched", None),
        "seconds": round(time.time() - t0, 1),
        "books_not_read": "every 8.0 book except the C Library Reference index "
                          "and the migration guide",
    }
    with open(os.path.join(out_dir, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return manifest


def apply_quick_limits(results, version="8.0", previous="7.1", lang="en"):
    """Removes from quick results what only the full corpus can prove.

    ``absent`` becomes ``unknown`` (the 7.1 page and citation stay: they are
    facts); the note of every ``unknown`` says what was not read.
    """
    n = QUICK_NOTES[lang if lang in QUICK_NOTES else "en"]
    for res in results:
        if res.status == ABSENT and getattr(res, "removed_by_migration_guide", False):
            # the removal is stated by the official migration guide, which
            # the quick mode has read in full: this "absent" is a quotation,
            # not a conclusion drawn from the books it did not read
            continue
        if res.status == ABSENT:
            res.status = UNKNOWN
            res.note = n["absent"] % (previous, version, version)
        elif res.status == UNKNOWN:
            res.note = n["unknown"] % (version, previous, version)
    return results
