#!/usr/bin/env python3
"""Contre-epreuve ROUGE : casser une regle, montrer que le test echoue.

Un test qui passe toujours ne teste rien. Ce script casse volontairement
dix regles du code, une par une, et verifie que le test charge de la
detester. Il restaure le depot a chaque etape (restauration par git).

Neuf regles se testent sans le corpus complet (elles s'appuient sur le
corpus miniature reconstruit a partir des fixtures). La dixieme verifie
l'integrite du corpus fige livre : elle n'est testable que si le corpus
est present dans le depot ; sinon elle est signalee comme non testable
et n'est pas comptee dans le total.

Usage :
    python3 tools/contre_epreuve.py

Sortie : un tableau "regle cassee -> test -> echec observe".
Code de sortie : 0 si toutes les contre-epreuves testables sont concluantes.
"""

import os
import shutil
import subprocess
import sys

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
     None,
     "tests.test_frozen_corpus.TestFrozenCorpus.test_every_page_matches_its_sha256"),

    ("la mention en prose ne vaut que pour un nom qui ressemble a une API",
     "qnx_portmap/classify.py",
     '                if not self._is_api_name(sym):\n'
     '                    # Un mot anglais rencontre dans une phrase ("argument",\n'
     '                    # "current") ou un nom de parametre suivi de "(" dans un\n'
     '                    # extrait de code n\'est pas un symbole QNX : l\'annoncer\n'
     '                    # comme "decrit ailleurs" serait faux.\n'
     '                    continue',
     '                if not self._is_api_name(sym):\n'
     '                    # regle cassee volontairement : la mention en prose est\n'
     '                    # acceptee quel que soit le nom\n'
     '                    pass',
     "tests.test_classify.TestClassification."
     "test_english_word_mentioned_in_prose_is_not_a_symbol"),

    ("detection des symboles cites en gras",
     "qnx_portmap/extract.py",
     '    for m in _BOLD.finditer(article_of(page_html)):',
     '    for m in []:',
     "tests.test_classify.TestClassification.test_symbol_cited_in_bold"),
]


def sh(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def restore(path, original=None):
    """Remet le fichier dans son etat initial.

    On ecrit directement les octets d'origine : le corpus fige n'est pas
    suivi par git dans l'arbre publiable, `git checkout` ne pourrait donc
    pas le restaurer.
    """
    if original is not None:
        with open(path, "wb") as fh:
            fh.write(original)
    else:
        sh(["git", "checkout", "--", path])


def clean_pycache():
    """Supprime les bytecodes caches.

    Sans cela, Python peut reutiliser un .pyc compiles avant la casse : le
    fichier source etant modifie dans la meme seconde et avec la meme taille
    que la version precedente, le bytecode reutilise masque la casse, et le
    test passerait alors que la regle cassee n'a jamais ete executee.
    """
    for sub in ("qnx_portmap", "tests", "tools", ""):
        d = os.path.join(ROOT, sub, "__pycache__") if sub else os.path.join(ROOT, "__pycache__")
        shutil.rmtree(d, ignore_errors=True)


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
        original = None
        if before is None:
            # corruption binaire d'une page du corpus fige : on altere un octet
            # au milieu du flux compresse, ce qui change le contenu
            # decompresse et donc son empreinte SHA-256
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

    # le depot doit etre propre apres la contre-epreuve
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
