"""Online reload of the corpus (option ``--fresh``).

This mode is never used by default: QX PORTMAP works on the frozen corpus
shipped in the repository. ``--fresh`` rebuilds that corpus from the
official documentation, to update the tool after a new version of QNX.

The download is done with the public API of the QNX documentation site
(urllib), without authentication, like a documentation reader.
"""

import collections
import gzip
import hashlib
import http.client
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# Documentation books used for the 8.0 corpus, and their granularity.
BOOKS = [
    ("com.qnx.doc.neutrino.lib_ref", "about.html"),
    ("com.qnx.doc.neutrino.io_sock", "about.html"),
    ("com.qnx.doc.neutrino.user_guide", "about.html"),
    ("com.qnx.doc.neutrino.sys_arch", "about.html"),
    ("com.qnx.doc.neutrino.building", "about.html"),
    ("com.qnx.doc.neutrino.technotes", "about.html"),
    ("com.qnx.doc.qnxsdp.migration", "about.html"),
    ("com.qnx.doc.system.tuning", "about.html"),
]
BOOKS_71 = [("com.qnx.doc.neutrino.lib_ref", "about.html")]

OUT_RELPATH = re.compile(r'name="wh-out-relpath"\s+content="([^"]+)"')
_CACHE_HASH_SUFFIX = re.compile(r"__[0-9a-f]{16}(\.html)$")
_HTML_HREF = re.compile(r'href="([^"]+\.html(?:#[^"]*)?)"')


class Downloader(object):
    """Downloads the pages of a documentation book and caches them."""

    def __init__(self, cache_dir, delay=0.1, timeout=45, retries=3):
        self.cache_dir = cache_dir
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.fetched = 0
        self.failed = []
        os.makedirs(cache_dir, exist_ok=True)

    def cache_path(self, url):
        """Collision-free cache file path for *url*.

        Preserves the sanitized URL prefix (including ``_docs_<version>_``)
        and ``.html`` extension while appending a 16-hex SHA-256 digest of
        the full URL so arbitrarily long URLs never collide or exceed
        filesystem filename limits.
        """
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        stripped = re.sub(r"^https?://", "", url)
        clean = re.sub(r"[^A-Za-z0-9._-]", "_", stripped)
        ext = ".html" if clean.endswith(".html") else ""
        stem = clean[:-len(ext)] if ext else clean
        if len(stem) > 160:
            stem = stem[:95] + "_" + stem[-64:]
        key = "%s__%s%s" % (stem, digest, ext)
        return os.path.join(self.cache_dir, key)

    def fetch(self, url):
        path = self.cache_path(url)
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8", "replace")
                tmp_path = path + ".tmp.%d" % os.getpid()
                try:
                    with open(tmp_path, "w", encoding="utf-8") as fh:
                        fh.write(body)
                    os.replace(tmp_path, path)
                except OSError:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
                    raise
                self.fetched += 1
                time.sleep(self.delay)
                return body
            except (urllib.error.URLError, http.client.HTTPException,
                    OSError, ValueError) as exc:
                # http.client.HTTPException covers IncompleteRead (a page cut
                # off in the middle by the network): it is not an OSError, and
                # without it one cut page stopped the whole corpus download
                # with a traceback (measured on 17/11/2026, page 1545 of 3426).
                if attempt == self.retries - 1:
                    self.failed.append((url, str(exc)))
                    return ""
                time.sleep(2 * (attempt + 1))
        return ""

    def crawl_book(self, version, book, seed="about.html", max_pages=None):
        """Walks a book and returns the list of the URLs seen."""
        base = "https://www.qnx.com/developers/docs/%s/%s/topic/" % (version, book)
        start = base + seed
        seen = {start}
        queue = collections.deque([start])
        pages = []
        while queue:
            url = queue.popleft()
            body = self.fetch(url)
            if not body:
                continue
            pages.append(url)
            if max_pages is not None and max_pages > 0 and len(pages) >= max_pages:
                break
            for href in dict.fromkeys(_HTML_HREF.findall(body)):
                if href.startswith("#"):
                    continue
                nxt = urllib.parse.urljoin(url, href).split("#")[0]
                if not nxt.startswith(base):
                    continue
                if nxt not in seen and ".." not in nxt:
                    seen.add(nxt)
                    queue.append(nxt)
        return pages

    def crawl(self, version="8.0", books=None, max_pages=None, progress=None):
        books = books if books is not None else BOOKS
        urls = []
        for book, seed in books:
            got = self.crawl_book(version, book, seed, max_pages)
            urls.extend(got)
            if progress:
                progress("  %-42s %d pages" % (book, len(got)))
        return urls


