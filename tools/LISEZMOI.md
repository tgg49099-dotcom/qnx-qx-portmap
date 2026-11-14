# tools — dossier de travail de QX PORTMAP

Sous-dossier du produit **QX PORTMAP** (racine : `qnx-portmap/`).
Lise `../LISEZMOI.md` avant de commencer : il decrit l'outil, l'etat des tests et les
regles (pas de modification du corpus `../corpus/`, pas de secret, pas de caractere
CJK / cyrillique / grec, aucun acces reseau par defaut).

Ce que contient ce dossier :

- `tools/` : `build_corpus.py` (construction deterministe du corpus) et `contre_epreuve.py` (contre-epreuve ROUGE).

Commandes de verification (depuis la racine `qnx-portmap/`) :

```bash
python3 -m unittest discover -s tests -t .   # les tests doivent tous passer
python3 tools/contre_epreuve.py               # 8/8 contre-epreuves doivent etre concluantes
```
