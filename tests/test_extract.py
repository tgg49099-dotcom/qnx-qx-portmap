"""Tests de l'extraction : du HTML QNX vers les faits utiles."""

import unittest

from qnx_portmap.extract import (article_of, parse_index_page, parse_topic_page,
                                 sentences_with, strip_tags)

DOCS_ROOT = "https://www.qnx.com/developers/docs/8.0/"


class TestStripTags(unittest.TestCase):
    def test_removes_markup_and_decodes_entities(self):
        html = "<p>Le <span class='k'>SIGABRT</span> &amp; co</p>"
        self.assertEqual(strip_tags(html), "Le SIGABRT & co")

    def test_collapses_whitespace(self):
        self.assertEqual(strip_tags("<p>a\n\n   b</p>"), "a b")


class TestArticle(unittest.TestCase):
    def test_keeps_only_article(self):
        html = "<body><nav>MENU</nav><article>CONTENU</article></body>"
        self.assertEqual(strip_tags(article_of(html)), "CONTENU")

    def test_returns_empty_without_article(self):
        self.assertEqual(article_of("<body><nav>MENU</nav></body>"), "")


class TestParseIndexPage(unittest.TestCase):
    def setUp(self):
        html = (
            "<html><body><nav><ul>"
            '<li role="treeitem"><div class="topicref"><div class="title">'
            '<a href="../../com.qnx.doc.neutrino.lib_ref/topic/a/abort.html">'
            '<span class="keyword apiname">abort()</span></a>'
            '<div class="wh-tooltip"><p class="shortdesc"><em class="ph i">'
            "Raise the SIGABRT signal</em></p></div></div></div></li>"
            '<li role="treeitem"><div class="topicref"><div class="title">'
            '<a href="../../com.qnx.doc.neutrino.lib_ref/topic/a/_amblksiz.html">'
            '<var class="keyword varname">_amblksiz</var></a>'
            '<div class="wh-tooltip"><p class="shortdesc"><em class="ph i">'
            "The arena size</em></p></div></div></div></li>"
            "</ul></nav><article><p>x</p></article></body></html>")
        self.parsed = parse_index_page(html, DOCS_ROOT)

    def test_finds_function_entry(self):
        entry = self.parsed["entries"]["abort"]
        self.assertEqual(entry["kind"], "function")
        self.assertEqual(
            entry["url"],
            "https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html")
        self.assertEqual(entry["desc"], "Raise the SIGABRT signal")

    def test_finds_variable_entry(self):
        entry = self.parsed["entries"]["_amblksiz"]
        self.assertEqual(entry["kind"], "variable")
        self.assertEqual(entry["desc"], "The arena size")

    def test_ignores_navigation_letters(self):
        self.assertNotIn("A", self.parsed["entries"])


class TestParseIndexElsewhere(unittest.TestCase):
    def test_finds_described_elsewhere_row(self):
        html = (
            "<html><body><article><p>The following are described elsewhere:</p>"
            "<table><tbody><tr>"
            '<td><span class="+ topic/keyword pr-d/apiname keyword apiname">'
            "accept(), accept4()</span></td>"
            '<td>FreeBSD documentation (<a href="https://man.freebsd.org/cgi/man.cgi?query=accept">'
            "https://man.freebsd.org</a>) and Networking APIs.</td>"
            "</tr></tbody></table></article></body></html>")
        parsed = parse_index_page(html, DOCS_ROOT)
        self.assertIn("accept", parsed["elsewhere"])
        self.assertIn("accept4", parsed["elsewhere"])
        info = parsed["elsewhere"]["accept"]
        self.assertIn("FreeBSD documentation", info["text"])
        self.assertEqual(info["urls"],
                         ["https://man.freebsd.org/cgi/man.cgi?query=accept"])


class TestParseTopicPage(unittest.TestCase):
    def setUp(self):
        html = (
            "<html><body><article>"
            '<h1><span class="+ topic/keyword pr-d/apiname keyword apiname">abort()</span></h1>'
            '<p class="- topic/shortdesc shortdesc"><em class="+ topic/ph hi-d/i ph i">'
            "Raise the SIGABRT signal</em></p>"
            "<section><h2>Library:</h2><p>Use the -l c option.</p></section>"
            "<section><h2>Description:</h2>"
            '<p class="- topic/p p">The abort() function causes abnormal process '
            "termination to occur when the signal is not caught.</p></section>"
            "<section><h2>Caveats:</h2><p>On <strong>bolded</strong> systems.</p></section>"
            "</article></body></html>")
        self.parsed = parse_topic_page(html)

    def test_title(self):
        self.assertEqual(self.parsed["title"], "abort()")

    def test_shortdesc(self):
        self.assertEqual(self.parsed["shortdesc"], "Raise the SIGABRT signal")

    def test_description_is_the_description_section_not_the_library_one(self):
        self.assertTrue(self.parsed["description"].startswith("The abort() function"))
        self.assertNotIn("-l c", self.parsed["description"])

    def test_bold_text_is_kept(self):
        self.assertIn("bolded", self.parsed["bold"])


class TestSentencesWith(unittest.TestCase):
    def test_finds_the_sentence_containing_the_symbol(self):
        text = "First sentence here. The bolded symbol is here. Last one."
        out = sentences_with(text, "bolded")
        self.assertEqual(len(out), 1)
        self.assertIn("The bolded symbol", out[0])

    def test_respects_word_boundaries(self):
        # "boldedish" contient "bolded" mais n'est pas le symbole cherche
        text = "The boldedish symbol is here."
        self.assertEqual(sentences_with(text, "bolded"), [])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(sentences_with("nothing here", "absent"), [])


if __name__ == "__main__":
    unittest.main()
