"""Tests of the quick mode (``--quick``): indexes and migration guide only.

The network is never used here: a fake downloader serves the pages of a
small synthetic site (always) or of the frozen corpus (when it is present).
The key property is checked on the frozen corpus: the quick mode never
contradicts the full mode, and never prints ``absent``.
"""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from qnx_portmap import quick as quick_mod
from qnx_portmap.classify import (ABSENT, DOCUMENTED, ELSEWHERE, UNKNOWN,
                                  Classifier)
from qnx_portmap.cli import main
from qnx_portmap.corpus import LIB_REF_BOOK, MIGRATION_BOOK, Corpus
from qnx_portmap.quick import (INDEX_LETTERS, QuickError, apply_quick_limits,
                               build_quick_corpus, index_urls, is_quick)
from qnx_portmap.refresh import Downloader

from .helpers import CORPUS_ABSENT_MSG, LIB_REF, USER_GUIDE, index_html, topic_html
from .test_frozen_corpus import CORPUS_DIR, corpus_available

DOCS = "https://www.qnx.com/developers/docs/%s/"


def _index(version, letter, entries=(), elsewhere=()):
    html = index_html(version, list(entries), list(elsewhere))
    return html.replace("/topic/lib-a.html", "/topic/lib-%s.html" % letter)


def fake_site(missing=()):
    """URL -> HTML of a tiny QNX documentation site."""
    site = {}
    for v in ("8.0", "7.1"):
        for letter in INDEX_LETTERS:
            site[(DOCS % v) + "%s/topic/lib-%s.html" % (LIB_REF, letter)] = _index(v, letter)
    site[(DOCS % "8.0") + "%s/topic/lib-a.html" % LIB_REF] = _index(
        "8.0", "a",
        [("frob()", "../../%s/topic/f/frob.html" % LIB_REF, "Frob the widget")],
        [("vanish()", "See", "../../%s/topic/vanish.html" % USER_GUIDE)])
    site[(DOCS % "7.1") + "%s/topic/lib-a.html" % LIB_REF] = _index(
        "7.1", "a",
        [("frob()", "../../%s/topic/f/frob.html" % LIB_REF, "Frob the widget"),
         ("gone()", "../../%s/topic/g/gone.html" % LIB_REF, "Gone since 8.0")])
    site[(DOCS % "8.0") + "%s/topic/f/frob.html" % LIB_REF] = topic_html(
        "8.0", LIB_REF, "f/frob.html", "frob()", "Frob the widget",
        "The frob() function frobs the widget. It returns 0 on success.")
    mig = (DOCS % "8.0") + "%s/topic/" % MIGRATION_BOOK
    site[mig + "about.html"] = topic_html(
        "8.0", MIGRATION_BOOK, "about.html", "Migration", "Migration guide",
        'Read <a href="c_apps.html">C apps</a>.')
    site[mig + "c_apps.html"] = topic_html(
        "8.0", MIGRATION_BOOK, "c_apps.html", "C apps", "C applications",
        "Replace calls to Old_call() in your code.")
    # a page of another book: the full mode would read it, the quick mode never
    site[(DOCS % "8.0") + "%s/topic/bold.html" % USER_GUIDE] = topic_html(
        "8.0", USER_GUIDE, "bold.html", "Bold", "Bold",
        "The Bold_api() call is described here.")
    for url in missing:
        site.pop(url, None)
    return site


