# UTILISATION - QX PORTMAP

Guide d'usage court : ce que fait l'outil, comment le lancer, et ce que
signifie exactement la limite de 96 %. Pour l'explication complete du
fonctionnement (index 8.0, renvois "described elsewhere", deux passes de
recherche), voir le [README](../README.md) ; pour le detail de la mesure, voir
[`mesure-J5.md`](mesure-J5.md).

## 1. Ce que fait l'outil

QX PORTMAP prend une liste de symboles QNX (fonctions, variables, constantes)
et repond, pour chacun, par l'**etat de sa documentation dans QNX 8.0** :

| etat | ce que l'outil dit |
|---|---|
| `documented` | le symbole a sa propre page dans la C Library Reference 8.0 |
| `described_elsewhere` | pas de page propre en 8.0, mais la documentation 8.0 le decrit (renvoi de l'index, ou mention dans un autre livre QNX 8.0) |
| `absent` | le symbole etait dans la C Library Reference 7.1 et a disparu du corpus 8.0 |
| `unknown` | introuvable dans le corpus fige : faute de frappe, macro du projet, ou ajout publie apres le 14/11/2026 - l'outil ne devine pas |

Pour chaque symbole trouve, l'outil affiche la **page officielle**, la
**citation exacte** (le texte verbatim de la page) et l'**empreinte SHA-256**
de la page. Il produit ensuite une **liste de travail** : les symboles a
traiter, classes par priorite, avec la page a lire.

L'outil ne compile rien, ne s'execute pas sur cible et n'a besoin d'aucun
acces reseau par defaut.

## 2. Installer

```bash
# depuis la racine du depot
pip install .

# ou, isole, avec pipx (https://pipx.pypa.io)
pipx install .

# ou sans rien installer
python3 -m qnx_portmap --help
```

**Python 3.8 ou plus, bibliotheque standard uniquement.** Aucune dependance,
aucune cle d'API, aucun compte, aucun privilege root.

## 3. Lancer

```bash
# symboles en ligne de commande
qnx-portmap abort accept bzero

# liste dans un fichier (un symbole par ligne, les commentaires # sont ignores)
qnx-portmap --file symbols.txt

# liste sur l'entree standard (exemple : les symboles appeles par un projet)
grep -o '[A-Za-z_][A-Za-z0-9_]*' mon_code.c | sort -u | qnx-portmap --stdin --format json

# formats de sortie
qnx-portmap --format markdown abort accept bzero > etat.md
qnx-portmap --format json abort > etat.json

# controle d'integrite du corpus
qnx-portmap --verify-corpus

# rechargement en ligne (option, jamais utilise par defaut)
qnx-portmap --fresh --fresh-only
```

### Codes de sortie

| code | signification |
|---:|---|
| `0` | tous les symboles analyses sont documentes en 8.0 |
| `1` | au moins un symbole est `absent` ou `unknown` (etat de la documentation, pas erreur du programme) |
| `2` | erreur d'execution : corpus introuvable, aucune liste fournie |

Le code `1` n'est donc **pas** un echec de l'outil : c'est le resultat
attendu quand un symbole a disparu de la documentation.

## 4. Ou est le corpus

L'outil cherche le corpus fige dans cet ordre :

1. la variable d'environnement `QX_PORTMAP_CORPUS` ;
2. le repertoire `corpus/` du depot (a cote du paquet) ;
3. le repertoire `corpus/` du repertoire courant.

Le depot **ne contient pas** de repertoire `corpus/` : la documentation QNX
n'est pas redistribuable (voir `LICENCE-DOCS-QNX.md`). Sans corpus, l'outil
affiche `corpus introuvable` et sort avec le code `2` - il ne devine rien.

### Reconstruire le corpus (une commande, un journal)

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
```

Le script telecharge la documentation officielle QNX 7.1 et 8.0 depuis
`https://www.qnx.com/developers/docs/`, en garde le journal de telechargement,
et calcule l'empreinte SHA-256 de chaque page. Un essai rapide (3 pages par
livre, pour verifier l'acces reseau) :

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded --fresh --fresh-max-pages 3
```

Le corpus reconstruit est verifiable : `qnx-portmap --verify-corpus`.

## 5. La limite de 96 % : ce qu'elle veut dire

Sur l'echantillon de reference (100 symboles QNX reellement appeles par
**cinq depots QNX publics**, commits epingles, liste des 100 symboles dans
[`mesure-J5.md`](mesure-J5.md)) :

| etat | nombre |
|---|---:|
| resolu et cite (page QNX 8.0 + citation + SHA-256) | **96** |
| resolu mais decrit ailleurs | 0 |
| non resolu | 4 |
| **taux** | **96 %** |

Les 4 symboles non resolus sont **honnes** : ils avaient une page dans la C
Library Reference **7.1** et n'en ont plus dans la 8.0 (`ND_NODE_CMP`,
`pthread_sleepon_lock`, `pthread_sleepon_unlock`, `fcfgopen`). L'outil les
declare `absent` avec le lien de leur page 7.1 : il ne les invente pas, il ne
les efface pas. C'est le **plafond honnete** du taux sur cet echantillon.

**Ce que 96 % ne veut pas dire** :

- ce n'est pas une garantie pour votre projet : l'echantillon est un
  echantillon ;
- l'outil analyse la **documentation**, pas le binaire : `absent` signifie
  "absent de la documentation 8.0 figee", pas "absent du systeme" ;
- le corpus est un **instantane** du 14/11/2026 : un symbole publie depuis
  est classe `unknown` tant que le corpus n'est pas reconstruit (`--fresh`) ;
- une mention en prose suffit a classer un symbole `described_elsewhere`, mais
  la citation indique alors `mention` : il faut verifier que le symbole est
  bien un appel de fonction.

## 6. Verifier l'outil (et non le croire)

```bash
python3 -m unittest discover -s tests -t .
```

Sans corpus : 124 tests, dont 21 sautes (le test le dit, il ne ment pas).
Avec le corpus : 124 tests, 0 saut, code de sortie 0.

La preuve **ROUGE -> VERT** (on casse une regle, le test echoue, on restaure,
le test repasse) est dans [`preuves/`](preuves/) ; le detail des mesures et
des methodes dans [`mesure-J4.md`](mesure-J4.md) et
[`mesure-J5.md`](mesure-J5.md).

## 7. Depannage

| symptome | cause | solution |
|---|---|---|
| `corpus introuvable`, code 2 | le corpus n'est pas dans l'arbre | `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`, puis `QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort` |
| `unknown` pour un symbole qui existe | ajoute apres le 14/11/2026 | reconstruire le corpus (`--fresh`) ou verifier l'orthographe |
| `absent` pour un symbole utilise | il a disparu de la 8.0 | lire la page 7.1 citee ; c'est un etat de la documentation, pas une erreur |
| une citation parait mal formatee | le HTML officiel a une mise en forme irreguliere | le texte est verbatim, la ponctuation ne l'est pas toujours |

## 8. Licence

Le code est sous licence MIT (`LICENSE`). **La documentation QNX n'est pas
redistribuee** : voir `LICENCE-DOCS-QNX.md` et `CORPUS-NON-PUBLIE.txt`.
