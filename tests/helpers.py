"""Outils de test : construction d'un petit corpus QNX synthetique.

Deux corpus de test sont construits ici :

* ``build_mini_corpus`` : un corpus **fabrique a la main**, avec la meme
  structure de fichiers que le corpus fige livre (MANIFEST.json,
  index/pages.jsonl, SHA256SUMS, pages compressees). Il permet de tester les
  cas limites sans dependre des 3 426 pages du corpus reel ;
* ``build_fixture_corpus`` : un corpus **reconstruit a partir des fixtures
  miniatures** (extraits courts de pages QNX reelles, ``tests/fixtures/``).
  Il permet de faire tourner les tests de l'outil sur de la documentation
  QNX reelle sans redistribuer le corpus complet.
"""

import gzip
import hashlib
import json
import os

DOCS_ROOT = "https://www.qnx.com/developers/docs/%s/"
LIB_REF = "com.qnx.doc.neutrino.lib_ref"
USER_GUIDE = "com.qnx.doc.neutrino.user_guide"
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

# Message de saut des tests qui exigent le corpus complet. Le corpus n'est
# pas redistribue : il se reconstruit avec scripts/bootstrap_corpus.sh.
CORPUS_ABSENT_MSG = "corpus absent : lancer scripts/bootstrap_corpus.sh"


def _page(version, book, topic, body):
    """Page HTML au format Oxygen, avec le lien de version dans wh-out-relpath."""
    rel = "%s/topic/%s" % (book, topic)
    return (
        "<!DOCTYPE html><html><head><title>%s</title>"
        '<meta name="wh-out-relpath" content="%s"/></head><body>'
        "<nav><ul>%s</ul></nav>"
        "<article><h1>%s</h1>%s</article>"
        "</body></html>" % (topic, rel, body, topic, body)
    )


def index_html(version, entries, elsewhere):
    """Page d'index A-Z : entrees de l'arbre de navigation + table "elsewhere".

    ``entries``   : liste de (nom, href, description courte)
    ``elsewhere`` : liste de (noms, texte "See", href)
    """
    nav = []
    for name, href, desc in entries:
        if name.endswith("()"):
            label = '<span class="keyword apiname">%s</span>' % name
        else:
            label = '<var class="keyword varname">%s</var>' % name
        nav.append(
            '<li role="treeitem"><div class="topicref" data-id="x"><div class="title">'
            '<a href="%s">%s</a>'
            '<div class="wh-tooltip"><p class="shortdesc"><em class="ph i">%s</em></p></div>'
            "</div></div></li>" % (href, label, desc))
    rows = []
    for names, text, href in elsewhere:
        rows.append(
            "<tr><td><span class=\"+ topic/keyword pr-d/apiname keyword apiname\">%s</span></td>"
            '<td>%s <a href="%s">the user guide</a></td></tr>' % (names, text, href))
    table = ""
    if rows:
        table = ("<p>The following are described elsewhere:</p>"
                 "<table><tbody>%s</tbody></table>" % "".join(rows))
    return (
        "<!DOCTYPE html><html><head><title>lib-a</title>"
        '<meta name="wh-out-relpath" content="%s/topic/lib-a.html"/></head><body>'
        "<nav><ul>%s</ul></nav><article><h1>A</h1>%s</article></body></html>"
        % (LIB_REF, "".join(nav), table))


def topic_html(version, book, topic, title, shortdesc, description, body=""):
    return (
        "<!DOCTYPE html><html><head><title>%s</title>"
        '<meta name="wh-out-relpath" content="%s/topic/%s"/></head><body>'
        "<article><h1><span class=\"+ topic/keyword pr-d/apiname keyword apiname\">%s</span></h1>"
        '<p class="- topic/shortdesc shortdesc"><em class="+ topic/ph hi-d/i ph i">%s</em></p>'
        "<section><h2>Description:</h2>"
        '<p class="- topic/p p">%s</p></section>%s</article></body></html>'
        % (topic, book, topic, title, shortdesc, description, body))