class FakeDownloader(Downloader):
    """Serves pages from a dict (or a function), through the real cache."""

    def __init__(self, cache_dir, source):
        Downloader.__init__(self, cache_dir, delay=0)
        self.source = source
        self.requested = []

    def fetch(self, url):
        path = self.cache_path(url)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read()
        self.requested.append(url)
        body = self.source(url) if callable(self.source) else self.source.get(url, "")
        if not body:
            self.failed.append((url, "404"))
            return ""
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        self.fetched += 1
        return body


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class TestQuickSynthetic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qxpm-quick-")
        self.out = os.path.join(self.tmp, "corpus-quick")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build(self, symbols, site=None):
        dl = FakeDownloader(os.path.join(self.out, "cache"), site or fake_site())
        man = build_quick_corpus(self.out, symbols, downloader=dl)
        return dl, man

    def test_index_urls_are_the_26_letters(self):
        urls = index_urls("8.0")
        self.assertEqual(len(urls), 26)
        self.assertTrue(urls[0].endswith("/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html"))
        self.assertTrue(urls[-1].endswith("/topic/lib-z.html"))

    def test_only_indexes_migration_and_own_pages_are_requested(self):
        dl, man = self.build(["frob", "vanish", "gone", "Bold_api", "zzz"])
        # 26 + 26 index pages, 2 migration pages, 1 own page (frob)
        self.assertEqual(len(dl.requested), 55)
        self.assertNotIn((DOCS % "8.0") + "%s/topic/bold.html" % USER_GUIDE,
                         dl.requested)
        self.assertEqual(man["mode"], "quick")
        self.assertEqual(man["pages_total"], 55)

    def test_second_run_uses_the_cache(self):
        self.build(["frob"])
        dl, _ = self.build(["frob"])
        self.assertEqual(dl.requested, [])

    def test_statuses_never_claim_absent(self):
        self.build(["frob", "vanish", "gone", "Bold_api", "Old_call", "zzz"])
        corpus = Corpus(self.out, lang="en")
        self.assertTrue(is_quick(corpus))
        results = Classifier(corpus, lang="en").classify(
            ["frob", "vanish", "gone", "Bold_api", "Old_call", "zzz"])
        before = {r.symbol: r.status for r in results}
        self.assertEqual(before["gone"], ABSENT)       # what the full logic would say
        apply_quick_limits(results, lang="en")
        got = {r.symbol: r for r in results}
        self.assertEqual(got["frob"].status, DOCUMENTED)
        self.assertIn("frobs the widget", got["frob"].detail)
        self.assertEqual(got["vanish"].status, ELSEWHERE)
        self.assertEqual(got["Old_call"].status, ELSEWHERE)   # migration guide
        self.assertEqual(got["gone"].status, UNKNOWN)
        self.assertIn("quick mode", got["gone"].note)
        self.assertIn("7.1", got["gone"].url)                  # the 7.1 fact stays
        self.assertEqual(got["Bold_api"].status, UNKNOWN)      # other book not read
        self.assertEqual(got["zzz"].status, UNKNOWN)
        self.assertFalse([r for r in results if r.status == ABSENT])

    def test_missing_index_page_refuses_to_answer(self):
        bad = (DOCS % "7.1") + "%s/topic/lib-q.html" % LIB_REF
        with self.assertRaises(QuickError):
            self.build(["frob"], site=fake_site(missing=[bad]))

    def test_cli_quick_text_json_and_french(self):
        site = fake_site()
        orig = quick_mod.Downloader
        quick_mod.Downloader = lambda cache, delay=1.0: FakeDownloader(cache, site)
        try:
            code, out, err = run_cli(["--quick", "--quick-out", self.out,
                                      "frob", "gone", "zzz"])
            self.assertEqual(code, 1)                   # unknown symbols
            self.assertIn("quick-mode small corpus", out)
            self.assertIn("quick mode (A-Z indexes and migration guide only", out)
            self.assertNotIn("offline mode", out)
            self.assertNotIn(" absent\n", out)
            self.assertIn("small corpus ready", err)
            code, out, _ = run_cli(["--quick", "--quick-out", self.out,
                                    "--format", "json", "frob"])
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertFalse(data["corpus"]["offline"])
            self.assertEqual(data["corpus"]["mode"], "quick")
            code, out, _ = run_cli(["--quick", "--quick-out", self.out,
                                    "--lang", "fr", "gone"])
            self.assertIn("mode rapide", out)
            self.assertNotIn("absent de la 8.0", out)
            # no symbol: same error as the normal mode, nothing downloaded
            code, _, err = run_cli(["--quick", "--quick-out", self.out])
            self.assertEqual(code, 2)
            self.assertIn("no symbol given", err)
        finally:
            quick_mod.Downloader = orig

    def test_cli_quick_failure_exit_code_2(self):
        bad = (DOCS % "8.0") + "%s/topic/lib-b.html" % LIB_REF
        site = fake_site(missing=[bad])
        orig = quick_mod.Downloader
        quick_mod.Downloader = lambda cache, delay=1.0: FakeDownloader(cache, site)
        try:
            code, out, err = run_cli(["--quick", "--quick-out", self.out, "frob"])
        finally:
            quick_mod.Downloader = orig
        self.assertEqual(code, 2)
        self.assertIn("quick mode not possible", err)
        self.assertEqual(out, "")


@unittest.skipUnless(corpus_available(), CORPUS_ABSENT_MSG)
class TestQuickAgainstFrozenCorpus(unittest.TestCase):
    """On the real documentation: quick never contradicts full."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-quick-real-")
        cls.full = Corpus(CORPUS_DIR, lang="en")

        def serve(url):
            page = cls.full.find_url(url.split("#")[0])
            return cls.full.html(page) if page else ""

        base = Classifier(cls.full, lang="en")
        cls.symbols = sorted(set(base.entries) | set(base.elsewhere)
                             | set(base.prev_entries)) + ["zzz_fonction_inexistante"]
        cls.out = os.path.join(cls.tmp, "corpus-quick")
        cls.dl = FakeDownloader(os.path.join(cls.out, "cache"), serve)
        build_quick_corpus(cls.out, cls.symbols, downloader=cls.dl)
        cls.full_res = {r.symbol: r.status for r in base.classify(cls.symbols)}
        quick = Classifier(Corpus(cls.out, lang="en"), lang="en")
        cls.quick_res = {r.symbol: r.status for r in
                         apply_quick_limits(quick.classify(cls.symbols))}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_no_failed_page(self):
        self.assertEqual(self.dl.failed, [])

    def test_quick_never_contradicts_full(self):
        wrong = [(s, self.quick_res[s], self.full_res[s]) for s in self.symbols
                 if self.quick_res[s] != UNKNOWN
                 and self.quick_res[s] != self.full_res[s]]
        self.assertEqual(wrong, [])

    def test_quick_never_says_absent(self):
        self.assertFalse([s for s, st in self.quick_res.items() if st == ABSENT])

    def test_every_documented_symbol_is_found_by_quick(self):
        missed = [s for s, st in self.full_res.items()
                  if st == DOCUMENTED and self.quick_res[s] != DOCUMENTED]
        self.assertEqual(missed, [])

    def test_readme_symbols(self):
        for sym, want in (("abort", DOCUMENTED), ("accept", ELSEWHERE),
                          ("bzero", UNKNOWN), ("zzz_fonction_inexistante", UNKNOWN)):
            self.assertEqual(self.quick_res[sym], want, sym)
