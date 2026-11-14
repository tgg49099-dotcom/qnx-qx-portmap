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
fige, local (3 426 pages, 7.1 et 8.0), avec l'empreinte SHA-256 de chaque page.

**La documentation QNX n'est pas redistribuee avec ce depot.** Le corpus se
reconstruit a la demande depuis le site officiel QNX, avec une commande et un
journal de telechargement ; voir [Corpus QNX](#corpus-qnx--non-distribue).
Le depot contient le code, les tests, 12 **fixtures miniatures** (extraits
courts de pages QNX, avec URL et date) et la procedure de reconstruction.

**Mesure sur du code reel** : sur 100 symboles QNX reellement appeles par
cinq depots QNX publics, l'outil en resout et cite **96 %**
([`docs/mesure-J5.md`](docs/mesure-J5.md)). La premiere mesure, sur le meme
echantillon, en resolvait 93 % ([`docs/mesure-J4.md`](docs/mesure-J4.md)) :
la difference est expliquee plus bas.

---

## Requirements

- **Python 3.8 ou plus.** Aucune dependance a installer : bibliotheque standard
  uniquement (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`).
- **Aucun acces SDP n'est requis.** Ni QNX SDP, ni compilateur, ni carte cible,
  ni compte QNX, ni jeton d'API, ni acces root. L'outil ne compile rien et ne
  s'execute pas sur cible : il lit de la documentation.
- **Le corpus n'est pas livre avec le depot.** La documentation QNX est (c) QNX
  Software Systems Ltd / BlackBerry Limited et n'est pas redistribuable : voir
  `LICENCE-DOCS-QNX.md` et `CORPUS-NON-PUBLIE.txt`. Il se reconstruit avec une
  seule commande, qui demande un acces reseau a
  `https://www.qnx.com/developers/docs/` :
  `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`.
- Le corpus reconstruit est verifiable : `qnx-portmap --verify-corpus`.

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

Le depot **ne contient pas** de repertoire `corpus/` : apres avoir reconstruit
le corpus (voir plus bas), on le designate explicitement :

```bash
QX_PORTMAP_CORPUS=/chemin/vers/corpus qnx-portmap abort
qnx-portmap --corpus /chemin/vers/corpus abort
```

Sans corpus, l'outil ne devine rien : il affiche `corpus introuvable` et
sort avec le code 2.

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
corpus fige : <CORPUS>
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

`<CORPUS>` designe le repertoire du corpus utilise pour la commande
(`QX_PORTMAP_CORPUS=...`) : le chemin depend de la machine. Ce bloc est
compare ligne a ligne a la sortie reelle par `tests/test_readme.py`, qui
echoue si l'outil change.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

124 tests, aucune dependance, **aucun acces reseau**. Deux cas :

| Situation | Resultat |
|---|---|
| Corpus present (dans `corpus/`, ou via `QX_PORTMAP_CORPUS`) | 124 tests, **0 skip**, code de sortie 0 |
| Corpus absent | 124 tests, **25 skip**, code de sortie 0 |

Les 25 tests sautes sont ceux qui exigent le corpus complet (integrite
SHA-256 de chacune des 3 426 pages, chiffres de l'index 8.0 et 7.1, reponses
sur des symboles reels). Ils sont **sautes, jamais en echec**, avec le message :

```
corpus absent : lancer scripts/bootstrap_corpus.sh
```

Les 85 autres tests passent **sans corpus**. Parmi eux, les 21 tests de
`tests/test_fixtures.py` travaillent sur les **fixtures miniatures** : 12
extraits courts (1 a 3 lignes) de pages QNX reelles, ranges dans
`tests/fixtures/`, avec l'URL source, la date de consultation et l'empreinte
SHA-256 de la page complete dont l'extrait est tire. Ces tests reconstruisent
un petit corpus a partir de ces extraits et font tourner le vrai
classificateur dessus : `abort` est documente, `errno` est une variable,
`accept` est decrit ailleurs, `bzero` a disparu, `rw_interrupt` est cite en
gras, `getprotobyname_r` est appele dans un autre livre, `_smalloc` est cite
par le guide de migration, et le mot anglais `entire` n'est **pas** annonce
comme un symbole.

Les tests couvrent aussi les cas limites de la mission : symbole absent,
symbole decrit ailleurs, symbole cite en gras, symbole duplique, liste vide,
fichier de corpus corrompu. Un test verifie aussi que **l'exemple de sortie
du README est la sortie reelle** de la commande ecrite juste au-dessus.

Pour tout lancer avec le corpus complet :

```bash
QX_PORTMAP_CORPUS=/chemin/vers/corpus python3 -m unittest discover -s tests -t .
```

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
| le taux J4 ne compte que les symboles resolus et cites | `test_le_taux_du_script_egale_le_taux_compte_a_la_main` |
| le taux J5 vaut 96 % sur le meme echantillon que J4 | `test_le_taux_publie_est_96_pour_cent` |
| l'echantillon J5 est strictement celui de J4 | `test_echantillon_identique_a_j4` |
| une page QNX 8.0 verifiee dans le corpus fige est exigee pour chaque conversion | `test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256` |

Les 11 contre-epreuves sont concluantes (`11 / 11`, code de sortie 0) ; la sortie
complete est conservee dans `docs/contre-epreuve-rouge.txt`.

Sur l'arbre **sans** corpus, 10 des 11 regles restent contre-prouvees (`10 / 10`,
code de sortie 0) : la regle "integrite du corpus fige livre" porte sur les
3 426 pages, donc sur le corpus lui-meme ; sans lui, il n'y a rien a corrompre
et le test correspondant est saute. Les deux executions sont dans
`docs/contre-epreuve-rouge.txt`.

## Corpus QNX : non distribue

> **the QNX documentation is not redistributed; it is downloaded from the official site on demand**

La documentation QNX est (c) QNX Software Systems Ltd / BlackBerry Limited. La
page officielle de copyright de la documentation 8.0 (consultee le 14/11/2026)
indique que l'information de licence de chaque fichier se trouve dans le QNX
Software Center, derriere un compte myQNX ; elle ne donne aucune autorisation
de redistribuer les pages :

<https://www.qnx.com/developers/docs/8.0/com.qnx.doc.copyright/topic/coverpage.html>

Le depot public livre donc **le code (MIT), les tests, 12 fixtures miniatures
et la procedure de reconstruction**, mais pas les 3 426 pages.

### Reconstruction : la commande exacte

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
```

Le script :

1. telecharge la documentation depuis `https://www.qnx.com/developers/docs/`
   (versions 8.0 et 7.1, 9 livres), avec un **delai de 1,0 s entre les
   requetes** (le serveur est respecte) ;
2. **journalise chaque page telechargee** dans `corpus-downloaded/download.log`
   (date, statut, URL, taille, SHA-256) ;
3. construit le corpus avec le meme outil que le corpus fige
   (`tools/build_corpus.py`, deterministe : a cache identique, corpus
   identique) ;
4. **refuse d'ecrire dans un corpus deja fige** (et dans tout repertoire
   place sous une archive portant le marqueur `CORPUS-FIGE.txt`).

