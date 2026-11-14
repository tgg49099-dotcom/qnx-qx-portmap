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

V0 fonctionnelle (14/11/2026). 68 tests verts. Contre-epreuve ROUGE : 8/8.

```
python3 -m unittest discover -s tests -t .        # 68 tests
python3 tools/contre_epreuve.py                    # 8/8 contre-epreuves concluantes
qnx-portmap abort accept bzero                    # exemple reel (voir README.md)
```

## Arborescence

| Chemin | Contenu | Taille |
|---|---|---|
| `qnx_portmap/` | le paquet (6 modules, bibliotheque standard uniquement) | ~100 Ko |
| `tests/` | 68 tests, dont 10 sur le corpus fige reel | ~60 Ko |
| `tools/` | construction du corpus, contre-epreuve ROUGE | ~30 Ko |
| `docs/` | sortie conservee de la contre-epreuve | ~3 Ko |
| `corpus/` | **3 426 pages HTML QNX compressees, 44,9 Mo** | 44,9 Mo |

## Corpus fige : a lire avant d'y toucher

`corpus/` est une **copie verbatim de la documentation officielle QNX**
(C Library Reference 7.1 et 8.0, io-sock, guide utilisateur, guide de migration, technotes).
C'est du contenu **tiers** : **QNX Software Systems Ltd / BlackBerry Limited**.

- **Ne pas modifier, deplacer, renommer ni regenerer ces fichiers.** Une seule erreur de
  byte change le SHA-256 de la page et fait echouer `test_every_page_matches_its_sha256`.
- **Ne pas le republier** (il n'est pas couvert par la licence MIT du code) : la decision
  du proprietaire est demandee dans `/rapports/demandes.md`.
- Il est **fige par un commit git local** (`6a2c442`), SHA-256 de chaque page dans
  `corpus/index/pages.jsonl`, empreinte des fichiers dans `corpus/SHA256SUMS`.
- Les pages sont **compressees** : lire avec `gzip.open`, pas `open`.

## Regles du produit

- **Python 3.8+**, bibliotheque standard seulement : aucune dependance a ajouter.
- **Aucun acces reseau** dans le mode par defaut. `--fresh` est une option, pas le mode normal.
- Chaque symbole absent du corpus doit rester `unknown` : **ne jamais deviner** un statut.
- Une citation doit etre **verbatim** de la page officielle, jamais reformulee.
- Un test qui passe toujours ne teste pas : chaque test a au moins un cas qui le fait echouer.
- Aucun caractere CJK / cyrillique / grec dans les fichiers ecrits.
- Aucun secret, aucune cle, aucune URL d'API avec cle.
