# qnx_portmap — dossier de travail de QX PORTMAP

Sous-dossier du produit **QX PORTMAP** (racine : `qnx-portmap/`).
Lise `../LISEZMOI.md` avant de commencer : il decrit l'outil, l'etat des tests et les
regles (le corpus QNX n'est pas dans le depot, pas de secret, pas de caractere
CJK / cyrillique / grec, aucun acces reseau par defaut).

Ce que contient ce dossier :

- `qnx_portmap/` : le paquet lui-meme (6 modules). Les corrections se font ici.
  La logique de l'outil ne change pas : le depot est publiable tel quel.

Commandes de verification (depuis la racine `qnx-portmap/`) :

```bash
python3 -m unittest discover -s tests -t .   # 90 tests : verts, 18 sautes sans corpus
python3 tools/contre_epreuve.py               # 10/10 contre-epreuves doivent etre concluantes
```