**Temps mesure** le 14/11/2026, avec un delai de 1,0 s : **27 pages en 53 s**
(soit environ 2 s par page, requete comprise), 0 echec. Pour le corpus complet
de 3 426 pages, il faut compter **environ 1 h 55** a ce rythme. La commande
s'arrete a tout moment : `--max-pages N` limite le nombre de pages par livre
(utile pour un essai).

```bash
# essai rapide (3 pages par livre)
bash scripts/bootstrap_corpus.sh --out /tmp/essai --max-pages 3 --delay 1.0

# utiliser le corpus reconstruit
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort accept bzero
```

### Structure du corpus

```
corpus-downloaded/
  MANIFEST.json        metadonnees, comptes par livre et par version, sources
  SHA256SUMS           empreinte SHA-256 de chaque fichier stocke
  NOTICE               avis de droit de copie
  download.log         journal de telechargement (une ligne par page)
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

### Le corpus fige d'origine (archive locale, non publiee)

Le corpus utilise pour developper l'outil est conserve dans une archive
locale, hors de ce depot, avec son ancrage :

| Element | Valeur |
|---|---|
| Commit d'origine qui fige le corpus | `6a2c442` |
| Arbre git du corpus a ce commit | `a80c34bbe7873514ee031e6ea746c1157ece8393` |
| Fichiers | 3 430 |
| Taille | 44 942 705 octets (44,9 Mo) |
| SHA-256 de `corpus/SHA256SUMS` | `e312cea466329a76053be0160911cf378ffb1c6ea80050a66c66186ca0023efd` |
| SHA-256 de `corpus/MANIFEST.json` | `df762fecc0b67c7f5dd7116ae38daf080b8159843dd9dbf6abcf8971e692b3fc` |
| SHA-256 de `corpus/index/pages.jsonl` | `292185a3cf9bd615f3709d5c52cac54cb87129ad9a5d08f4055a896bfe5d5595` |

L'empreinte SHA-256 de **chaque page** est dans `index/pages.jsonl` :
`qnx-portmap --verify-corpus` les recalcule toutes (3 426 pages, ~2 s).

### Controle anti-fuite

`scripts/controle_fuite_corpus.py` verifie que l'arbre publiable ne contient
aucune page de la documentation QNX. Il fait six controles :

1. SHA-256 de chaque fichier publie compare aux SHA-256 des 3 426 pages et aux
   SHA-256 des fichiers stockes dans le corpus ;
2. contenu decompresse de chaque fichier gzip de l'arbre ;
3. chaque objet git du depot (contenu brut et contenu decompresse) ;
4. lignes de l'arbre identiques mot pour mot a une ligne du corpus ;
5. plus longue sous-chaine commune, fichier par fichier (fragments) ;
6. budget de copie : **aucun fichier ne doit contenir plus de 4 000 octets de
   texte QNX verbatim**.

Resultat mesure le 14/11/2026 : **0 correspondance**. L'arbre entier ne contient que
**6 037 octets** de texte QNX verbatim, et le fichier qui en contient le plus en compte
**633 octets** (le mini corpus recompose dans `tests/helpers.py`) ; **0 fichier** ne depasse le
budget de 4 000 octets. Les fichiers de citations des mesures J4 et J5
(`docs/mesure-J4/citations-*.txt`, `docs/mesure-J5/citations-*.txt`) sont analyses fragment par
fragment comme les fixtures : ils contiennent 54 a 187 octets de texte QNX verbatim chacun. La
sortie complete est dans `docs/preuves/d-controle-fuite-corpus.txt`.

```bash
python3 scripts/controle_fuite_corpus.py --tree . \
    --corpus /chemin/vers/corpus
