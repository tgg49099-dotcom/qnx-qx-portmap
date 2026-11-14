#!/usr/bin/env python3
"""Contre-epreuve ROUGE : casser une regle, montrer que le test echoue.

Un test qui passe toujours ne teste rien. Ce script casse volontairement
huit regles du code, une par une, et verifie que le test charge de la
detester. Il restaure le depot a chaque etape (restauration par git).

Usage :
    python3 tools/contre_epreuve.py

Sortie : un tableau "regle cassee -> test -> echec observe".
Code de sortie : 0 si toutes les contre-epreuves sont concluantes.
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (nom de la regle, fichier, avant, apres, test a lancer)
BREAKS = [
    ("frontiere de mot dans la recherche de citation",
     "qnx_portmap/extract.py",
     'pattern = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % body)',
     'pattern = re.compile(r"%s" % body)',
     "tests.test_extract.TestSentencesWith.test_respects_word_boundaries"),

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
     "    for m in _ROW.finditer(article):",
     '    for m in _ROW.finditer(""):',
     "tests.test_classify.TestClassification.test_described_elsewhere_symbol"),

    ("extraction de la section Description",
     "qnx_portmap/extract.py",
     '        if "description" not in strip_tags(hm.group(1)).lower():\n'
     '            continue',
     '        if "description" not in strip_tags(hm.group(1)).lower():\n'
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
     "            if sym and sym not in unique:",
     "            if sym:",
     "tests.test_classify.TestClassification.test_duplicate_symbol_is_reported_once"),

    ("integrite du corpus fige livre",
     "corpus/pages/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html.gz",
     None,                       # corruption binaire, traite a part
     "tests.test_frozen_corpus.TestFrozenCorpus.test_every_page_matches_its_sha256"),
]


def sh(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def restore(path):
    sh(["git", "checkout", "--", path])


def main():
    status = sh(["git", "status", "--porcelain"])
    if status.stdout.strip():
        sys.stderr.write("contre_epreuve: le depot doit etre propre "
                         "(git status non vide)\n")
        return 2
    print("Contre-epreuve ROUGE de QX PORTMAP")
    print("On casse une regle a la fois ; le test charge doit echouer.\n")
    results = []
    for name, path, before, after, test in BREAKS:
        full = os.path.join(ROOT, path)
        if before is None:
            # corruption binaire d'une page du corpus fige
            with open(full, "ab") as fh:
                fh.write(b"\x00")
        else:
            with open(full, encoding="utf-8") as fh:
                text = fh.read()
            if before not in text:
                sys.stderr.write("contre_epreuve: motif introuvable dans %s\n" % path)
                restore(path)
                results.append((name, test, "MOTIF INTROUVABLE"))
                continue
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(text.replace(before, after, 1))
        proc = sh([sys.executable, "-m", "unittest", test])
        restore(path)
        red = proc.returncode != 0
        detail = ""
        for line in (proc.stderr or "").splitlines():
            if line.startswith(("FAIL:", "AssertionError", "Error")):
                detail = line.strip()
                break
        results.append((name, test, ("ECHEC ATTENDU" if red else "PAS D'ECHEC (!!)"),
                        detail))
        print("%-58s %s" % (name, "test rouge OK" if red else "TEST NON ROUGE (!!)"))
        if detail:
            print("    %s" % detail)

    # le depot doit etre propre apres la contre-epreuve
    final = sh(["git", "status", "--porcelain"])
    print("\nDepot propre apres contre-epreuve : %s"
          % ("oui" if not final.stdout.strip() else "NON"))
    if final.stdout.strip():
        print(final.stdout)
    bad = [r for r in results if r[2] != "ECHEC ATTENDU"]
    print("\n%d / %d contre-epreuves concluantes"
          % (len(results) - len(bad), len(results)))
    return 0 if not bad and not final.stdout.strip() else 1


if __name__ == "__main__":
    sys.exit(main())
