"""Tests for fixes and features added by Antigravity.

Covers:
- ``--worklist`` in text, JSON, Markdown, and SARIF modes (EN and FR);
- ``classify.py``: dead variable removal, regex caching, early exit, typo suggestions;
- ``extract.py``: ``html.parser`` migration (non-greedy ``<article>``, no 900-char
  window, ``<script>``/``<style>`` stripping, single quotes, nested elements);
- ``refresh.py``: collision-free cache keys, excluding raw ``cache/`` from
  ``SHA256SUMS``, version filtering, fragment links, atomic cache writes;
- ``corpus.py``: ``zlib.error``, malformed JSON/``SHA256SUMS``, tab-separated symbols;
- ``scan.py`` & ``--scan-dir``: C/H scanning, project-defined exclusion, exact
  ``file:line`` call sites across all output formats and ``--quick``;
- ``--format sarif``: SARIF 2.1.0 output with physical/logical locations.
"""

import ast
import inspect
import io
import json
import os
import re
import shutil
import tempfile
import unittest
import zlib
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from qnx_portmap import classify as classify_mod
from qnx_portmap import quick as quick_mod
from qnx_portmap import refresh as refresh_mod
from qnx_portmap.classify import (ABSENT, DOCUMENTED, ELSEWHERE, UNKNOWN,
                                  Classifier, SymbolResult)
from qnx_portmap.cli import main
from qnx_portmap.corpus import Corpus, CorpusError, read_symbols
from qnx_portmap.extract import (article_of, bold_identifiers, parse_index_page,
                                 parse_topic_page, strip_tags)
from qnx_portmap.refresh import Downloader, build_corpus_from_cache
from qnx_portmap.report import render_markdown, render_sarif
from qnx_portmap.scan import (ScanError, scan_directory, scan_file,
                              strip_c_comments_and_strings)

from .helpers import LIB_REF, USER_GUIDE, build_fixture_corpus, build_mini_corpus, topic_html
from .test_lang_en import _marker_hits, run_cli
from .test_quick import FakeDownloader, fake_site

DOCS_ROOT = "https://www.qnx.com/developers/docs/8.0/"


