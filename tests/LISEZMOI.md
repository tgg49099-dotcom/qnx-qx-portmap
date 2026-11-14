# tests — dossier de travail de QX PORTMAP

Sous-dossier du produit **QX PORTMAP** (racine : `qnx-portmap/`).
Lise `../LISEZMOI.md` avant de commencer : il decrit l'outil, l'etat des tests et les
regles (pas de modification du corpus `../corpus/`, pas de secret, pas de caractere
CJK / cyrillique / grec, aucun acces reseau par defaut).

Ce que contient ce dossier :

- `tests/` : les tests (unittest, sans dependance). Les nouveaux tests vont ici ; ils doivent tous etre verts.

Commandes de verification (depuis la racine `qnx-portmap/`) :

```bash
python3 -m unittest discover -s tests -t .   # les tests doivent tous passer
python3 tools/contre_epreuve.py               # 8/8 contre-epreuves doivent etre concluantes
```