```

Le controle est complet (bout en bout, environ 15 minutes : il decompresse et
compare 350 Mo de documentation).

`MANIFESTE-PUBLIE.txt` (a la racine) liste, pour chaque fichier publiable, le
chemin, la taille et le SHA-256 ; il se regenere avec :

```bash
python3 scripts/manifeste_publie.py            # regenere le manifeste
python3 scripts/manifeste_publie.py --check    # verifie qu'il est a jour
```

### Preuves

Les preuves du 14/11/2026 (commande et sortie reelle pour chacune) sont dans
`docs/preuves/` :

| Fichier | Preuve |
|---|---|
| `a-tests-sans-corpus.txt` | 124 tests sur une copie **sans** corpus : 99 passent, 25 sont sautes, code de sortie 0 |
| `b-tests-avec-corpus.txt` | la meme commande **avec** le corpus : 124 tests, 0 saut, code de sortie 0 |
| `c-contre-epreuve-rouge-sans-corpus.txt` | contre-epreuve ROUGE sans le corpus : 10/10 concluantes, 1 regle non testable |
| `d-controle-fuite-corpus.txt` | controle anti-fuite : 0 correspondance |
| `e-fresh-sans-corpus.txt` | `--fresh --fresh-max-pages 3` sur la copie sans corpus : code de sortie 0, corpus fige inchange |
| `f-manifeste-publie.txt` | `MANIFESTE-PUBLIE.txt` : nombre de fichiers, taille totale, 3 plus gros fichiers |
| `garde-fou-bootstrap.txt` | le script de reconstruction refuse d'ecrire dans un corpus fige |
| `g-mesure-j4-rouge.txt` | la mesure J4 : le test echoue quand on truque le taux ou les donnees publiees, puis repasse au vert |
| `h-mesure-j5-rouge.txt` | la mesure J5 : le test echoue sur l'etat d'avant (93 %) et quand la donnee publiee est cassee, puis repasse au vert (96 %) |

## Sources

Toutes consultees le **14/11/2026** :

- Documentation QNX OS 8.0 - <https://www.qnx.com/developers/docs/8.0/>
  - C Library Reference : <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/>
  - Guide de migration : <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/>
  - Networking APIs (io-sock) : <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html>
- Documentation QNX OS 7.1 - <https://www.qnx.com/developers/docs/7.1/>
- Documentation FreeBSD (citee par la C Library Reference 8.0 pour les API
  BSD retirees) : <https://man.freebsd.org/>

## Mesure sur de vrais depots QNX publics (critere J4, puis J5)

**96 % des symboles QNX reellement utilises par de vrais projets QNX sont
resolus et cites par l'outil.** Le detail complet (echantillon, commits
epingles, methode, les 100 symboles) est dans
[`docs/mesure-J5.md`](docs/mesure-J5.md).

L'echantillon : **cinq depots QNX publics** - le BSP officiel QNX pour
Raspberry Pi 5, un BSP QNX pour Raspberry Pi, les sources des *resource
managers* de QNX Neutrino, le Signal Framework QNX et un pilote SocketCAN.
Pour chaque depot, on releve les symboles **reellement appeles** dans les
`.c`/`.h` (les symboles definis par le projet lui-meme sont ecartes), on en
retient 20, et l'echantillon compte exactement **100 symboles distincts**.

| etat | J4 (14/11, mesure datee) | J5 (14/11, meme echantillon) |
|---|---:|---:|
| resolu et cite | 93 | **96** |
| resolu mais decrit ailleurs | 3 | **0** |
| non resolu | 4 | **4** |
| **taux** | **93 %** | **96 %** |

Les 4 symboles qui ne comptent pas ont disparu de la reference 8.0 : ils
etaient dans la reference 7.1, l'outil le dit et ne les invente pas. C'est le
**plafond honnete** du taux sur cet echantillon.

Ce qui change entre les deux mesures : en J4, trois symboles
(`InterruptAttach`, `if_freenameindex`, `setsockopt`) etaient renvoyes par
l'index 8.0 vers une documentation **externe** (pages FreeBSD) ou vers une
autre page de QNX, et comptaient donc « non resolus ». En J5, l'outil est
interroge sur la page QNX 8.0 qui decrit reellement ces trois symboles -
le guide de migration pour `InterruptAttach`, le guide io-sock pour les deux
fonctions socket - et cite cette page avec son empreinte SHA-256. Le
**meme echantillon**, les memes 100 symboles, le meme ordre : le test
verifie l'egalite stricte des deux listes.

La mesure J4 reste une **mesure datee** et n'est pas reecrite :
[`docs/mesure-J4.md`](docs/mesure-J4.md).

Les mesures sont **reproductibles** (`tools/mesure_j4.py` et
`tools/mesure_j5.py`, clones en lecture seule) et **verifiees par les
tests** : `tests/test_mesure_j4.py` et `tests/test_mesure_j5.py` recalculent
le taux et le comparent au taux **compte a la main sur dix symboles donnes
dans le test** ; le test echoue si le taux publie ne correspond plus aux
donnees publiees, si un symbole « resolu » n'a pas de page QNX 8.0
verifiable dans le corpus fige, ou si l'echantillon change. Les preuves
ROUGE -> VERT (on casse la regle, le test echoue, on restaure, le test
repasse) sont dans
[`docs/preuves/g-mesure-j4-rouge.txt`](docs/preuves/g-mesure-j4-rouge.txt) et
[`docs/preuves/h-mesure-j5-rouge.txt`](docs/preuves/h-mesure-j5-rouge.txt) ;
l'etat de chaque fonction de l'outil est dans
[`PROGRESSION.md`](PROGRESSION.md).

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

**La documentation QNX n'est pas redistribuee avec ce depot.** Les pages
restent la propriete de QNX Software Systems Ltd / BlackBerry Limited. Les 12
fixtures de `tests/fixtures/` et les citations des mesures J4 et J5
(`docs/mesure-J4/`, `docs/mesure-J5/`) sont
des extraits courts cites avec leur URL, leur date de consultation et
l'empreinte SHA-256 de la page source ; la licence MIT ne les couvre pas. Voir
`LICENCE-DOCS-QNX.md` (page de copyright officielle, consultee le 14/11/2026)
et `CORPUS-NON-PUBLIE.txt`.

## Comment le statut est decide

1. **Index 8.0** : les pages d'index A-Z de la C Library Reference 8.0
   (26 pages) sont lues. Un symbole trouve dans l'arbre de navigation a sa
   propre page -> `documented`, avec la description courte officielle comme
   citation.
2. **Renvois "described elsewhere"** : le tableau de la meme page d'index
   renvoie vers la documentation FreeBSD ou le guide io-sock pour un certain
   nombre de symbols -> `described_elsewhere`, avec la phrase exacte du renvoi.
3. **Corps du corpus** : sinon, le corps de toutes les pages 8.0 est parcouru
   en **deux passes**. 1re passe : une occurrence de la forme `symbole(`.
   2e passe : une simple mention en prose. Dans les deux passes, le symbole
   doit **ressembler a un nom d'API** : figurer dans un index QNX, ou
   s'ecrire avec une majuscule ou un tiret bas (`pthread_create`, `MSG_NOTIFY`).
   Sans cette condition, un mot anglais rencontre dans une phrase (`argument`,
   `current`, `valid`) ou un nom de parametre suivi de `(` dans un extrait de
   code serait annonce comme un symbole QNX : ce serait faux. La citation
   indique la nature de la rencontre : `appel de fonction` ou `mention` ; une
   mention en **gras** dans la page officielle est signalee `cite en gras`,
   car c'est une mention deliberee de la documentation.
4. **Absent** : le symbole est dans l'index 7.1 mais nulle part dans le corpus
   8.0 -> `absent`, avec sa page 7.1 et sa description.
5. **Inconnu** : sinon -> `unknown`.

Le guide de migration officiel 8.0 est consulte en plus pour chaque symbole de
la liste de travail : un symbole cite par le guide est signale, car c'est la
seule source officielle qui dit quoi faire.