def build_mini_corpus(root, corrupt=None):
    """Ecrit un corpus de test dans ``root``.

    ``corrupt`` : nom du fichier a corrompre apres ecriture (test d'integrite).
    """
    os.makedirs(root, exist_ok=True)
    pages = []

    def add(version, book, topic, html):
        rel = "%s/topic/%s" % (book, topic)
        name = "%s__%s__%s.html.gz" % (version.replace(".", "_"), book, topic.replace("/", "_"))
        path = os.path.join(root, "pages", version, book, "topic",
                            topic.replace("/", os.sep) + ".gz")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        raw = html.encode("utf-8")
        with open(path, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(raw)
        pages.append({
            "version": version,
            "book": book,
            "topic": topic,
            "url": (DOCS_ROOT % version) + rel,
            "file": os.path.relpath(path, root).replace(os.sep, "/"),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        })
        return path

    # --- 8.0 : index avec frob() et une variable, plus un renvoi "elsewhere"
    add("8.0", LIB_REF, "lib-a.html", index_html(
        "8.0",
        [("frob()", "../../%s/topic/f/frob.html" % LIB_REF, "Frob the widget"),
         ("widget", "../../%s/topic/w/widget.html" % LIB_REF, "The widget handle")],
        [("vanish(), vanish2()", "See", "../../%s/topic/vanish.html" % USER_GUIDE)]))

    add("8.0", LIB_REF, "f/frob.html", topic_html(
        "8.0", LIB_REF, "f/frob.html", "frob()", "Frob the widget",
        "The frob() function frobs the widget. It returns 0 on success."))

    add("8.0", LIB_REF, "w/widget.html", topic_html(
        "8.0", LIB_REF, "w/widget.html", "widget", "The widget handle",
        "The widget variable holds the handle of the current widget."))

    # page d'un autre livre : un symbole cite en gras, et qui n'existe
    # que sous cette forme (aucun appel "nom(" dans la page)
    add("8.0", USER_GUIDE, "bold.html", topic_html(
        "8.0", USER_GUIDE, "bold.html", "Bold", "A page with a bold symbol",
        "The <strong>bold_api</strong> symbol is described here in bold."))

    add("8.0", USER_GUIDE, "vanish.html", topic_html(
        "8.0", USER_GUIDE, "vanish.html", "vanish", "The vanished widget",
        "The vanish() and vanish2() functions are documented in the user guide."))

    # page d'un autre livre : un mot anglais rencontre en prose
    add("8.0", USER_GUIDE, "prose.html", topic_html(
        "8.0", USER_GUIDE, "prose.html", "Prose", "A page with English words",
        "The argument of the call is checked at runtime, and the result is normal ( normal )."))

    # --- 7.1 : meme index, mais avec gone() en plus
    add("7.1", LIB_REF, "lib-a.html", index_html(
        "7.1",
        [("frob()", "../../%s/topic/f/frob.html" % LIB_REF, "Frob the widget"),
         ("gone()", "../../%s/topic/g/gone.html" % LIB_REF, "Gone since 8.0")],
        []))

    add("7.1", LIB_REF, "g/gone.html", topic_html(
        "7.1", LIB_REF, "g/gone.html", "gone()", "Gone since 8.0",
        "The gone() function existed in QNX 7.1 and was removed in 8.0."))

    # --- index des pages + manifeste -------------------------------------
    index_dir = os.path.join(root, "index")
    os.makedirs(index_dir, exist_ok=True)
    with open(os.path.join(index_dir, "pages.jsonl"), "w", encoding="utf-8") as fh:
        for rec in pages:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    by_version = {}
    by_book = {}
    for rec in pages:
        by_version[rec["version"]] = by_version.get(rec["version"], 0) + 1
        by_book[rec["book"]] = by_book.get(rec["book"], 0) + 1
    manifest = {
        "corpus": "mini corpus de test",
        "tool": "QX PORTMAP",
        "built": "2026-11-14",
        "consulted": "2026-11-14",
        "docs_root": {v: DOCS_ROOT % v for v in sorted(by_version)},
        "versions": sorted(by_version),
        "pages_total": len(pages),
        "pages_by_version": by_version,
        "pages_by_book": by_book,
        "files": len(pages),
        "sha256sums": "SHA256SUMS",
        "pages_index": "index/pages.jsonl",
    }
    with open(os.path.join(root, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    sums = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn in ("SHA256SUMS", "MANIFEST.json"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            with open(full, "rb") as f:
                sums.append("%s  %s" % (hashlib.sha256(f.read()).hexdigest(), rel))
    with open(os.path.join(root, "SHA256SUMS"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sums) + "\n")

    if corrupt:
        target = os.path.join(root, "pages", "8.0", LIB_REF, "topic", "f", "frob.html.gz")
        with open(target, "ab") as fh:
            fh.write(b"\x00corruption")

    return root


# ---------------------------------------------------------------------------
# Corpus construit a partir des fixtures miniatures (documentation QNX reelle)
# ---------------------------------------------------------------------------

def read_fixture(name):
    """Lit une fixture de ``tests/fixtures/``.

    Retourne ``(meta, lignes)`` : ``meta`` est le dictionnaire des
    entetes (``# cle: valeur``), ``lignes`` la liste des lignes verbatim.
    """
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    head, _, body = text.partition("\n\n")
    meta = {}
    for line in head.splitlines():
        if line.startswith("# ") and ":" in line:
            key, _, value = line[2:].partition(":")
            meta[key.strip()] = value.strip()
    return meta, body.splitlines()


def fixture(name):
    """Lignes verbatim d'une fixture, sans les entetes."""
    return read_fixture(name)[1]


def _page_html(inner, title="page", relpath=None):
    """Enveloppe un fragment dans un document HTML minimal."""
    head = ""
    if relpath:
        head = ('<meta name="wh-out-relpath" content="%s"/>' % relpath)
    return ("<!DOCTYPE html><html><head><title>%s</title>%s</head>"
            "<body><article>%s</article></body></html>" % (title, head, inner))


def build_fixture_corpus(root):
    """Ecrit dans ``root`` un corpus construit avec les fixtures miniatures.

    Le corpus a exactement la meme structure que le corpus fige livre
    (MANIFEST.json, index/pages.jsonl, SHA256SUMS, pages compressees) : il
    passe donc par le vrai code de chargement, sans corpus complet.
    """
    os.makedirs(root, exist_ok=True)
    nav80 = "\n".join(fixture("f04-abort.txt"))
    nav71 = "\n".join(fixture("f12-bzero.txt"))
    nav_errno = "\n".join(fixture("f11-errno.txt"))
    td_elsewhere = "\n".join(fixture("f05-accept.txt"))
    h1_abort = "\n".join(fixture("f01-abort.txt"))
    shortdesc_abort = "\n".join(fixture("f02-abort.txt"))
    desc_abort = "\n".join(fixture("f03-abort.txt"))
    h1_bzero = "\n".join(fixture("f06-bzero.txt"))
    bold_rw = "\n".join(fixture("f07-rw_interrupt.txt"))
    prose = "\n".join(fixture("f08-prose.txt"))
    migration = "\n".join(fixture("f09-_smalloc.txt"))
    mention = "\n".join(fixture("f10-getprotobyname_r.txt"))

    pages = []

    def add(version, book, topic, html):
        rel = "%s/topic/%s" % (book, topic)
        dest = os.path.join(root, "pages", version, *rel.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        raw = html.encode("utf-8")
        with open(dest, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(raw)
        pages.append({
            "version": version,
            "book": book,
            "topic": topic,
            "url": (DOCS_ROOT % version) + rel,
            "file": os.path.relpath(dest, root).replace(os.sep, "/"),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        })

    # index 8.0 : une entree d'index (abort), une variable (errno) et le
    # tableau "described elsewhere"
    add("8.0", LIB_REF, "lib-a.html", (
        "<!DOCTYPE html><html><head><title>A</title>"
        '<meta name="wh-out-relpath" content="%s/topic/lib-a.html"/></head><body>'
        "<nav><ul>%s%s</ul></nav>"
        "<article><h1>A</h1>"
        "<p>The following are described elsewhere:</p>"
        '<table class="- topic/table table"><tbody><tr class="- topic/row">'
        "%s"
        '<td class="- topic/entry entry">See <a class="- topic/xref xref" '
        'href="../../com.qnx.doc.neutrino.io_sock/topic/socket_api.html">'
        "the io-sock User's Guide</a></td>"
        "</tr></tbody></table></article></body></html>"
        % (LIB_REF, nav80, nav_errno, td_elsewhere)))

    # index 7.1 : une entree d'index (bzero)
    add("7.1", LIB_REF, "lib-b.html", (
        "<!DOCTYPE html><html><head><title>B</title>"
        '<meta name="wh-out-relpath" content="%s/topic/lib-b.html"/></head><body>'
        "<nav><ul>%s</ul></nav><article><h1>B</h1></article></body></html>"
        % (LIB_REF, nav71)))

    # page de symbole 8.0 (abort) : titre, description courte, description
    add("8.0", LIB_REF, "a/abort.html", _page_html(
        "%s%s<section class=\"- topic/section section\">"
        '<h2 class="- topic/title title sectiontitle">Description:</h2>'
        '<p class="- topic/p p">%s</p></section>'
        % (h1_abort, shortdesc_abort, desc_abort),
        title="abort()", relpath="%s/topic/a/abort.html" % LIB_REF))

    # page de symbole 7.1 (bzero)
    add("7.1", LIB_REF, "b/bzero.html", _page_html(
        h1_bzero, title="bzero()", relpath="%s/topic/b/bzero.html" % LIB_REF))

    # mention en gras (rw_interrupt)
    add("8.0", "com.qnx.doc.neutrino.building", "callouts/callout_rwstorage.html",
        _page_html('<p class="- topic/p p">%s</p>' % bold_rw,
                   title="Callout library",
                   relpath="com.qnx.doc.neutrino.building/topic/callouts/callout_rwstorage.html"))

    # prose anglaise sans nom d'API
    add("8.0", USER_GUIDE, "glossary.html", _page_html(
        prose, title="Glossary",
        relpath="%s/topic/glossary.html" % USER_GUIDE))

    # mention d'une fonction d'un autre livre (bindresvport)
    add("8.0", "com.qnx.doc.neutrino.io_sock", "socket_api.html", _page_html(
        '<p class="- topic/p p">%s</p>' % mention,
        title="Socket API",
        relpath="com.qnx.doc.neutrino.io_sock/topic/socket_api.html"))

    # guide de migration officiel (symboles supprimes de libc)
    add("8.0", "com.qnx.doc.qnxsdp.migration", "c_apps.html", _page_html(
        "<ul><li>%s</li></ul>" % migration,
        title="C and C++ applications",
        relpath="com.qnx.doc.qnxsdp.migration/topic/c_apps.html"))

    # --- index des pages + manifeste ---------------------------------------
    index_dir = os.path.join(root, "index")
    os.makedirs(index_dir, exist_ok=True)
    with open(os.path.join(index_dir, "pages.jsonl"), "w", encoding="utf-8") as fh:
        for rec in pages:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    by_version = {}
    for rec in pages:
        by_version[rec["version"]] = by_version.get(rec["version"], 0) + 1
    manifest = {
        "corpus": "corpus miniature reconstruit depuis les fixtures",
        "tool": "QX PORTMAP",
        "built": "2026-11-14",
        "consulted": "2026-11-14",
        "docs_root": {v: DOCS_ROOT % v for v in sorted(by_version)},
        "versions": sorted(by_version),
        "pages_total": len(pages),
        "pages_by_version": by_version,
        "files": len(pages),
        "sha256sums": "SHA256SUMS",
        "pages_index": "index/pages.jsonl",
    }
    with open(os.path.join(root, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    sums = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn in ("SHA256SUMS", "MANIFEST.json"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            with open(full, "rb") as f:
                sums.append("%s  %s" % (hashlib.sha256(f.read()).hexdigest(), rel))
    with open(os.path.join(root, "SHA256SUMS"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sums) + "\n")
    return root
