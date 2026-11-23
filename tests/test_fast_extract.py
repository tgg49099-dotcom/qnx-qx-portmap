"""The fast strip_tags / article_of give the same text as the html.parser
reference (Studio, 23/11/2026).

The html.parser versions made the test suite with the frozen corpus go
from 36 s to more than 170 s; the regular-expression versions must not
change a single character of the output.
"""

import os
import random
import unittest

from qnx_portmap import extract

from .helpers import FIXTURES_DIR

_TOKENS = [
    '<p>', '</p>', '<b class="x">', '</b>', '<article>', '</article>',
    '<article id="a">', '<article/>', '<script>', '</script>',
    '<style type="t">', '</style>', '<!-- c -->', '<!DOCTYPE html>',
    '&amp;', '&lt;', '&nbsp;', '&#65;', ' ', '\n', 'text', 'open()',
    'x > y', '<br/>', '<img src="a>b"/>', '<?xml v?>', '<nav>', '</nav>',
    '<SCRIPT>', '</Script>', '<li role="treeitem">', '</div >',
    '<span class="keyword apiname">accept()</span>',
]


def _same(testcase, html):
    testcase.assertEqual(extract.strip_tags(html), extract._strip_tags_parser(html), html)
    testcase.assertEqual(extract.article_of(html), extract._article_of_parser(html), html)
    art = extract.article_of(html)
    testcase.assertEqual(extract.strip_tags(art), extract._strip_tags_parser(art), html)


class TestFastExtractIsExact(unittest.TestCase):

    def test_known_cases(self):
        for html in [
            "", "plain text", "a &amp; b",
            "<p>a<b>b</b>&amp;c</p><script>x<p>y</script>z",
            "<!DOCTYPE html>a<!-- c -->b",
            "<article>A<article>B</article>C</article><article/>x<article>D",
            '<p title="a>b">t</p>', "a < b &lt; c", "<style/>s",
            "<SCRIPT>q</SCRIPT >r", "<!-- <article>x</article> -->y",
            "<script>'<article>'</script><article>z</article>",
        ]:
            _same(self, html)

    def test_fixtures_of_real_qnx_pages(self):
        names = sorted(os.listdir(FIXTURES_DIR))
        self.assertTrue(names)
        for name in names:
            with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as fh:
                _same(self, fh.read())

    def test_random_markup(self):
        for seed in range(3000):
            rnd = random.Random(seed)
            _same(self, "".join(rnd.choice(_TOKENS) for _ in range(rnd.randint(1, 40))))

    def test_counter_proof_the_check_bites(self):
        """A strip_tags that keeps script contents is caught."""
        html = "<p>a</p><script>var x = 1;</script>"
        self.assertNotEqual("a var x = 1;", extract._strip_tags_parser(html))


if __name__ == "__main__":
    unittest.main()
