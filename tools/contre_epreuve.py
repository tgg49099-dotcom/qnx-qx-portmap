#!/usr/bin/env python3
"""RED counter-proof: break a rule, show that the test fails.

A test that always passes tests nothing. This script breaks twelve rules of the
code on purpose, one at a time, and checks that the loaded test detects it.
It restores the repository at every step (restoration by git).

Eleven rules are testable without the complete corpus (they rely on the
miniature corpus rebuilt from the fixtures). The twelfth one verifies the
integrity of the frozen corpus shipped with the tool: it is testable only if
the corpus is present in the tree; otherwise it is reported as not testable
and is not counted in the total.

Usage:
    python3 tools/contre_epreuve.py

Output: a table "broken rule -> test -> observed failure".
Exit code: 0 when every testable counter-proof is conclusive.
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (name of the rule, file, before, after, test to run)
BREAKS = [
    ("frontiere de mot dans la recherche de citation",
     "qnx_portmap/extract.py",
     r'    return re.compile(r"(?<![A-Za-z0-9_/\\])%s%s" % (body, tail))',
     r'    return re.compile(r"%s" % body)',
     "tests.test_extract.TestSentencesWith.test_respects_word_boundaries"),

    ("un nom de fichier n'est pas un symbole (recv.c, /dev/socket)",
     "qnx_portmap/extract.py",
     r'    return re.compile(r"(?<![A-Za-z0-9_/\\])%s%s" % (body, tail))',
     r'    return re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % body)',
     "tests.test_symbol_paths.FileNameIsNotSymbol.test_path_is_ignored"),

    ("verification du SHA-256 des pages du corpus",
     "qnx_portmap/corpus.py",
     '            if got != page.sha256:\n'
     '                failed.append((page.url, page.sha256, got))\n'
     '        return {"checked": checked, "ok": not failed, "failed": failed}',
     '            if got != page.sha256:\n'
     '                failed.append((page.url, page.sha256, got))\n'
     '        return {"checked": checked, "ok": True, "failed": failed}',
     "tests.test_corpus.TestMiniCorpus.test_detects_a_corrupted_page"),

    ("verification du fichier SHA256SUMS",
     "qnx_portmap/corpus.py",
     '                if h.hexdigest() != digest:\n'
     '                    failed.append((rel, digest, h.hexdigest()))\n'
     '        return {"checked": checked, "ok": not failed, "failed": failed}',
     '                if h.hexdigest() != digest:\n'
     '                    failed.append((rel, digest, h.hexdigest()))\n'
     '        return {"checked": checked, "ok": True, "failed": failed}',
     "tests.test_corpus.TestMiniCorpus.test_detects_a_corrupted_sha256sums_file"),

    ("lecture du tableau \"described elsewhere\" de l'index",
     "qnx_portmap/extract.py",
     "    for left, right in parser.elsewhere_rows:",
     "    for left, right in []:",
     "tests.test_classify.TestClassification.test_described_elsewhere_symbol"),

    ("extraction de la section Description",
     "qnx_portmap/extract.py",
     '        if "description" not in heading.lower():\n'
     '            continue',
     '        if "description" not in heading.lower():\n'
     '            pass',
     "tests.test_extract.TestParseTopicPage."
     "test_description_is_the_description_section_not_the_library_one"),

    ("statut inconnu pour un symbole hors corpus",
     "qnx_portmap/classify.py",
     "                else:\n                    res.status = UNKNOWN",
     "                else:\n                    res.status = DOCUMENTED",
     "tests.test_classify.TestClassification.test_unknown_symbol"),

    ("deduplication de la liste de symboles",
     "qnx_portmap/classify.py",
     "            if sym and sym not in seen:",
     "            if sym:",
     "tests.test_classify.TestClassification.test_duplicate_symbol_is_reported_once"),

    ("integrite du corpus fige livre",
     "corpus/pages/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html.gz",
     None,                       # corruption binaire, traite a part
     None,
     "tests.test_frozen_corpus.TestFrozenCorpus.test_every_page_matches_its_sha256"),

    ("la mention en prose ne vaut que pour un nom qui ressemble a une API",
     "qnx_portmap/classify.py",
     '                if not self._is_api_name(sym):\n'
     '                    # An English word met in a sentence ("argument",\n'
     '                    # "current") or a parameter name followed by "(" in a\n'
     '                    # code extract is not a QNX symbol: reporting it as\n'
     '                    # "described elsewhere" would be wrong.\n'
     '                    continue',
     '                if not self._is_api_name(sym):\n'
     '                    # rule broken on purpose: the prose mention is\n'
     '                    # accepted whatever the name is\n'
     '                    pass',
     "tests.test_classify.TestClassification."
     "test_english_word_mentioned_in_prose_is_not_a_symbol"),

    ("detection des symboles cites en gras",
     "qnx_portmap/extract.py",
     '    for text in _bold_texts_in_article(page_html, whole_page=whole_page):',
     '    for text in []:',
     "tests.test_classify.TestClassification.test_symbol_cited_in_bold"),

    ("le taux J4 ne compte que les symboles resolus et cites",
     "tools/mesure_j4.py",
     '    ok = sum(1 for r in records if r["etat"] == RESOLU)',
     '    ok = sum(1 for r in records if r["etat"] in (RESOLU, AILLEURS))',
     "tests.test_mesure_j4.TestTauxCompteALaMain."
     "test_le_taux_du_script_egale_le_taux_compte_a_la_main"),
]


def sh(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def restore(path, original=None):
    """Puts the file back in its initial state.

    The original bytes are written directly: the frozen corpus is not
    tracked by git in the publishable tree, so `git checkout` could not
    restore it.
    """
    if original is not None:
        with open(path, "wb") as fh:
            fh.write(original)
    else:
        sh(["git", "checkout", "--", path])


def clean_pycache():
    """Removes the cached bytecodes.

    Without this, Python can reuse a .pyc compiled before the break: the
    source file being modified in the same second and with the same size
    as the previous version, the reused bytecode hides the break, and
    the test would pass although the broken rule was never executed.
    """
    for sub in ("qnx_portmap", "tests", "tools", ""):
        d = os.path.join(ROOT, sub, "__pycache__") if sub else os.path.join(ROOT, "__pycache__")
        shutil.rmtree(d, ignore_errors=True)


def main():
    status = sh(["git", "status", "--porcelain"])
    if status.stdout.strip():
        sys.stderr.write("contre_epreuve: the repository must be clean "
                         "(git status not empty)\n")
        return 2
    print("Contre-epreuve ROUGE de QX PORTMAP")
    print("On casse une regle a la fois ; le test charge doit echouer.\n")
    results = []
    for name, path, before, after, test in BREAKS:
        full = os.path.join(ROOT, path)
        original = None
        if before is None:
            # binary corruption of a page of the frozen corpus: one byte is
            # altered in the middle of the compressed stream, which changes
            # the decompressed content and therefore its SHA-256 fingerprint
            if not os.path.isfile(full):
                results.append((name, test, "NON TESTABLE (corpus absent)", ""))
                print("%-58s %s" % (name, "non testable : corpus absent"))
                continue
            with open(full, "rb") as fh:
                original = fh.read()
            data = bytearray(original)
            mid = len(data) // 2
            data[mid] ^= 0xFF
            with open(full, "wb") as fh:
                fh.write(bytes(data))
        else:
            with open(full, encoding="utf-8") as fh:
                text = fh.read()
            original = text.encode("utf-8")
            if before not in text:
                sys.stderr.write("contre_epreuve: motif introuvable dans %s\n" % path)
                restore(path, original)
                results.append((name, test, "MOTIF INTROUVABLE"))
                continue
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(text.replace(before, after, 1))
        clean_pycache()
        proc = sh([sys.executable, "-B", "-m", "unittest", test])
        restore(path, original)
        clean_pycache()
        red = proc.returncode != 0
        detail = ""
        for line in (proc.stderr or "").splitlines():
            if line.startswith(("FAIL:", "ERROR:", "AssertionError", "Error")):
                detail = line.strip()
                break
        results.append((name, test, ("ECHEC ATTENDU" if red else "PAS D'ECHEC (!!)"),
                        detail))
        print("%-58s %s" % (name, "test rouge OK" if red else "TEST NON ROUGE (!!)"))
        if detail:
            print("    %s" % detail)

    # the repository must be clean after the counter-proof
    final = sh(["git", "status", "--porcelain"])
    print("\nDepot propre apres contre-epreuve : %s"
          % ("oui" if not final.stdout.strip() else "NON"))
    if final.stdout.strip():
        print(final.stdout)
    bad = [r for r in results
           if r[2] != "ECHEC ATTENDU" and not r[2].startswith("NON TESTABLE")]
    tested = [r for r in results if r[2] == "ECHEC ATTENDU"]
    untestable = [r for r in results if r[2].startswith("NON TESTABLE")]
    print("\n%d / %d contre-epreuves concluantes"
          % (len(tested), len(tested) + len(bad)))
    for name, _test, _status, _detail in untestable:
        print("regle non testable ici (corpus absent) : %s" % name)
    return 0 if not bad and not final.stdout.strip() else 1


if __name__ == "__main__":
    sys.exit(main())
