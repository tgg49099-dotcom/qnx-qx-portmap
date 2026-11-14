# tests — dossier de travail de QX PORTMAP

Sous-dossier du produit **QX PORTMAP** (racine : `qnx-portmap/`).
Lise `../LISEZMOI.md` avant de commencer : il decrit l'outil, l'etat des tests et les
regles (le corpus QNX n'est pas dans le depot, pas de secret, pas de caractere
CJK / cyrillique / grec, aucun acces reseau par defaut).

Ce que contient ce dossier :

- `test_*.py` : les tests (unittest, sans dependance). Les nouveaux tests vont ici ; ils doivent tous etre verts.
- `fixtures/` : 12 extraits courts (1 a 3 lignes) de pages QNX, avec l'URL source et la date
  de consultation. Ce sont les seules traces de documentation QNX presentes dans le depot.
- `helpers.py` : outils communs, dont `build_fixture_corpus()` qui reconstitue un corpus
  miniature au format reel a partir des fixtures, et le message de saut
  `corpus absent : lancer scripts/bootstrap_corpus.sh`.

Commandes de verification (depuis la racine `qnx-portmap/`) :

```bash
python3 -m unittest discover -s tests -t .   # 90 tests : verts, 18 sautes sans corpus
python3 tools/contre_epreuve.py               # 10/10 contre-epreuves doivent etre concluantes
```

Sans le corpus complet, les tests qui en dependent sont **sautes** (jamais en echec) ;
les tests fondes sur les fixtures passent toujours.
