"""Le README doit montrer une sortie reellement produite, pas un exemple invente.

Ce test rejoue la commande d'exemple du README contre le corpus fige et
compare, ligne a ligne, la sortie obtenue a celle qui est ecrite dans le
README. Si l'outil change, le test echoue : le README doit etre mis a jour.
"""

import io
import os
import unittest
from contextlib import redirect_stdout

from qnx_portmap.cli import main
from qnx_portmap.corpus import default_corpus_dir

from .helpers import CORPUS_ABSENT_MSG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
SYMBOLS = ["abort", "accept", "bzero", "zzz_fonction_inexistante"]


def readme_example_output():
    """Extrait le bloc de sortie de l'exemple du README."""
    with open(README, encoding="utf-8") as fh:
        text = fh.read()
    marker = "Sortie reelle :"
    pos = text.find(marker)
    if pos < 0:
        return None
    start = text.find("```", pos)
    if start < 0:
        return None
    start += 3
    while text[start] == "\n":
        start += 1
    end = text.find("```", start)
    if end < 0:
        return None
    return text[start:end]


@unittest.skipUnless(os.path.isfile(os.path.join(default_corpus_dir(), "MANIFEST.json")),
                     CORPUS_ABSENT_MSG)
class TestReadmeExample(unittest.TestCase):
    def test_readme_shows_the_real_output(self):
        expected = readme_example_output()
        self.assertIsNotNone(expected, "bloc d'exemple introuvable dans le README")

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--corpus", default_corpus_dir()] + SYMBOLS)
        got = buf.getvalue()
        # le chemin du corpus depend de la machine : on le normalise
        root = default_corpus_dir()
        got = got.replace(root, "<CORPUS>")
        expected = expected.replace(root, "<CORPUS>")
        self.assertEqual(expected.strip(), got.strip())
        self.assertEqual(code, 1)   # bzero est absent -> code de sortie 1
