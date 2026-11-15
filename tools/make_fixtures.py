#!/usr/bin/env python3
"""Builds the miniature fixtures of ``tests/fixtures/``.

The fixtures are short extracts (1 to 3 lines) of official pages of the QNX
documentation, with the source URL and the consultation date. They make it
possible to run the tests of the tool **without** the complete corpus: the
corpus is not redistributed, it is rebuilt on demand
(``scripts/bootstrap_corpus.sh``).

This script is not needed to use the tool: it documents how the fixtures were
produced. It is deterministic: same corpus, same fixtures.

Usage:
    python3 tools/make_fixtures.py \
        --corpus /work/qnx-portmap-corpus-local/corpus --out tests/fixtures
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import sys

CONSULTED = "2026-11-14"
DOCS_ROOT = "https://www.qnx.com/developers/docs/%s/"

# (id, version, book, topic, kind, expected symbol, selector)
SPECS = [
    ("f01", "8.0", "com.qnx.doc.neutrino.lib_ref", "a/abort.html", "h1", "abort",
     {"type": "line", "contains": "<h1 ", "count": 1}),
    ("f02", "8.0", "com.qnx.doc.neutrino.lib_ref", "a/abort.html", "shortdesc", "abort",
     {"type": "line", "contains": "shortdesc", "count": 1}),
    ("f03", "8.0", "com.qnx.doc.neutrino.lib_ref", "a/abort.html", "description", "abort",
     {"type": "line", "contains": "function causes abnormal process termination", "count": 3}),
    ("f04", "8.0", "com.qnx.doc.neutrino.lib_ref", "lib-a.html", "index-nav", "abort",
     {"type": "element", "pattern": r'<li role="treeitem">.*?</li>',
      "contains": "/topic/a/abort.html", "count": 1}),
    ("f05", "8.0", "com.qnx.doc.neutrino.lib_ref", "lib-a.html", "index-elsewhere", "accept",
     {"type": "line", "contains": ">accept(), accept4()</span>", "count": 1}),
    ("f06", "7.1", "com.qnx.doc.neutrino.lib_ref", "b/bzero.html", "h1", "bzero",
     {"type": "line", "contains": "<h1 ", "count": 1}),
    ("f07", "8.0", "com.qnx.doc.neutrino.building", "callouts/callout_rwstorage.html",
     "bold", "rw_interrupt",
     {"type": "line", "contains": "<strong", "count": 1}),
    ("f08", "8.0", "com.qnx.doc.neutrino.user_guide", "glossary.html", "prose", "",
     {"type": "line", "contains": "Changing a bit from a 0 state into a 1 state", "count": 2}),
    ("f09", "8.0", "com.qnx.doc.qnxsdp.migration", "c_apps.html", "migration", "_smalloc",
     {"type": "line", "contains": "The following functions have been removed from", "count": 3}),
    ("f10", "8.0", "com.qnx.doc.neutrino.io_sock", "socket_api.html", "mention",
     "getprotobyname_r",
     {"type": "element",
      "pattern": r'<span class="[^"]*apiname[^"]*">getprotobyname_r\(\)</span>',
      "contains": "getprotobyname_r()", "count": 1}),
    ("f11", "8.0", "com.qnx.doc.neutrino.lib_ref", "lib-e.html", "index-nav", "errno",
     {"type": "element", "pattern": r'<li role="treeitem">.*?</li>',
      "contains": "/topic/e/errno.html", "count": 1}),
    ("f12", "7.1", "com.qnx.doc.neutrino.lib_ref", "lib-b.html", "index-nav", "bzero",
     {"type": "element", "pattern": r'<li role="treeitem">.*?</li>',
      "contains": "/topic/b/bzero.html", "count": 1}),
]


def load_index(corpus_dir):
    index = {}
    path = os.path.join(corpus_dir, "index", "pages.jsonl")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                index[(rec["version"], rec["book"], rec["topic"])] = rec
    return index


def page_html(corpus_dir, rec):
    with gzip.open(os.path.join(corpus_dir, rec["file"]), "rb") as fh:
        return fh.read().decode("utf-8", "replace")


def extract(html, selector):
    """Extracts the requested fragment. Returns a list of lines."""
    kind = selector["type"]
    count = selector.get("count", 1)
    if kind == "line":
        lines = html.splitlines()
        scope = list(range(len(lines)))
        if selector.get("scope", "article") == "article":
            # only the <article> body of the page is searched:
            # the header (<head>) and the navigation are not documentation
            # extracts, they are repeated on every page.
            first = last = None
            for i, line in enumerate(lines):
                if first is None and "<article" in line:
                    first = i
                if "</article>" in line:
                    last = i
            if first is None:
                first, last = 0, len(lines) - 1
            scope = list(range(first, last + 1))
        for i in scope:
            if selector["contains"] in lines[i]:
                return [lines[j] for j in range(i, min(i + count, len(lines)))]
        raise LookupError("motif introuvable : %r" % selector["contains"])
    if kind == "element":
        for m in re.finditer(selector["pattern"], html, re.S):
            block = m.group(0)
            if selector.get("contains", "") in block:
                return [block]
        raise LookupError("element introuvable : %r" % selector.get("contains"))
    raise ValueError("selecteur inconnu : %r" % kind)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default=os.environ.get(
        "QX_PORTMAP_CORPUS", "/work/qnx-portmap-corpus-local/corpus"))
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "fixtures"))
    args = ap.parse_args()

    index = load_index(args.corpus)
    os.makedirs(args.out, exist_ok=True)
    written = []
    for fid, version, book, topic, kind, symbol, selector in SPECS:
        key = (version, book, topic)
        if key not in index:
            sys.stderr.write("page introuvable dans le corpus : %s\n" % (key,))
            return 1
        rec = index[key]
        html = page_html(args.corpus, rec)
        lines = extract(html, selector)
        content = "\n".join(l.rstrip() for l in lines)
        header = [
            "# fixture %s : %s" % (fid, kind),
            "# source : %s" % rec["url"],
            "# consulte le : %s" % CONSULTED,
            "# livre : %s" % book,
            "# topic : %s" % topic,
            "# sha256 de la page source : %s" % rec["sha256"],
            "# symbole attendu : %s" % (symbol or "(aucun)"),
            "# lignes de l'extrait : %d" % len(lines),
            "",
        ]
        path = os.path.join(args.out, "%s-%s.txt" % (fid, symbol or kind))
        with open(path, "w", encoding="utf-8") as fh:
            # the headers, an empty line, then the verbatim extract
            fh.write("\n".join(header) + "\n" + content + "\n")
        written.append((path, len(lines), len(content)))
        print("%-14s %-18s %d ligne(s) %5d octets  %s"
              % (fid, kind, len(lines), len(content), os.path.basename(path)))
    print()
    print("fixtures ecrites : %d (maximum autorise : 12)" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
