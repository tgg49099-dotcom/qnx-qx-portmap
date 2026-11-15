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
        key = re.sub(r"[^A-Za-z0-9._-]", "_", url.replace("https://", ""))[-150:]
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
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(body)
                self.fetched += 1
                time.sleep(self.delay)
                return body
            except (urllib.error.URLError, OSError, ValueError) as exc:
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
            if max_pages and len(pages) >= max_pages:
                break
            for href in dict.fromkeys(re.findall(r'href="([^"]+\.html)"', body)):
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
    records = []
    for name in sorted(os.listdir(cache_dir)):
        if not name.endswith(".html"):
            continue
        m = re.search(r"_docs_(\d+\.\d+)_", name)
        if not m:
            continue
        version = m.group(1)
        path = os.path.join(cache_dir, name)
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", "replace")
        rel = OUT_RELPATH.search(text)
        rel = rel.group(1) if rel else None
        if not rel:
            book = name.split("_docs_", 1)[1].split("_", 1)[1].partition("_topic_")[0]
            topic = name.rsplit("_topic_", 1)[-1]
            rel = "%s/topic/%s" % (book, topic)
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

    sums = []
    for dirpath, dirnames, filenames in os.walk(out_dir):
        dirnames.sort()
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
