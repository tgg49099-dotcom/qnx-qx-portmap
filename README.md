# QX PORTMAP

**Ou en est un symbole QNX dans la documentation officielle 8.0 ?**

QX PORTMAP prend une liste de symboles QNX (fonctions, variables, constantes)
et repond, pour chacun, avec la page officielle et la citation exacte :

| Statut | Signification |
|---|---|
| `documented` | le symbole a sa propre page dans la C Library Reference 8.0 |
| `described_elsewhere` | pas de page propre en 8.0, mais la documentation 8.0 le decrit (renvoi "The following are described elsewhere", ou mention dans un autre livre) |
| `absent` | le symbole etait dans la C Library Reference 7.1 et a disparu du corpus 8.0 |
| `unknown` | introuvable dans le corpus fige : faute de frappe, macro du projet, ou ajout posterieur au 14/11/2026 - l'outil ne devine pas |

L'outil produit aussi une **liste de travail de mise a niveau** : les symboles a
traiter, classes par priorite, avec pour chacun la page a lire.

**Par defaut, aucun acces reseau.** L'outil lit un corpus de documentation QNX
fige dans le depot (3 426 pages, 7.1 et 8.0), avec l'empreinte SHA-256 de
chaque page.

---

## Requirements

- **Python 3.8 ou plus.** Aucune dependance a installer : bibliotheque standard
  uniquement (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`).
- **Aucun acces SDP n'est requis.** Ni QNX SDP, ni compilateur, ni carte cible,
  ni compte QNX, ni jeton d'API, ni acces root. L'outil ne compile rien et ne
  s'execute pas sur cible : il lit de la documentation.
- **Le corpus fige** (44,9 Mo compresses, 3 430 fichiers) est livre dans le
  depot, sous `corpus/`. Il est verifiable : `qnx-portmap --verify-corpus`.
- Pour reconstruire le corpus depuis le web (`--fresh`), il faut seulement un
  acces reseau a `https://www.qnx.com/developers/docs/`.

## Installation

```bash
# depuis la racine du depot
pip install .

# ou, isole, avec pipx (https://pipx.pypa.io)
pipx install .

# ou sans rien installer
python3 -m qnx_portmap --help
```

L'outil cherche le corpus fige dans cet ordre :

1. la variable d'environnement `QX_PORTMAP_CORPUS` ;
2. le repertoire `corpus/` du depot (a cote du paquet) ;
3. le repertoire `corpus/` du repertoire courant.

Si le corpus est ailleurs, on le designe explicitement :

```bash
QX_PORTMAP_CORPUS=/chemin/vers/corpus qnx-portmap abort
qnx-portmap --corpus /chemin/vers/corpus abort
```

## Utilisation

```bash
# symboles en ligne de commande
qnx-portmap abort accept bzero

# liste dans un fichier (un symbole par ligne, les commentaires # sont ignores)
qnx-portmap --file symbols.txt

# liste sur l'entree standard
grep -o '[A-Za-z_][A-Za-z0-9_]*' mon_code.c | sort -u | qnx-portmap --stdin --format json

# formats de sortie
qnx-portmap --format markdown abort accept bzero > etat.md
qnx-portmap --format json abort > etat.json

# controle d'integrite du corpus
qnx-portmap --verify-corpus

# rechargement en ligne (option, jamais utilise par defaut)
qnx-portmap --fresh --fresh-only
```

Code de sortie : `0` si tous les symboles analyses sont documentes en 8.0,
`1` si au moins un symbole est absent ou inconnu, `2` en cas d'erreur
(corpus absent, aucune liste fournie).

### Exemple reel execute

Commande lancee le 14/11/2026 sur ce depot :

```
$ qnx-portmap abort accept bzero zzz_fonction_inexistante
```

Sortie reelle :

```
QX PORTMAP - etat des symboles QNX dans la documentation 8.0
corpus fige : /work/qnx-portmap/corpus
pages : 3426 (7.1 : 1200, 8.0 : 2226) - consulte le 2026-11-14 - mode hors ligne

  abort                        documente
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    citation (index C Library Reference 8.0) :
      Raise the SIGABRT signal to terminate program execution
    detail :
      The abort() function causes abnormal process termination to occur by means of the function
      call raise ( SIGABRT ) , unless the signal SIGABRT is caught and the signal handler doesn't
      return. If the signal SIGABRT is caught and the signal handler returns, the signal handler is
      removed and raise ( SIGABRT ) is called again. Note that prior to calling raise() , abort()
      ensures that SIGABRT isn't ignored or blocked.
    note   : present en 7.1 et en 8.0

  accept                       decrit ailleurs
    page   : https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
    voir   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html
    citation (index C Library Reference 8.0, section "described elsewhere") :
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports ) and
      Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
    * cite par le guide de migration officiel 8.0 : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
    note   : decrit dans la documentation 8.0 mais sans page propre dans la C Library Reference

  bzero                        absent de la 8.0
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
    citation (index C Library Reference 7.1, entree d'index) :
      Set the first part of an object to null bytes
    note   : present dans la C Library Reference 7.1, absent de tout le corpus 8.0

  zzz_fonction_inexistante     inconnu du corpus
    note   : introuvable dans le corpus 8.0 fige : symbole inconnu, erreur de saisie, ou ajout posterieur au 2026-11-14

--- Liste de travail de mise a niveau (2 symbole(s)) ---
P2  bzero                      absent de la 8.0
      https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
      Set the first part of an object to null bytes
P3  accept                     decrit ailleurs
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports )
      and Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
      cite par le guide de migration : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
```

Les quatre statuts apparaissent dans la meme sortie : `abort` est documente,
`accept` est decrit ailleurs (renvoi vers la documentation FreeBSD et le guide
io-sock), `bzero` a disparu de la 8.0, et `zzz_fonction_inexistante` est
inconnu du corpus - l'outil le dit au lieu d'inventer une reponse.

## Tests

```bash
python3 -m unittest discover -s tests -t .     # 69 tests, aucune dependance
```

Les tests couvrent le corpus fige (integrite SHA-256 de chaque page) et les cas
limites de la mission : symbole absent, symbole decrit ailleurs, symbole cite
en gras, symbole duplique, liste vide, fichier de corpus corrompu. Un test
verifie aussi que **l'exemple de sortie du README est la sortie reelle** de la
commande ecrite juste au-dessus.

### Contre-epreuve ROUGE

Un test qui passe toujours ne teste rien. `tools/contre_epreuve.py` casse
volontairement une regle du code a la fois et verifie que le test charge
devient **rouge**, puis restaure le depot :

```bash
python3 tools/contre_epreuve.py
```

| Regle cassee | Test qui doit devenir rouge |
|---|---|
| frontiere de mot dans la recherche de citation | `test_respects_word_boundaries` |
| verification du SHA-256 des pages du corpus | `test_detects_a_corrupted_page` |
| verification du fichier `SHA256SUMS` | `test_detects_a_corrupted_sha256sums_file` |
| lecture du tableau "described elsewhere" de l'index | `test_described_elsewhere_symbol` |
| extraction de la section Description | `test_description_is_the_description_section_not_the_library_one` |
| statut inconnu pour un symbole hors corpus | `test_unknown_symbol` |
| deduplication de la liste de symboles | `test_duplicate_symbol_is_reported_once` |
| integrite du corpus fige livre | `test_every_page_matches_its_sha256` |
| la mention en prose ne vaut que pour un nom qui ressemble a une API | `test_english_word_mentioned_in_prose_is_not_a_symbol` |
| detection des symboles cites en gras | `test_symbol_cited_in_bold` |

Les 10 contre-epreuves sont concluantes (`10 / 10`, code de sortie 0) ; la sortie
complete est conservee dans `docs/contre-epreuve-rouge.txt`.

## Le corpus fige

```
corpus/
  MANIFEST.json        metadonnees, comptes par livre et par version, sources
  SHA256SUMS           empreinte SHA-256 de chaque fichier stocke
  NOTICE               avis de droit de copie (voir plus bas)
  index/pages.jsonl    une ligne par page : URL, livre, sujet, SHA-256, taille
  pages/8.0/<livre>/topic/<sujet>.html.gz
  pages/7.1/<livre>/topic/<sujet>.html.gz
```

| Version | Pages | Livres |
|---|---|---|
| 8.0 | 2 226 | C Library Reference (1 600), io-sock (37), user guide (169), system architecture (179), building (190), technotes (19), guide de migration (23), system tuning (9) |
| 7.1 | 1 200 | C Library Reference (1 200) |

Les pages sont compressees en gzip **telles qu'elles ont ete telechargees** le
14/11/2026 ; l'empreinte SHA-256 des octets originaux est inscrite dans
`index/pages.jsonl` et verifiee par `qnx-portmap --verify-corpus`.

Le corpus a ete fige avec `tools/build_corpus.py`, qui est deterministe :
a cache identique, corpus identique.

Le corpus est **fige par un commit git local** (pas de remote, pas de push) :

| Element | Valeur |
|---|---|
| Commit qui fige le corpus | `6a2c442` |
| Fichiers | 3 430 |
| Taille | 44 942 705 octets (44,9 Mo) |
| SHA-256 de `corpus/SHA256SUMS` | `e312cea466329a76053be0160911cf378ffb1c6ea80050a66c66186ca0023efd` |
| SHA-256 de `corpus/MANIFEST.json` | `df762fecc0b67c7f5dd7116ae38daf080b8159843dd9dbf6abcf8971e692b3fc` |
| SHA-256 de `corpus/index/pages.jsonl` | `292185a3cf9bd615f3709d5c52cac54cb87129ad9a5d08f4055a896bfe5d5595` |

L'empreinte SHA-256 de **chaque page** est dans `index/pages.jsonl` :
`qnx-portmap --verify-corpus` les recalcule toutes (3 426 pages, ~2 s).

## Sources

Toutes consultees le **14/11/2026** :

- Documentation QNX OS 8.0 - <https://www.qnx.com/developers/docs/8.0/>
  - C Library Reference : <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/>
  - Guide de migration : <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/>
  - Networking APIs (io-sock) : <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html>
- Documentation QNX OS 7.1 - <https://www.qnx.com/developers/docs/7.1/>
- Documentation FreeBSD (citee par la C Library Reference 8.0 pour les API
  BSD retirees) : <https://man.freebsd.org/>

## Limites

- Le corpus est un **instantane** : il date du 14/11/2026. Un symbole ajoute
  dans une version ulterieure de la documentation est classe `unknown`, jamais
  devine. `--fresh` reconstruit le corpus a partir du site officiel.
- L'analyse porte sur la **documentation**, pas sur le code binaire : un
  symbole `absent` signifie "absent de la documentation 8.0 figee", pas
  "absent du systeme". La documentation 8.0 ne dit pas tout, et l'outil ne
  pretend pas le contraire.
- La recherche dans le corpus ignore les menus de navigation et ne retient que
  le corps des pages. Une mention en prose suffit a classer un symbole
  `described_elsewhere`, mais la citation indique alors `mention` : il faut
  verifier que le symbole est encore un appel de fonction.
- Les versions **6.5** et **6.6** de la documentation QNX ne sont pas publiques
  (`https://www.qnx.com/developers/docs/6.5.0/` redirige vers une page de
  telechargement, `6.6/` renvoie 404). L'outil couvre donc l'axe 7.1 -> 8.0.
- Les citations sont extraites des pages HTML officielles : la mise en forme
  du texte est parfois irreguliere (espaces autour des parentheses, par
  exemple). Le texte est verbatim, la ponctuation ne l'est pas toujours.
- L'outil ne remplace pas la lecture de la documentation : il indique **ou**
  lire, et **ce que** la page dit.

## Licence

Le code est sous licence MIT (voir `LICENSE`).

**Les pages de documentation QNX du repertoire `corpus/` ne sont pas
couvertes par cette licence** : elles restent la propriete de QNX Software
Systems Ltd / BlackBerry Limited (voir `corpus/NOTICE`). Avant toute
publication du depot, il faut soit livrer le code sans le repertoire
`corpus/` (l'utilisateur lance `qnx-portmap --fresh` une fois), soit obtenir
une autorisation de redistribution.

## Comment le statut est decide

1. **Index 8.0** : les pages d'index A-Z de la C Library Reference 8.0
   (26 pages) sont lues. Un symbole trouve dans l'arbre de navigation a sa
   propre page -> `documented`, avec la description courte officielle comme
   citation.
2. **Renvois "described elsewhere"** : le tableau de la meme page d'index
   renvoie vers la documentation FreeBSD ou le guide io-sock pour un certain
   nombre de symbols -> `described_elsewhere`, avec la phrase exacte du renvoi.
3. **Corps du corpus** : sinon, le corps de toutes les pages 8.0 est
   parcouru. Une occurrence de la forme `symbole(` donne `described_elsewhere`
   (citation `appel de fonction`) ; une simple mention en prose donne aussi
   `described_elsewhere` (citation `mention`), **a une condition** : le
   symbole doit ressembler a un nom d'API, c'est-a-dire figurer dans un index
   QNX ou s'ecrire avec une majuscule ou un tiret bas (`pthread_create`,
   `MSG_NOTIFY`). Sans cette condition, un mot anglais rencontre dans une
   phrase (`argument`, `current`, `valid`) serait annonce comme un symbole
   QNX, ce qui serait faux. Une mention en **gras** dans la page officielle
   est signalee comme telle (citation `cite en gras`) : c'est une mention
   deliberee de la documentation.
4. **Absent** : le symbole est dans l'index 7.1 mais nulle part dans le corpus
   8.0 -> `absent`, avec sa page 7.1 et sa description.
5. **Inconnu** : sinon -> `unknown`.

Le guide de migration officiel 8.0 est consulte en plus pour chaque symbole de
la liste de travail : un symbole cite par le guide est signale, car c'est la
seule source officielle qui dit quoi faire.
