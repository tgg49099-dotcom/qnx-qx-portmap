"""Acces au corpus de documentation QNX fige dans le depot.

Le corpus est un ensemble de pages HTML officielles, compressees en gzip,
accompagnees de leurs empreintes SHA-256. Rien n'est telecharge au runtime :
le mode par defaut est hors ligne.
"""

import gzip
import hashlib
import json
import os
import re

from .extract import strip_tags

DEFAULT_CORPUS_ENV = "QX_PORTMAP_CORPUS"
LIB_REF_BOOK = "com.qnx.doc.neutrino.lib_ref"
MIGRATION_BOOK = "com.qnx.doc.qnxsdp.migration"
INDEX_PREFIX = "lib-"


def default_corpus_dir():
    """Repertoire du corpus.

    Ordre de recherche :
      1. la variable d'environnement ``QX_PORTMAP_CORPUS`` ;
      2. le repertoire ``corpus/`` livre a cote du paquet (depot) ;
      3. le repertoire ``corpus/`` du repertoire courant (installation
         dans un site-packages, usage depuis la racine du depot).
    """
    env = os.environ.get(DEFAULT_CORPUS_ENV)
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.abspath(os.path.join(here, os.pardir, "corpus")),
        os.path.abspath(os.path.join(os.getcwd(), "corpus")),
    ]
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, "MANIFEST.json")):
            return cand
    return candidates[0]


class CorpusError(Exception):
    """Le corpus est absent, incomplet ou corrompu."""


class Page(object):
    """Une page du corpus."""

    __slots__ = ("version", "book", "topic", "url", "file", "sha256", "bytes")

    def __init__(self, rec):
        self.version = rec["version"]
        self.book = rec["book"]
        self.topic = rec["topic"]
        self.url = rec["url"]
        self.file = rec["file"]
        self.sha256 = rec["sha256"]
        self.bytes = rec["bytes"]

    @property
    def is_index_page(self):
        return self.book == LIB_REF_BOOK and self.topic.startswith(INDEX_PREFIX)

    @property
    def is_migration_page(self):
        return self.book == MIGRATION_BOOK

    def __repr__(self):
        return "<Page %s %s>" % (self.version, self.topic)


class Corpus(object):
    """Le corpus fige, en lecture seule."""

    def __init__(self, root=None, lang="fr"):
        self.root = os.path.abspath(root or default_corpus_dir())
        self.lang = lang if lang in ("fr", "en") else "fr"
        self.manifest = None
        self.pages = []
        self._by_key = {}
        self._by_url = {}
        self._text_cache = {}
        self._load()

    def _t(self, fr, en):
        """Message dans la langue demandee ; le francais reste le defaut."""
        return en if self.lang == "en" else fr

    # -- chargement ------------------------------------------------------
    def _load(self):
        manifest_path = os.path.join(self.root, "MANIFEST.json")
        if not os.path.isfile(manifest_path):
            raise CorpusError(self._t("corpus introuvable : %s" % self.root,
                                      "corpus not found: %s" % self.root))
        with open(manifest_path, encoding="utf-8") as fh:
            self.manifest = json.load(fh)
        index_path = os.path.join(self.root, self.manifest.get("pages_index", "index/pages.jsonl"))
        if not os.path.isfile(index_path):
            raise CorpusError(self._t("index des pages introuvable : %s" % index_path,
                                      "page index not found: %s" % index_path))
        with open(index_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                page = Page(json.loads(line))
                self.pages.append(page)
                self._by_key[(page.version, page.book, page.topic)] = page
                self._by_url[page.url] = page
        if not self.pages:
            raise CorpusError(self._t("corpus vide : %s" % self.root,
                                      "empty corpus: %s" % self.root))

    # -- acces -----------------------------------------------------------
    def versions(self):
        return list(self.manifest.get("versions", []))

    def path_of(self, page):
        return os.path.join(self.root, page.file)

    def raw_bytes(self, page):
        """Octets originaux (decompresses) de la page."""
        path = self.path_of(page)
        if not os.path.isfile(path):
            raise CorpusError(self._t("page absente du corpus : %s" % page.file,
                                      "page missing from the corpus: %s" % page.file))
        try:
            with gzip.open(path, "rb") as fh:
                return fh.read()
        except (OSError, EOFError) as exc:
            raise CorpusError(self._t("page illisible (%s) : %s" % (page.file, exc),
                                      "unreadable page (%s): %s" % (page.file, exc)))

    def html(self, page):
        return self.raw_bytes(page).decode("utf-8", "replace")

    def text(self, page):
        """Texte de la page (balises retirees), mis en cache."""
        key = (page.version, page.book, page.topic)
        if key not in self._text_cache:
            self._text_cache[key] = strip_tags(self.html(page))
        return self._text_cache[key]

    def find(self, version, book, topic):
        return self._by_key.get((version, book, topic))

    def find_url(self, url):
        return self._by_url.get(url)

    def index_pages(self, version):
        """Pages d'index A-Z de la C Library Reference d'une version."""
        return [p for p in self.pages if p.version == version and p.is_index_page]

    def migration_pages(self, version="8.0"):
        return [p for p in self.pages if p.version == version and p.is_migration_page]

    def book_pages(self, version, book):
        return [p for p in self.pages if p.version == version and p.book == book]

    def search_pages(self, version):
        """Pages du corpus d'une version, hors C Library Reference.

        Sert a repondre : "ce symbole est-il decrit ailleurs en 8.0 ?".
        """
        return [p for p in self.pages if p.version == version and p.book != LIB_REF_BOOK]

    def all_pages(self, version):
        return [p for p in self.pages if p.version == version]

    # -- integrite -------------------------------------------------------
    def verify(self, version=None):
        """Verifie le SHA-256 de chaque page contre l'index fige.

        Retourne un dict : ``checked``, ``ok``, ``failed`` (liste de
        (url, attendu, obtenu)).
        """
        checked = 0
        failed = []
        for page in self.pages:
            if version and page.version != version:
                continue
            checked += 1
            try:
                data = self.raw_bytes(page)
            except CorpusError as exc:
                failed.append((page.url, page.sha256,
                               self._t("page illisible : %s" % exc,
                                       "unreadable page: %s" % exc)))
                continue
            got = hashlib.sha256(data).hexdigest()
            if got != page.sha256:
                failed.append((page.url, page.sha256, got))
        return {"checked": checked, "ok": not failed, "failed": failed}

    def verify_sha256sums(self):
        """Verifie le fichier SHA256SUMS (empreintes des fichiers stockes)."""
        path = os.path.join(self.root, "SHA256SUMS")
        if not os.path.isfile(path):
            raise CorpusError(self._t("SHA256SUMS introuvable : %s" % path,
                                      "SHA256SUMS not found: %s" % path))
        failed = []
        checked = 0
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                digest, _, rel = line.partition("  ")
                full = os.path.join(self.root, rel)
                checked += 1
                if not os.path.isfile(full):
                    failed.append((rel, digest, self._t("fichier absent",
                                                        "file missing")))
                    continue
                h = hashlib.sha256()
                with open(full, "rb") as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        h.update(chunk)
                if h.hexdigest() != digest:
                    failed.append((rel, digest, h.hexdigest()))
        return {"checked": checked, "ok": not failed, "failed": failed}


def read_symbols(text):
    """Lit une liste de symboles : un par ligne, ou separes par virgule.

    Les commentaires (``#``) et les lignes vides sont ignores.
    """
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        for chunk in line.replace(";", ",").replace(" ", ",").split(","):
            chunk = chunk.strip()
            if chunk and chunk not in out:
                out.append(chunk)
    return out


IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_*]*$")
