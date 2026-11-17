#!/usr/bin/env python3
"""Checks that no placeholder is left in the published documents.

The submission kit (``KIT-SOUMISSION-QNX.md``) is the text the entrant pastes
into the Devpost form: a placeholder left in it is a field that would be
pasted as-is, and a placeholder left in the README is a promise the repository
does not keep.  This control looks for the placeholder tokens used by this
project (``*_TO_BE_FILLED*``, ``*_A_COMPLETER*`` and the length placeholder
``__LEN_*`` of the submission kit) in every published document, and checks
that the demonstration video URL written in the README is also written in the
submission kit.

The control is a **control**: it must be able to fail.  On the state of the
tree before the video was published (17 November 2026), it prints the three
placeholders it found and exits 1.

Usage::

    python3 tools/controle_placeholders.py            # exit 1 if a placeholder is left
    python3 tools/controle_placeholders.py --tree DIR # check another tree

Exit code: 0 when every published document is free of placeholder, 1 otherwise.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The same directories as the published manifest: they are not published.
IGNORED_DIRS = (".git", "__pycache__", "build", "dist", "qnx_portmap.egg-info",
                ".pytest_cache")
IGNORED_SUFFIX = (".pyc", ".pyo", ".orig", ".rej")

# Only the documents are scanned: the sources of the tools may name the
# patterns they look for (this file does), and that would be a false positive.
DOCUMENT_SUFFIX = (".md", ".txt")

# The placeholder tokens, and what they mean.
PLACEHOLDERS = [
    ("TO_BE_FILLED", "a field to fill once the artefact is published"),
    ("A_COMPLETER", "a text to complete once the artefact is published"),
    ("__LEN_", "the length placeholder of the submission kit"),
]

# The two files that must carry the same demonstration video URL.
VIDEO_URL_FILES = ("README.md", "KIT-SOUMISSION-QNX.md")

# A URL of a video on YouTube, in the form used in this repository.
VIDEO_URL = re.compile(r"https://youtu\.be/[A-Za-z0-9_-]+")


def published_documents(tree):
    """Returns the sorted list of the published documents of *tree*."""
    out = []
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for name in sorted(filenames):
            if name.endswith(IGNORED_SUFFIX):
                continue
            if not name.endswith(DOCUMENT_SUFFIX):
                continue
            full = os.path.join(dirpath, name)
            out.append((os.path.relpath(full, tree).replace(os.sep, "/"), full))
    return sorted(out)


def find_placeholders(tree):
    """Returns [(path, line number, token, line)] for every placeholder found."""
    found = []
    for rel, full in published_documents(tree):
        with open(full, encoding="utf-8") as handle:
            for number, line in enumerate(handle.read().split("\n"), start=1):
                for token, _why in PLACEHOLDERS:
                    if token in line:
                        found.append((rel, number, token, line.strip()))
    return found


def video_urls(tree):
    """Returns the demonstration video URL of each file of VIDEO_URL_FILES."""
    urls = {}
    for rel in VIDEO_URL_FILES:
        path = os.path.join(tree, rel)
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            urls[rel] = None
            continue
        found = VIDEO_URL.findall(text)
        urls[rel] = found[0] if found else None
    return urls


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tree", default=ROOT,
                        help="arbre a controler (default: la racine du depot)")
    args = parser.parse_args(argv)
    tree = os.path.abspath(args.tree)
    if not os.path.isdir(tree):
        print("tree not found: %s" % tree)
        return 2

    documents = published_documents(tree)
    found = find_placeholders(tree)
    failed = False

    print("CONTROL OF THE PLACEHOLDERS - %d published documents" % len(documents))
    if found:
        failed = True
        print("\nKO : %d placeholder(s) left in the published documents:" % len(found))
        for rel, number, token, line in found:
            print("  - %s:%d: [%s] %s" % (rel, number, token, line))
    else:
        print("OK : no placeholder in the %d published documents." % len(documents))

    urls = video_urls(tree)
    kit = urls.get("KIT-SOUMISSION-QNX.md")
    readme = urls.get("README.md")
    if readme is None:
        failed = True
        print("\nKO : no demonstration video URL in README.md.")
    elif kit is None:
        failed = True
        print("\nKO : no demonstration video URL in KIT-SOUMISSION-QNX.md, "
              "but README.md has one (%s)." % readme)
    elif kit != readme:
        failed = True
        print("\nKO : the video URL of the README (%s) is not the one of the "
              "submission kit (%s)." % (readme, kit))
    else:
        print("OK : the same video URL in the README and in the submission kit: %s"
              % readme)

    if failed:
        print("\nVERDICT: FAILED - a placeholder is left, or the video URL is "
              "not the same in the README and in the kit (RC 1)")
        return 1
    print("\nVERDICT: NO PLACEHOLDER LEFT (RC 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
