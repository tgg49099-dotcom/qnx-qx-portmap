# QX PORTMAP — dossier produit

**Outil** : etant donne une liste de symboles QNX (fonctions, variables, constantes),
dire pour chacun son etat dans la documentation officielle QNX 8.0 — `documented`,
`described_elsewhere`, `absent` ou `unknown` — avec **la page officielle** et **la citation
exacte**, puis produire la **liste de travail de mise a niveau**.

**Fonction unique** (c'est le critere du concours : outil 2, different de QX Probe).
Entree : une liste de symboles. Sortie : un statut documentaire par symbole. Source : la
documentation officielle QNX 7.1 et 8.0. Aucun acces SDP, aucune compilation, aucun reseau
par defaut.

## Etat

V0 fonctionnelle (14/11/2026). 90 tests verts. Contre-epreuve ROUGE : 10/10 avec le corpus,
9/9 sans le corpus (la regle d'integrite du corpus fige ne peut pas etre testee sans lui).

```
python3 -m unittest discover -s tests -t .        # 90 tests (18 skips sans corpus)
python3 tools/contre_epreuve.py                    # 10/10 contre-epreuves concluantes
qnx-portmap abort accept bzero                    # exemple reel (voir README.md)
```

## Arborescence

Le depot est **publiable** : il ne contient plus la documentation QNX.

| Chemin | Contenu | Taille |
|---|---|---|
| `qnx_portmap/` | le paquet (6 modules, bibliotheque standard uniquement) | ~100 Ko |
| `tests/` | 90 tests, dont 21 sur les fixtures miniatures | ~60 Ko |
| `tests/fixtures/` | 12 extraits courts (1 a 3 lignes) de pages QNX, avec URL et date | ~4 Ko |
| `tools/` | construction du corpus, fixtures, contre-epreuve ROUGE | ~40 Ko |
| `scripts/` | bootstrap du corpus, manifeste publie, controle anti-fuite | ~30 Ko |
| `docs/` | contre-epreuve ROUGE, demonstration, preuves | ~30 Ko |
| `MANIFESTE-PUBLIE.txt` | chemin, taille et SHA-256 de chaque fichier publiable | ~5 Ko |
| `corpus/` | **absent du depot** — reconstruit a la demande, voir ci-dessous | 0 |

## Corpus fige : a lire avant d'y toucher

Le corpus de documentation QNX (3 426 pages HTML officielles, 44,9 Mo compresses) **n'est
plus dans ce depot** : il est (c) QNX Software Systems Ltd / BlackBerry Limited et n'est pas
redistribue. La documentation reste la source, elle est telechargee a la demande depuis le
site officiel.

- L'archive locale du slot (hors depot, jamais publiee) est dans
  `/work/qnx-portmap-corpus-local/corpus/`, avec son ancrage `CORPUS-FIGE.txt`.
- Pour reconstituer un corpus : `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`
  (delai entre les requetes, journal `download.log`, refus d'ecrire dans un corpus fige).
- Pour l'outil : `QX_PORTMAP_CORPUS=/chemin/vers/corpus qnx-portmap ...`.
- **Le corpus fige n'est jamais modifie, jamais republie.** Toute page QNX qui apparait
  dans ce depot est un extrait de 1 a 3 lignes dans `tests/fixtures/`, cite avec son URL et
  la date de consultation.
- Le controle `python3 scripts/controle_fuite_corpus.py --tree . --corpus <corpus>`
  prouve qu'aucun fichier publiable ne contient de page QNX (0 correspondance) et qu'aucun
  fichier ne depasse 4 000 octets de texte QNX verbatim.

## Regles du produit

- **Python 3.8+**, bibliotheque standard uniquement : aucune dependance a ajouter.
- **Aucun acces reseau** dans le mode par defaut. `--fresh` est une option, pas le mode normal.
- Chaque symbole absent du corpus doit rester `unknown` : **ne jamais deviner** un statut.
- Une citation doit etre **verbatim** de la page officielle, jamais reformulee.
- Un test qui passe toujours ne teste pas : chaque test a au moins un cas qui le fait echouer.
- Un test qui exige le corpus complet est **saute** (jamais en echec) quand le corpus est
  absent ; le message est `corpus absent : lancer scripts/bootstrap_corpus.sh`.
- `MANIFESTE-PUBLIE.txt` est **regenere apres chaque changement** :
  `python3 scripts/manifeste_publie.py` (verification : `--check`).
- Aucun caractere CJK / cyrillique / grec dans les fichiers ecrits.
- Aucun secret, aucune cle, aucune URL d'API avec cle.