def build_corpus_from_cache(cache_dir, out_dir, versions=("8.0", "7.1")):
    """Writes the frozen corpus from a cache of downloaded pages.

    Returns the written manifest.
    """
    os.makedirs(out_dir, exist_ok=True)
    index_dir = os.path.join(out_dir, "index")
    os.makedirs(index_dir, exist_ok=True)
    allowed_versions = set(versions) if versions else None
    records = []
    seen_pages = set()
    for name in sorted(os.listdir(cache_dir)):
        if not name.endswith(".html"):
            continue
        m = re.search(r"_docs_(\d+\.\d+)_", name)
        if not m:
            continue
        version = m.group(1)
        if allowed_versions is not None and version not in allowed_versions:
            continue
        path = os.path.join(cache_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", "replace")
        rel = OUT_RELPATH.search(text)
        rel = rel.group(1) if rel else None
        if not rel:
            book = name.split("_docs_", 1)[1].split("_", 1)[1].partition("_topic_")[0]
            topic = _CACHE_HASH_SUFFIX.sub(r"\1", name.rsplit("_topic_", 1)[-1])
            rel = "%s/topic/%s" % (book, topic)
        page_key = (version, rel)
        if page_key in seen_pages:
            continue
        seen_pages.add(page_key)
        dest = os.path.join(out_dir, "pages", version, rel + ".gz")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(raw)
        records.append({
            "version": version,
            "book": rel.split("/topic/")[0],
            "topic": rel.split("/topic/", 1)[1] if "/topic/" in rel else rel,
            "url": "https://www.qnx.com/developers/docs/%s/%s" % (version, rel),
            "file": os.path.relpath(dest, out_dir).replace(os.sep, "/"),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        })
    with open(os.path.join(index_dir, "pages.jsonl"), "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    out_abs = os.path.realpath(out_dir)
    cache_abs = os.path.realpath(cache_dir)
    sums = []
    for dirpath, dirnames, filenames in os.walk(out_dir):
        dirpath_abs = os.path.realpath(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames
            if os.path.realpath(os.path.join(dirpath_abs, d)) != cache_abs
            and not (dirpath_abs == out_abs and d == "cache")
        )
        for fn in sorted(filenames):
            if fn in ("SHA256SUMS", "MANIFEST.json"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, out_dir).replace(os.sep, "/")
            h = hashlib.sha256()
            with open(full, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            sums.append("%s  %s" % (h.hexdigest(), rel))
    with open(os.path.join(out_dir, "SHA256SUMS"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sums) + "\n")

    by_version = {}
    by_book = {}
    for rec in records:
        by_version[rec["version"]] = by_version.get(rec["version"], 0) + 1
        by_book[rec["book"]] = by_book.get(rec["book"], 0) + 1
    manifest = {
        "corpus": "QNX documentation (C Library Reference et livres lies)",
        "tool": "QX PORTMAP",
        "built": time.strftime("%Y-%m-%d"),
        "consulted": time.strftime("%Y-%m-%d"),
        "docs_root": {v: "https://www.qnx.com/developers/docs/%s/" % v for v in sorted(by_version)},
        "versions": sorted(by_version),
        "pages_total": len(records),
        "pages_by_version": by_version,
        "pages_by_book": dict(sorted(by_book.items(), key=lambda kv: (-kv[1], kv[0]))),
        "files": len(sums),
        "sha256sums": "SHA256SUMS",
        "pages_index": "index/pages.jsonl",
        "integrity": "sha256 dans index/pages.jsonl = empreinte des octets originaux "
                     "telecharges ; SHA256SUMS = empreinte des fichiers stockes (gzip)",
        "note": "Copie de pages de documentation QNX (c) QNX Software Systems Ltd / "
                "BlackBerry Limited. Non redistribuable sans autorisation : voir README.",
    }
    with open(os.path.join(out_dir, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return manifest