class TestWorklistOption(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-ag-wl-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_mini_corpus(cls.root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_worklist_text_omits_documented_section_en_and_fr(self):
        code_full, out_full = run_cli(["--corpus", self.root, "frob", "gone", "vanish"])
        code_wl, out_wl = run_cli(["--corpus", self.root, "--worklist", "frob", "gone", "vanish"])
        self.assertEqual(code_full, 1)
        self.assertEqual(code_wl, 1)
        self.assertIn("Frob the widget", out_full)
        self.assertNotIn("Frob the widget", out_wl)
        self.assertNotIn("  frob", out_wl)
        self.assertIn("--- Upgrade worklist (2 symbol(s)) ---", out_wl)
        self.assertIn("P2  gone", out_wl)
        self.assertIn("P3  vanish", out_wl)
        self.assertFalse(_marker_hits(out_wl), _marker_hits(out_wl)[:5])

        code_fr, out_fr = run_cli(["--corpus", self.root, "--lang", "fr",
                                   "--worklist", "frob", "gone", "zzz_nope"])
        self.assertEqual(code_fr, 1)
        self.assertNotIn("Frob the widget", out_fr)
        self.assertIn("--- Liste de travail de mise a niveau (1 symbole(s)) ---", out_fr)
        self.assertIn("(+ 1 symbole(s) inconnu(s)", out_fr)

    def test_worklist_json_omits_symbols_and_includes_worklist_and_unknown(self):
        code, out = run_cli(["--corpus", self.root, "--format", "json",
                             "--worklist", "frob", "gone", "vanish", "zzz_nope"])
        self.assertEqual(code, 1)
        payload = json.loads(out)
        self.assertTrue(payload["worklist_only"])
        self.assertNotIn("symbols", payload)
        self.assertEqual([w["symbol"] for w in payload["worklist"]], ["gone", "vanish"])
        self.assertEqual([u["symbol"] for u in payload["unknown"]], ["zzz_nope"])
        self.assertEqual(payload["counts"]["documented"], 1)
        self.assertEqual(payload["counts"]["absent"], 1)

    def test_worklist_markdown_omits_main_table_en_and_fr(self):
        code, out = run_cli(["--corpus", self.root, "--format", "markdown",
                             "--worklist", "frob", "gone", "vanish"])
        self.assertEqual(code, 1)
        self.assertNotIn("| Symbol | Status 8.0 |", out)
        self.assertNotIn("`frob`", out)
        self.assertIn("### Upgrade worklist", out)
        self.assertIn("| P2 | `gone` |", out)
        self.assertIn("| P3 | `vanish` |", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

        code_fr, out_fr = run_cli(["--corpus", self.root, "--lang", "fr",
                                   "--format", "markdown", "--worklist", "frob", "gone"])
        self.assertEqual(code_fr, 1)
        self.assertNotIn("| Symbole | Statut 8.0 |", out_fr)
        self.assertIn("### Liste de travail de mise a niveau", out_fr)
        self.assertIn("| P2 | `gone` |", out_fr)

    def test_unreadable_file_returns_exit_code_2(self):
        code, out = run_cli(["--corpus", self.root, "--file", "/no/such/file.txt"])
        self.assertEqual(code, 2)
        self.assertIn("unreadable file", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])


class TestClassifyFixesAndImprovements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="qxpm-ag-cls-")
        cls.root = os.path.join(cls.tmp, "corpus")
        build_mini_corpus(cls.root)
        cls.fixture_root = os.path.join(cls.tmp, "fixture-corpus")
        build_fixture_corpus(cls.fixture_root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_no_dead_bold_variable_in_scan_corpus(self):
        src = inspect.getsource(Classifier._scan_corpus)
        tree = ast.parse(src.lstrip())
        assigned = {
            node.id
            for stmt in ast.walk(tree)
            if isinstance(stmt, ast.Assign)
            for target in stmt.targets
            for node in ast.walk(target)
            if isinstance(node, ast.Name)
        }
        self.assertNotIn("bold", assigned)

    def test_regex_compiled_once_per_symbol_not_per_page(self):
        corpus = Corpus(self.root)
        classifier = Classifier(corpus)
        # Warm caches so we only count classification regex compilations.
        for p in corpus.pages:
            classifier._article_text(p)
        real_compile = re.compile
        compiled = []

        def tracking_compile(pattern, flags=0):
            compiled.append(pattern)
            return real_compile(pattern, flags)

        with mock.patch.object(re, "compile", side_effect=tracking_compile):
            res1 = classifier.classify(["bold_api"])
            count_first = sum(1 for p in compiled if "bold_api" in p)
            res2 = classifier.classify(["bold_api"])
            count_second = sum(1 for p in compiled if "bold_api" in p)

        self.assertEqual(res1[0].status, ELSEWHERE)
        self.assertEqual(res2[0].status, ELSEWHERE)
        # Exactly 2 compilations for bold_api (call_form=True and call_form=False),
        # never recompiled per page or on subsequent classify() calls.
        self.assertEqual(count_first, 2)
        self.assertEqual(count_second, count_first)

    def test_scan_corpus_stops_early_once_all_symbols_found(self):
        corpus = Corpus(self.root)
        classifier = Classifier(corpus)
        visited = []
        orig = classifier._article_text

        def spy(page):
            visited.append(page.topic)
            return orig(page)

        classifier._article_text = spy
        found = classifier._scan_corpus(["bold_api"], call_form=False)
        self.assertIn("bold_api", found)
        non_index_80 = [p for p in corpus.pages if p.version == "8.0" and not p.is_index_page]
        self.assertLess(len(visited), len(non_index_80))

    def test_unknown_symbol_typo_suggests_close_official_symbols(self):
        classifier = Classifier(Corpus(self.fixture_root), lang="en")
        res_typo = classifier.classify(["abrot"])[0]
        self.assertEqual(res_typo.status, UNKNOWN)
        self.assertIn("abort", res_typo.suggestions)
        self.assertIn("abort", res_typo.to_dict()["suggestions"])

        res_far = classifier.classify(["zzz_unrelated_symbol"])[0]
        self.assertEqual(res_far.status, UNKNOWN)
        self.assertEqual(res_far.suggestions, [])
        self.assertNotIn("suggestions", res_far.to_dict())

        code, out = run_cli(["--corpus", self.fixture_root, "abrot"])
        self.assertEqual(code, 1)
        self.assertIn("similar symbol: abort", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

        _, out_fr = run_cli(["--corpus", self.fixture_root, "--lang", "fr", "abrot"])
        self.assertIn("symbole proche : abort", out_fr)

    def test_removed_by_migration_guide_serialized_in_to_dict(self):
        classifier = Classifier(Corpus(self.fixture_root), lang="en")
        res = classifier.classify(["_smalloc"])[0]
        self.assertTrue(res.removed_by_migration_guide)
        self.assertTrue(res.to_dict()["removed_by_migration_guide"])


class TestExtractHtmlParser(unittest.TestCase):
    def test_article_of_does_not_greedily_capture_between_siblings(self):
        html = (
            "<html><body>"
            "<article><p>FIRST</p></article>"
            "<aside><p>OUTSIDE_NOISE</p></aside>"
            "<article><p>SECOND</p></article>"
            "</body></html>"
        )
        art = article_of(html)
        text = strip_tags(art)
        self.assertIn("FIRST", text)
        self.assertIn("SECOND", text)
        self.assertNotIn("OUTSIDE_NOISE", text)

    def test_article_of_handles_nested_unclosed_comments_and_scripts(self):
        nested = "<body><article>OUT <article>IN</article> TAIL</article><footer>NO</footer></body>"
        self.assertEqual(strip_tags(article_of(nested)), "OUT IN TAIL")

        unclosed = "<body><nav>X</nav><article><p>UNCLOSED</p></body>"
        self.assertIn("UNCLOSED", strip_tags(article_of(unclosed)))

        commented = "<!-- <article>FAKE</article> --><article><p>REAL</p></article>"
        self.assertEqual(strip_tags(article_of(commented)), "REAL")

        scripted = '<script>var x = "<article>FAKE</article>";</script><article>OK</article>'
        self.assertEqual(strip_tags(article_of(scripted)), "OK")

        custom = "<article-widget>NOPE</article-widget>"
        self.assertEqual(article_of(custom), "")

    def test_strip_tags_removes_script_and_style_content(self):
        html = "<style>.a { color: red; }</style><p>Hello</p><script>alert(1);</script><p>World</p>"
        self.assertEqual(strip_tags(html), "Hello World")

    def test_parse_index_page_handles_shortdesc_far_beyond_900_chars(self):
        padding = '<div class="pad">' + ("x" * 1500) + "</div>"
        html = (
            "<html><body><nav><ul>"
            '<li role="treeitem"><div class="title">'
            '<a href="../../com.qnx.doc.neutrino.lib_ref/topic/f/far_fn.html">'
            '<span class="keyword apiname">far_fn()</span></a>'
            + padding +
            '<div class="wh-tooltip"><p class="shortdesc">Far short description</p></div>'
            "</div></li></ul></nav></body></html>"
        )
        parsed = parse_index_page(html, DOCS_ROOT)
        self.assertIn("far_fn", parsed["entries"])
        self.assertEqual(parsed["entries"]["far_fn"]["desc"], "Far short description")

    def test_parse_index_page_does_not_steal_next_item_shortdesc(self):
        html = (
            "<html><body><nav><ul>"
            '<li role="treeitem"><div class="title">'
            '<a href="../../com.qnx.doc.neutrino.lib_ref/topic/a/no_desc.html">'
            '<span class="keyword apiname">no_desc()</span></a>'
            "</div></li>"
            '<li role="treeitem"><div class="title">'
            '<a href="../../com.qnx.doc.neutrino.lib_ref/topic/b/has_desc.html">'
            '<span class="keyword apiname">has_desc()</span></a>'
            '<p class="shortdesc">Belongs only to has_desc</p>'
            "</div></li>"
            "</ul></nav></body></html>"
        )
        parsed = parse_index_page(html, DOCS_ROOT)
        self.assertEqual(parsed["entries"]["no_desc"]["desc"], "")
        self.assertEqual(parsed["entries"]["has_desc"]["desc"], "Belongs only to has_desc")

    def test_parse_index_page_single_quotes_and_elsewhere_table(self):
        html = (
            "<html><body><nav><ul>"
            "<li role='treeitem'>"
            "<a href='../../com.qnx.doc.neutrino.lib_ref/topic/s/sq_fn.html'>"
            "<span class='keyword apiname'>sq_fn()</span></a>"
            "<p class='shortdesc'>Single quoted</p></li>"
            "</ul></nav><article><table><tr>"
            "<td><span class='keyword apiname'>ext_a(), ext_b()</span></td>"
            "<td>See <a href='https://example.org/ext'>external doc</a></td>"
            "</tr></table></article></body></html>"
        )
        parsed = parse_index_page(html, DOCS_ROOT)
        self.assertEqual(parsed["entries"]["sq_fn"]["desc"], "Single quoted")
        self.assertIn("ext_a", parsed["elsewhere"])
        self.assertIn("ext_b", parsed["elsewhere"])
        self.assertEqual(parsed["elsewhere"]["ext_a"]["urls"], ["https://example.org/ext"])

    def test_parse_topic_page_and_bold_ignore_nav_and_script(self):
        html = (
            "<html><body>"
            "<nav><strong>NAV_BOLD</strong></nav>"
            "<script>var s = '<strong>SCRIPT_BOLD</strong>';</script>"
            "<article>"
            "<h1><span class='keyword apiname'>demo_fn()</span></h1>"
            "<p class='shortdesc'>Short desc</p>"
            "<h2>Library:</h2><p>Link with -lc for this function call in user space applications.</p>"
            "<h2>Description:</h2><p>The demo_fn() function performs a synthetic test action safely.</p>"
            "<p>Use <strong>REAL_BOLD</strong> here.</p>"
            "</article></body></html>"
        )
        parsed = parse_topic_page(html)
        self.assertEqual(parsed["title"], "demo_fn()")
        self.assertEqual(parsed["shortdesc"], "Short desc")
        self.assertTrue(parsed["description"].startswith("The demo_fn() function"))
        self.assertEqual(parsed["names"], ["demo_fn"])
        self.assertEqual(parsed["bold"], ["REAL_BOLD"])
        self.assertEqual(bold_identifiers(html), {"REAL_BOLD"})


class TestRefreshFixes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qxpm-ag-ref-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_cache_path_has_no_collision_for_long_urls(self):
        dl = Downloader(os.path.join(self.tmp, "cache"), delay=0)
        suffix = "/topic/" + ("deep_segment/" * 15) + "shared_page.html"
        url_80 = "https://www.qnx.com/developers/docs/8.0/com.qnx.doc.book_a" + suffix
        url_71 = "https://www.qnx.com/developers/docs/7.1/com.qnx.doc.book_a" + suffix
        url_b = "https://www.qnx.com/developers/docs/8.0/com.qnx.doc.book_b" + suffix
        p80 = dl.cache_path(url_80)
        p71 = dl.cache_path(url_71)
        pb = dl.cache_path(url_b)

        self.assertEqual(len({p80, p71, pb}), 3)
        for path, ver in ((p80, "8.0"), (p71, "7.1"), (pb, "8.0")):
            name = os.path.basename(path)
            self.assertLessEqual(len(name), 255)
            self.assertTrue(name.endswith(".html"))
            self.assertIn("_docs_%s_" % ver, name)

    def test_build_corpus_from_cache_excludes_cache_dir_from_sha256sums(self):
        out_dir = os.path.join(self.tmp, "out")
        cache_dir = os.path.join(out_dir, "cache")
        dl = Downloader(cache_dir, delay=0)
        url = "https://www.qnx.com/developers/docs/8.0/%s/topic/f/frob.html" % LIB_REF
        html = topic_html("8.0", LIB_REF, "f/frob.html", "frob()", "Frob",
                          "The frob() function frobs the widget cleanly.")
        with open(dl.cache_path(url), "w", encoding="utf-8") as fh:
            fh.write(html)

        manifest = build_corpus_from_cache(cache_dir, out_dir)
        self.assertEqual(manifest["pages_total"], 1)
        with open(os.path.join(out_dir, "SHA256SUMS"), encoding="utf-8") as fh:
            sums_text = fh.read()
        self.assertNotIn("cache/", sums_text)
        self.assertIn("index/pages.jsonl", sums_text)
        self.assertIn("pages/8.0/", sums_text)

        # Removing the temporary raw cache must NOT break corpus verification.
        shutil.rmtree(cache_dir)
        corpus = Corpus(out_dir)
        self.assertTrue(corpus.verify()["ok"])
        self.assertTrue(corpus.verify_sha256sums()["ok"])

    def test_build_corpus_from_cache_honors_versions_and_deduplicates(self):
        out_dir = os.path.join(self.tmp, "out-ver")
        cache_dir = os.path.join(self.tmp, "cache-ver")
        dl = Downloader(cache_dir, delay=0)
        u80 = "https://www.qnx.com/developers/docs/8.0/%s/topic/f/frob.html" % LIB_REF
        u71 = "https://www.qnx.com/developers/docs/7.1/%s/topic/f/frob.html" % LIB_REF
        h80 = topic_html("8.0", LIB_REF, "f/frob.html", "frob()", "Frob 8", "Desc 8")
        h71 = topic_html("7.1", LIB_REF, "f/frob.html", "frob()", "Frob 7", "Desc 7")
        with open(dl.cache_path(u80), "w", encoding="utf-8") as fh:
            fh.write(h80)
        # Write a duplicate legacy filename for the same 8.0 page
        with open(os.path.join(cache_dir, "legacy_docs_8.0_%s_topic_f_frob.html" % LIB_REF),
                  "w", encoding="utf-8") as fh:
            fh.write(h80)
        with open(dl.cache_path(u71), "w", encoding="utf-8") as fh:
            fh.write(h71)

        manifest = build_corpus_from_cache(cache_dir, out_dir, versions=("8.0",))
        self.assertEqual(manifest["pages_total"], 1)
        self.assertEqual(manifest["versions"], ["8.0"])

    def test_crawl_book_follows_the_frozen_corpus_link_rule(self):
        """Studio 23/11/2026: the crawler follows "page.html" links, as when
        the frozen corpus was built. Following "page.html#anchor" too made
        quick mode fetch bsps.html, absent from the frozen corpus, so quick
        mode no longer matched full mode (test_quick, test_no_failed_page).
        Change this rule only together with a rebuild of the frozen corpus."""
        base = "https://www.qnx.com/developers/docs/8.0/%s/topic/" % USER_GUIDE
        site = {
            base + "about.html": ('<a href="plain.html">Plain</a>'
                                  '<a href="anchored.html#section1">Anchored</a>'),
            base + "plain.html": "<article><p>Target page</p></article>",
            base + "anchored.html": "<article><p>Only linked with an anchor</p></article>",
        }
        dl = FakeDownloader(os.path.join(self.tmp, "frag-cache"), site)
        pages = dl.crawl_book("8.0", USER_GUIDE, "about.html")
        self.assertEqual(pages, [base + "about.html", base + "plain.html"])

    def test_fetch_atomic_write_leaves_no_tmp_files(self):
        cache_dir = os.path.join(self.tmp, "atomic-cache")
        dl = Downloader(cache_dir, delay=0, retries=1)

        class _Resp(object):
            def read(self):
                return b"<html>ok</html>"

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        with mock.patch.object(refresh_mod.urllib.request, "urlopen",
                               return_value=_Resp()):
            body = dl.fetch("https://www.qnx.com/developers/docs/8.0/book/topic/a.html")
        self.assertEqual(body, "<html>ok</html>")
        files = os.listdir(cache_dir)
        self.assertEqual(len(files), 1)
        self.assertFalse(any(".tmp." in f for f in files))


class TestCorpusHardening(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qxpm-ag-corp-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = os.path.join(self.tmp, "corpus")
        build_mini_corpus(self.root)

    def test_corrupted_manifest_raises_corpus_error(self):
        with open(os.path.join(self.root, "MANIFEST.json"), "w", encoding="utf-8") as fh:
            fh.write("{not valid json")
        with self.assertRaises(CorpusError):
            Corpus(self.root, lang="en")

    def test_corrupted_pages_jsonl_raises_corpus_error(self):
        with open(os.path.join(self.root, "index", "pages.jsonl"), "w", encoding="utf-8") as fh:
            fh.write('{"incomplete": true}\n')
        with self.assertRaises(CorpusError):
            Corpus(self.root, lang="en")

    def test_zlib_error_caught_as_corpus_error(self):
        corpus = Corpus(self.root, lang="en")
        page = corpus.pages[0]
        with mock.patch("qnx_portmap.corpus.gzip.open", side_effect=zlib.error("bad stream")):
            with self.assertRaises(CorpusError):
                corpus.raw_bytes(page)
            res = corpus.verify()
        self.assertFalse(res["ok"])

    def test_malformed_sha256sums_line_is_reported_as_failure(self):
        with open(os.path.join(self.root, "SHA256SUMS"), "a", encoding="utf-8") as fh:
            fh.write("broken_line_without_separator\n")
        corpus = Corpus(self.root, lang="en")
        sums = corpus.verify_sha256sums()
        self.assertFalse(sums["ok"])
        self.assertTrue(any("malformed entry" in f[2] for f in sums["failed"]))

    def test_read_symbols_splits_tabs_and_deduplicates(self):
        text = "frob\tgone\tfrob\nvanish;\tgone # comment\n"
        self.assertEqual(read_symbols(text), ["frob", "gone", "vanish"])


class TestScanDirAndScanner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qxpm-ag-scan-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.corpus_dir = os.path.join(self.tmp, "corpus")
        build_mini_corpus(self.corpus_dir)

    def test_strip_c_comments_and_strings_preserves_line_numbers(self):
        src = (
            "/* line 1\n"
            "   frob(1); line 2 */\n"
            'const char *s = "gone(2);\\n"; // vanish(3);\n'
            "frob(4);\n"
        )
        stripped = strip_c_comments_and_strings(src)
        self.assertEqual(stripped.count("\n"), src.count("\n"))
        self.assertNotIn("gone", stripped)
        self.assertNotIn("vanish", stripped)
        lines = stripped.splitlines()
        self.assertIn("frob(4);", lines[3])

    def test_scan_file_complex_c_constructs(self):
        code = "\n".join([
            "#include <sys/neutrino.h>",
            "#include <stdlib.h>",
            "#define LOCAL_WRAP(x) do { \\",
            "    gone(x); \\",
            "} while (0)",
            "extern int frob(int x);",
            "typedef int (*cb_t)(int);",
            "struct ops { int (*read)(int); } __attribute__((aligned(8)));",
            'extern "C" {',
            "static inline int",
            "inline_helper(int v) {",
            "    return frob(v);",
            "}",
            "}",
            "int knr_helper(a)",
            "    int a;",
            "{",
            "    return a + 1;",
            "}",
            "int (*ret_fnptr(int id))(int) {",
            "    return 0;",
            "}",
            "int entry_point(struct ops *p, struct ops q) {",
            "    /* vanish(0); */",
            '    const char *msg = "vanish(1)";',
            "    p->read(1);",
            "    q.read(2);",
            "    if (sizeof(int) > 0) {",
            "        LOCAL_WRAP(1);",
            "        inline_helper(2);",
            "        knr_helper(3);",
            "        vanish(4);",
            "    }",
            "    return 0;",
            "}",
        ])
        defined, calls, headers = scan_file(code)
        self.assertEqual(headers, ["sys/neutrino.h", "stdlib.h"])
        for name in ("LOCAL_WRAP", "inline_helper", "knr_helper", "ret_fnptr", "entry_point"):
            self.assertIn(name, defined)
        # Prototype on line 6 must NOT be reported as a call; call on line 12 MUST be.
        self.assertEqual(calls.get("frob"), [12])
        # Call inside multi-line #define body on line 4 MUST be reported.
        self.assertEqual(calls.get("gone"), [4])
        # Call inside entry_point on line 32 MUST be reported; comment/string ignored.
        self.assertEqual(calls.get("vanish"), [32])
        # Member accesses, attributes, keywords, typedefs must NOT be reported.
        for bad in ("read", "aligned", "if", "sizeof", "cb_t"):
            self.assertNotIn(bad, calls)
        # An operand followed by an operator and "(" is not a call, and "0x80"
        # does not yield "x80" (seen on a real QNX driver, 26/11/2026:
        # varghes/Raspberry-QNX, Bsp_Rasp/src/hardware/devi, commit 043582a).
        ops = "\n".join([
            "int g(int bits, int n, char *p, char *name, int flags, int nTries) {",
            "    int i = 0;",
            "    if (bits&(1<<i)) i++;",
            "    if (n && (i < 3)) i++;",
            "    while (p && (*p++ != 0)) i++;",
            "    if (!name && !(name = getenv(0))) i++;",
            "    i = (flags & (4 | 8)) ? 1 : 2;",
            "    i = ((0x80 & *(p + 1)) ? 0 : 1);",
            "    if (NULL != (p = malloc(4))) i++;",
            "    for (; nTries && (in8(0x60) & 1); nTries--) i++;",
            "    return i | (InterruptAttach(1, 0, 0, 0, 0));",
            "}",
        ])
        _d, ops_calls, _h = scan_file(ops)
        for bad in ("bits", "n", "p", "name", "flags", "nTries", "x80", "NULL", "i"):
            self.assertNotIn(bad, ops_calls)
        self.assertEqual(ops_calls.get("getenv"), [6])
        self.assertEqual(ops_calls.get("malloc"), [9])
        self.assertEqual(ops_calls.get("in8"), [10])
        self.assertEqual(ops_calls.get("InterruptAttach"), [11])

    def test_scan_directory_walks_c_and_h_and_filters_project_defined(self):
        proj = os.path.join(self.tmp, "proj")
        os.makedirs(os.path.join(proj, "src"))
        os.makedirs(os.path.join(proj, "include"))
        os.makedirs(os.path.join(proj, ".git"))

        with open(os.path.join(proj, "include", "helper.h"), "w", encoding="utf-8") as fh:
            fh.write(
                "#include <sys/neutrino.h>\n"
                "int project_helper(int x);\n"
                "#define ZERO_IT(p) gone(p)\n"
            )
        # Latin-1 byte in comment should not crash scanner
        with open(os.path.join(proj, "src", "helper.c"), "wb") as fh:
            fh.write(
                b"/* commentaire accentu\xe9 */\n"
                b"int project_helper(int x) {\n"
                b"    return frob(x);\n"
                b"}\n"
            )
        with open(os.path.join(proj, "src", "main.c"), "w", encoding="utf-8") as fh:
            fh.write(
                '#include "helper.h"\n'
                "int main(void) {\n"
                "    project_helper(1);\n"
                "    ZERO_IT(0);\n"
                "    vanish();\n"
                "    gone(2);\n"
                "    return 0;\n"
                "}\n"
            )
        # Files that must be ignored
        with open(os.path.join(proj, ".git", "ignored.c"), "w", encoding="utf-8") as fh:
            fh.write("void f(void) { git_hidden_call(); }\n")
        with open(os.path.join(proj, "README.txt"), "w", encoding="utf-8") as fh:
            fh.write("readme_fake_call();\n")

        res = scan_directory(proj)
        self.assertEqual(res.files, ["include/helper.h", "src/helper.c", "src/main.c"])
        self.assertIn("project_helper", res.defined)
        self.assertIn("ZERO_IT", res.defined)
        self.assertIn("main", res.defined)
        self.assertNotIn("project_helper", res.calls)
        self.assertNotIn("ZERO_IT", res.calls)
        self.assertNotIn("git_hidden_call", res.calls)
        self.assertNotIn("readme_fake_call", res.calls)
        self.assertEqual(res.calls["frob"], [{"file": "src/helper.c", "line": 3}])
        self.assertEqual(res.calls["vanish"], [{"file": "src/main.c", "line": 5}])
        self.assertEqual(res.calls["gone"], [
            {"file": "include/helper.h", "line": 3},
            {"file": "src/main.c", "line": 6},
        ])
        self.assertEqual(res.headers, ["sys/neutrino.h"])

    def test_cli_scan_dir_all_formats_en_and_fr(self):
        proj = os.path.join(self.tmp, "cli-proj")
        os.makedirs(proj)
        with open(os.path.join(proj, "app.c"), "w", encoding="utf-8") as fh:
            fh.write(
                "static void local_fn(void) {}\n"
                "int main(void) {\n"
                "    local_fn();\n"
                "    frob();\n"
                "    gone();\n"
                "    vanish();\n"
                "    return 0;\n"
                "}\n"
            )

        # Text (EN)
        code, out = run_cli(["--corpus", self.corpus_dir, "--scan-dir", proj])
        self.assertEqual(code, 1)
        self.assertNotIn("local_fn", out)
        self.assertIn("called : app.c:5", out)
        self.assertIn("called at: app.c:5", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

        # Text --worklist (FR)
        code_fr, out_fr = run_cli(["--corpus", self.corpus_dir, "--lang", "fr",
                                   "--scan-dir", proj, "--worklist"])
        self.assertEqual(code_fr, 1)
        self.assertNotIn("  frob", out_fr)
        self.assertIn("appele dans : app.c:5", out_fr)
        self.assertIn("appele dans : app.c:6", out_fr)

        # JSON
        code_j, out_j = run_cli(["--corpus", self.corpus_dir, "--scan-dir", proj,
                                 "--format", "json"])
        self.assertEqual(code_j, 1)
        data = json.loads(out_j)
        self.assertEqual(data["scan"]["files"], 1)
        self.assertEqual(data["scan"]["defined_ignored"], 2)
        by_sym = {s["symbol"]: s for s in data["symbols"]}
        self.assertEqual(by_sym["gone"]["locations"], [{"file": "app.c", "line": 5}])
        self.assertEqual(by_sym["vanish"]["locations"], [{"file": "app.c", "line": 6}])
        self.assertNotIn("local_fn", by_sym)

        # Markdown (EN + FR)
        _, out_md = run_cli(["--corpus", self.corpus_dir, "--scan-dir", proj,
                             "--format", "markdown"])
        self.assertIn("| File:line |", out_md)
        self.assertIn("app.c:5", out_md)
        self.assertFalse(_marker_hits(out_md), _marker_hits(out_md)[:5])

        _, out_md_fr = run_cli(["--corpus", self.corpus_dir, "--scan-dir", proj,
                                "--format", "markdown", "--lang", "fr"])
        self.assertIn("| Fichier:ligne |", out_md_fr)

        # SARIF
        code_s, out_s = run_cli(["--corpus", self.corpus_dir, "--scan-dir", proj,
                                 "--format", "sarif"])
        self.assertEqual(code_s, 1)
        sarif = json.loads(out_s)
        self.assertEqual(sarif["version"], "2.1.0")
        results = sarif["runs"][0]["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["ruleId"], "QXPM-P2")
        self.assertEqual(results[0]["locations"][0]["physicalLocation"], {
            "artifactLocation": {"uri": "app.c"},
            "region": {"startLine": 5},
        })
        self.assertEqual(results[1]["ruleId"], "QXPM-P3")
        self.assertEqual(results[1]["locations"][0]["physicalLocation"]["region"]["startLine"], 6)

    def test_cli_scan_dir_errors_return_2(self):
        code, out = run_cli(["--corpus", self.corpus_dir, "--scan-dir", "/no/such/dir"])
        self.assertEqual(code, 2)
        self.assertIn("unreadable or missing directory", out)
        self.assertFalse(_marker_hits(out), _marker_hits(out)[:5])

        code_fr, out_fr = run_cli(["--corpus", self.corpus_dir, "--lang", "fr",
                                   "--scan-dir", "/no/such/dir"])
        self.assertEqual(code_fr, 2)
        self.assertIn("repertoire illisible ou introuvable", out_fr)

        empty = os.path.join(self.tmp, "empty-dir")
        os.makedirs(empty)
        code_e, out_e = run_cli(["--corpus", self.corpus_dir, "--scan-dir", empty])
        self.assertEqual(code_e, 2)
        self.assertIn("no symbol given", out_e)

        with self.assertRaises(ScanError):
            scan_directory("/no/such/dir")

    def test_cli_scan_dir_combines_with_quick_mode(self):
        proj = os.path.join(self.tmp, "quick-proj")
        os.makedirs(proj)
        with open(os.path.join(proj, "q.c"), "w", encoding="utf-8") as fh:
            fh.write("int main(void) { frob(); vanish(); return 0; }\n")

        qout = os.path.join(self.tmp, "quick-corpus")
        site = fake_site()
        orig = quick_mod.Downloader
        quick_mod.Downloader = lambda cache, delay=1.0: FakeDownloader(cache, site)
        out_buf, err_buf = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                code = main(["--quick", "--quick-out", qout,
                             "--scan-dir", proj, "--format", "json"])
        finally:
            quick_mod.Downloader = orig
        self.assertEqual(code, 0)
        payload = json.loads(out_buf.getvalue())
        by_sym = {s["symbol"]: s for s in payload["symbols"]}
        self.assertEqual(by_sym["frob"]["status"], DOCUMENTED)
        self.assertEqual(by_sym["frob"]["locations"], [{"file": "q.c", "line": 1}])
        self.assertEqual(by_sym["vanish"]["status"], ELSEWHERE)


class TestSarifAndMarkdownEdgeCases(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qxpm-ag-sarif-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = os.path.join(self.tmp, "corpus")
        build_fixture_corpus(self.root)
        self.corpus = Corpus(self.root, lang="en")

    def test_sarif_levels_p1_p2_p3_unknown_and_worklist_filter(self):
        classifier = Classifier(self.corpus, lang="en")
        results = classifier.classify(["abort", "_smalloc", "bzero", "accept", "zzz_none"])
        worklist = Classifier.worklist(results)

        full_sarif = json.loads(render_sarif(results, worklist, self.corpus))
        rule_ids = [r["ruleId"] for r in full_sarif["runs"][0]["results"]]
        self.assertEqual(rule_ids, ["QXPM-P1", "QXPM-P2", "QXPM-P3", "QXPM-UNK"])
        levels = [r["level"] for r in full_sarif["runs"][0]["results"]]
        self.assertEqual(levels, ["error", "error", "warning", "note"])
        # Logical location fallback when --scan-dir is not used
        self.assertIn("logicalLocations", full_sarif["runs"][0]["results"][0]["locations"][0])

        wl_sarif = json.loads(render_sarif(results, worklist, self.corpus, worklist_only=True))
        wl_rule_ids = [r["ruleId"] for r in wl_sarif["runs"][0]["results"]]
        self.assertEqual(wl_rule_ids, ["QXPM-P1", "QXPM-P2", "QXPM-P3"])

    def test_markdown_sanitizes_newlines_in_citations(self):
        res = SymbolResult("demo")
        res.status = ABSENT
        res.in_71 = True
        res.citation = "Line one\nLine two | pipe"
        md = render_markdown([res], [res], self.corpus, lang="en")
        self.assertIn("Line one Line two \\| pipe", md)


if __name__ == "__main__":
    unittest.main()
