# QX PORTMAP

> **English summary first. The complete documentation further down is in
> French** (technical reference, corpus procedure, measurements).

## What QX PORTMAP does - English summary

You have a QNX 8.0 source tree and you want to know, for each API it calls,
**whether the symbol is still documented in QNX 8.0, and where exactly**.

QX PORTMAP takes a list of QNX symbols (functions, variables, constants) and
answers, for each one, with the **official page** and the **exact quotation**:

| Status | Meaning |
|---|---|
| `documented` | the symbol has its own page in the QNX 8.0 C Library Reference |
| `described_elsewhere` | no page of its own in 8.0, but the 8.0 documentation still describes it (a "described elsewhere" cross-reference, or a mention in another QNX book) |
| `absent` | the symbol was in the C Library Reference 7.1 and is gone from the 8.0 corpus |
| `unknown` | not found in the frozen corpus: a typo, a macro of your project, or an addition published after 14 November 2026 - the tool does not guess |

It also produces a **work list** of the symbols to fix, sorted by priority.

**No network access by default.** The tool reads a frozen, local copy of the
QNX documentation (3 426 pages, 7.1 and 8.0), with the SHA-256 of every page.

**The QNX documentation is not redistributed with this repository.** The corpus
is rebuilt on demand from the official QNX site with one command and one
download log (see [Corpus QNX](#corpus-qnx--non-distribue)).

**Measured on real code**: on the 100 QNX symbols really called by five public
QNX repositories, the tool resolves and quotes **95 %** of them
([`docs/mesure-J5-FR.md`](mesure-J5-FR.md)). The first measurement, on the same
sample, resolved 93 % ([`docs/mesure-J4-FR.md`](mesure-J4-FR.md)): the
difference is explained further down. One of the symbols that J5 first
resolved, `InterruptAttach`, is now reported as **removed in 8.0 according to
the official migration guide**, with the sentence of the guide quoted: that is
the honest answer, and the rate follows it down.

### The three things the contest rules ask a submission to state

| | |
|---|---|
| **QNX version** | **QNX SDP 8.0** - every answer is backed by a page of the BlackBerry QNX SDP 8.0 documentation (C Library Reference, io-sock User's Guide, SDP migration guide); each quotation carries the URL, the consultation date and the **SHA-256 of the page** it comes from |
| **Target** | the tool is a **host** tool (Linux, macOS, Windows) that needs **neither a QNX SDP, nor a QNX board, nor a QNX account**; it needs **no network connection to run** once the corpus has been downloaded (the corpus is a local snapshot; downloading it for the first time is the only step that needs the network - see [Quick start](#quick-start)); it is pure Python 3 with the standard library only, so it is POSIX-compatible and **designed to run on QNX 8.0 as well - this has not been demonstrated yet**, because the QNX SDP 8.0 licence is not available in this environment (see [Limites](#limites)) |
| **Toolchain** | **Python 3.8+, standard library only** (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`) - no compilation step, no third-party dependency, no API key |

### AI-assisted development

This project was written with the help of an AI coding assistant
(**AI-assisted development**). The assistant wrote the code, the tests and this
documentation. Nothing about QNX is taken on trust: every statement about a QNX
symbol is backed by an **exact quotation of an official page** (URL, date,
SHA-256 of the page), and the behaviour of the tool is checked by a test suite
plus a **RED -> GREEN proof** that breaks a rule on purpose and shows the test
catching it. The measurement itself is counted by hand on ten symbols given in
the test, and compared with the published number.

### Quick start (English)

```console
$ pip install .
$ qnx-portmap abort accept bzero zzz_fonction_inexistante
```

Excerpt of the **real output** (executed on 15 November 2026; the complete
session is further down and is compared line by line by a test - the citation
blocks are elided here):

```text
QX PORTMAP - etat des symboles QNX dans la documentation 8.0
corpus fige : <CORPUS>
pages : 3426 (7.1 : 1200, 8.0 : 2226) - consulte le 2026-11-14 - mode hors ligne

  abort                        documente
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    ...
  accept                       decrit ailleurs
    ...
  bzero                        absent de la 8.0
    ...
  zzz_fonction_inexistante     inconnu du corpus
    ...
```

Without a corpus, the tool says `corpus introuvable` and exits with code 2: it
never invents an answer. The corpus is rebuilt with:

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort
```

A quick check of the network path (3 pages per book: 27 pages downloaded in
51 seconds, measured on 15 November 2026):

```bash
bash scripts/bootstrap_corpus.sh --out /tmp/essai --max-pages 3 --delay 1.0
```

### Build and test (English)

**Build** - Python 3.8+, standard library only, no dependency, no API key, no
account:

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap
pip install .                     # or, without installing: python3 -m qnx_portmap
```

**Test**:

```bash
python3 -m unittest discover -s tests -t .
```

Result measured on 17 November 2026: **202 tests, exit code 0**, without any
network access and without any third-party dependency.

| Situation | Result |
|---|---|
| Corpus in `corpus/`, next to the package | 202 tests, **0 skipped**, exit code 0 |
| Corpus through `QX_PORTMAP_CORPUS` | 202 tests, **1 skipped**, exit code 0 |
| Corpus absent | 202 tests, **33 skipped**, exit code 0 |

The skipped tests are the ones that need the corpus: they are skipped, never
failed. A test that always passes tests nothing, so the repository also
contains a **RED -> GREEN proof**: one rule of the code is broken on purpose
and the matching test must turn red, then the code is restored.

```bash
python3 tools/contre_epreuve.py
```

11 rules, 11 conclusive (11/11, exit code 0) with the corpus, 10/11 without it
(the eleventh rule is about the integrity of the frozen corpus itself); the
output is kept in
[`docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt`](docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt)
(11/11) and
[`docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt`](docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt)
(10/10).

### Submission kit and video plan

- [`KIT-SOUMISSION-QNX.md`](KIT-SOUMISSION-QNX.md) - the text to paste into
  the Devpost submission form, block by block, in the order of the form, with
  the measured length of every block and the limit of every field.
- [`VIDEO-YOUTUBE-QNX-PORTMAP.md`](VIDEO-YOUTUBE-QNX-PORTMAP.md) - the plan of
  the demonstration video, minute by minute, and the one segment that is
  still missing.

Usage guide: [`docs/UTILISATION.md`](docs/UTILISATION.md). The codelab /
tutorial is **published** in this repository:
[`docs/CODELAB-COMMUNITY-QNX.md`](docs/CODELAB-COMMUNITY-QNX.md)
(<https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/CODELAB-COMMUNITY-QNX.md>)
- it teaches a task for QNX 8.0: find out which of the QNX calls your
project makes are still documented in QNX 8.0. The proposal of a post on
`community.qnx.com` is kept in
[`docs/CODELAB-FORUM-PROPOSITION.md`](docs/CODELAB-FORUM-PROPOSITION.md).

### Demo video

**https://youtu.be/UMmxNlxkEi0** - published and public on YouTube on
17 November 2026 (channel "Tgg Labs"), **1 min 51 s** (111.04 s), under the
three minutes the contest rules ask for.

What it shows: the tool running in a real terminal, filmed from a fresh clone
of this public repository - the quick mode against the official QNX
documentation (the A-Z indexes of the QNX 7.1 and 8.0 C Library Reference and
of the 8.0 migration guide, 76 pages, one request per second, the wait
shortened in the video), the status of
each symbol with the official page and the exact quotation, the JSON output,
the upgrade work list and the test suite. It is not a title card, and it
states its own limit: QX PORTMAP is a host tool, so it is not filmed running
on a QNX 8.0 target.

The video file itself is downloadable from this repository:
[`media/qx-portmap-demo-final.mp4`](../media/qx-portmap-demo-final.mp4)
(1 832 957 bytes), with its thumbnail
[`media/qx-portmap-demo-thumbnail.png`](../media/qx-portmap-demo-thumbnail.png).
The plan of the video and the YouTube fields are in
[`VIDEO-YOUTUBE-QNX-PORTMAP.md`](../VIDEO-YOUTUBE-QNX-PORTMAP.md).

### Honest limits (English)

- The project **has not been run on a QNX 8.0 machine yet**: that needs the QNX
  SDP 8.0 licence, which is not available in this environment. The code is
  Python 3 with the standard library only and is POSIX-compatible, so it is
  designed to run on QNX 8.0 as well, but that has not been demonstrated. The
  missing video segment is exactly that demonstration (see
  [`VIDEO-YOUTUBE-QNX-PORTMAP.md`](VIDEO-YOUTUBE-QNX-PORTMAP.md), section 4).
- The corpus is a **snapshot** of the official QNX documentation, taken on
  14 November 2026: a symbol published since then is reported as `unknown`,
  never guessed.
- The tool analyses the **documentation**, not a binary: `absent` means
  "absent from the frozen 8.0 documentation", not "absent from the system".
- The 95 % figure is a measurement on one sample of 100 symbols; it is not a
  guarantee for another project.
- The console messages are in French; the JSON output (`--format json`) uses
  English field names, and the status table above is in English.

---

## Le reste de ce README est en francais

La suite (installation detaillee, exemple de sortie complet, tests,
reconstruction du corpus, controle anti-fuite, mesures J4 et J5, limites,
licences) est en francais. Elle fait partie du depot publie et de son
manifeste ; les commandes et les chiffres sont les memes dans les deux
langues.

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
cinq depots QNX publics, l'outil en resout et cite **95 %**
([`docs/mesure-J5-FR.md`](mesure-J5-FR.md)). La premiere mesure, sur le meme
echantillon, en resolvait 93 % ([`docs/mesure-J4-FR.md`](mesure-J4-FR.md)) :
la difference est expliquee plus bas. Un des symboles que la J5 resolvait,
`InterruptAttach`, est desormais signale **retire de la 8.0 selon le guide
officiel de migration**, phrase du guide citee : c'est la reponse honnete,
et le taux descend avec elle.

---

## Requirements

- **Python 3.8 ou plus.** Aucune dependance a installer : bibliotheque standard
  uniquement (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`).
- **Aucun acces SDP n'est requis.** Ni QNX SDP, ni compilateur, ni carte cible,
  ni compte QNX, ni jeton d'API, ni acces root. L'outil ne compile rien et ne
  s'execute pas sur cible : il lit de la documentation.
- **Le corpus n'est pas livre avec le depot.** La documentation QNX est (c) QNX
  Software Systems Ltd / BlackBerry Limited et n'est pas redistribuable : voir
  `NOTICES-DOCS-QNX.md` et `CORPUS-NON-PUBLIE.txt`. Il se reconstruit avec une
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

**Mode rapide** (environ 80 requetes, quelques minutes) :
`qnx-portmap --quick --lang fr abort accept bzero`. Il ne telecharge que les
26 pages d'index A-Z des C Library Reference 8.0 et 7.1, le guide de
migration 8.0 et la page propre de chaque symbole documente (dans
`corpus-quick/`). Il repond `documente` et `decrit ailleurs` comme le mode
complet, mais ne dit `absent` **que** lorsque le guide officiel de migration
- qu'il lit en entier - annonce le retrait du symbole, en citant la phrase du
guide ; pour tout autre symbole de la 7.1 absent de l'index 8.0, il reste
prudent (une affirmation sur toute la documentation 8.0, qu'il n'a pas lue) :
`bzero` sort `inconnu du corpus`, avec sa page 7.1 et une
note qui l'explique. `tests/test_quick.py` verifie sur le corpus fige que le
mode rapide ne contredit jamais le mode complet.

## Utilisation

Guide d'usage court : [`docs/UTILISATION.md`](docs/UTILISATION.md) (lancer
l'outil, ce qu'il fait, ce que signifie la limite de 95 %).

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

Commande lancee le 14/11/2026 sur ce depot, et rejouee le 15/11/2026 par le
test `tests/test_readme.py`, qui compare cette sortie ligne a ligne avec la
sortie reelle du jour :

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
(+ 1 symbole(s) inconnu(s), hors de cette liste : zzz_fonction_inexistante - verifier l'orthographe, ou un symbole ajoute apres la date du corpus)
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

202 tests, aucune dependance, **aucun acces reseau**. Trois cas :

| Situation | Resultat |
|---|---|
| Corpus dans `corpus/` (a cote du paquet) | 202 tests, **0 skip**, code de sortie 0 |
| Corpus via `QX_PORTMAP_CORPUS` | 202 tests, **1 skip**, code de sortie 0 |
| Corpus absent | 202 tests, **33 skip**, code de sortie 0 |

Avec le corpus fourni par `QX_PORTMAP_CORPUS`, le seul test saute est celui
qui exige le corpus **dans le paquet installe** (absent du depot, la
documentation QNX n'etant pas redistribuee) ; il est saute, jamais en echec.
Si le corpus est place dans `corpus/` a cote du paquet, ce test s'execute et
la suite passe sans aucun saut. Les trois lignes du tableau ci-dessus ont ete
remesurees le 22/11/2026, sur des clones frais du depot public.

Les 33 tests sautes sont ceux qui exigent le corpus complet (integrite
SHA-256 de chacune des 3 426 pages, chiffres de l'index 8.0 et 7.1, reponses
sur des symboles reels). Ils sont **sautes, jamais en echec**, avec le message :

```
corpus absent : lancer scripts/bootstrap_corpus.sh
```

Les 169 autres tests passent **sans corpus**. Parmi eux, les 21 tests de
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
| le taux J5 vaut 95 % sur le meme echantillon que J4 | `test_le_taux_publie_est_95_pour_cent` |
| l'echantillon J5 est strictement celui de J4 | `test_echantillon_identique_a_j4` |
| une page QNX 8.0 verifiee dans le corpus fige est exigee pour chaque conversion | `test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256` |

Les 11 contre-epreuves sont concluantes (`11 / 11`, code de sortie 0) ; la sortie
complete est conservee dans `docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt`
(et dans `docs/contre-epreuve-rouge.txt`).

Sur l'arbre **sans** corpus, 10 des 11 regles restent contre-prouvees (`10 / 10`,
code de sortie 0) : la regle "integrite du corpus fige livre" porte sur les
3 426 pages, donc sur le corpus lui-meme ; sans lui, il n'y a rien a corrompre
et le test correspondant est saute. Les deux executions sont dans
`docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt` (11/11) et
`docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt` (10/10).

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

**Temps mesure**, avec un delai de 1,0 s : le 15/11/2026, **27 pages en 51 s**
(soit environ 2 s par page, requete comprise), 0 echec ; le 16/11/2026, **592 pages
en 1 030 s** sur deux tranches (soit 1,7 s par page), 0 echec ; le 18/11/2026, un
rejeu complet a telecharge **3 973 pages en 7 413 s** (2 h 03, soit 1,87 s par
page), 0 echec. Pour le corpus
complet (environ 4 000 pages, 3 973 mesurees le 18 novembre 2026 ; le corpus fige
en compte 3 426), il faut compter
**environ deux heures** a ce rythme. La commande
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

Resultat mesure le 15/11/2026 : **0 correspondance**. L'arbre entier ne contient que
**6 037 octets** de texte QNX verbatim, et le fichier qui en contient le plus en compte
**633 octets** (le mini corpus recompose dans `tests/helpers.py`) ; **0 fichier** ne depasse le
budget de 4 000 octets. Les fichiers de citations des mesures J4 et J5
(`docs/mesure-J4/citations-*.txt`, `docs/mesure-J5/citations-*.txt`) sont analyses fragment par
fragment comme les fixtures : ils contiennent 54 a 187 octets de texte QNX verbatim chacun. La
sortie complete est dans `docs/preuves/d-controle-fuite-corpus.txt` ; le nombre de fichiers
qu'elle y analyse est celui du moment de la mesure (kit de soumission, plan de la video et
fichiers de preuves compris).

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

Les preuves du 14/11 et du 15/11/2026 (commande et sortie reelle pour chacune)
sont dans `docs/preuves/` :

| Fichier | Preuve |
|---|---|
| `a-tests-sans-corpus.txt` | execution archivee du 15/11/2026 (commit `5653bb2`, avant l'ajout du mode anglais) : 147 tests sur une copie **sans** corpus, 122 passent, 25 sont sautes, code de sortie 0 |
| `b-tests-avec-corpus.txt` | la meme execution archivee **avec** le corpus : 147 tests, 0 saut, code de sortie 0 |
| `c-contre-epreuve-rouge-sans-corpus.txt` | contre-epreuve ROUGE sans le corpus : 10/10 concluantes, 1 regle non testable |
| `d-controle-fuite-corpus.txt` | controle anti-fuite : 0 correspondance |
| `e-fresh-sans-corpus.txt` | `--fresh --fresh-max-pages 3` sur la copie sans corpus : code de sortie 0, corpus fige inchange |
| `f-manifeste-publie.txt` | `MANIFESTE-PUBLIE.txt` : nombre de fichiers, taille totale, 3 plus gros fichiers |
| `garde-fou-bootstrap.txt` | le script de reconstruction refuse d'ecrire dans un corpus fige |
| `g-mesure-j4-rouge.txt` | la mesure J4 : le test echoue quand on truque le taux ou les donnees publiees, puis repasse au vert |
| `h-mesure-j5-rouge.txt` | la mesure J5 : le test echoue sur l'etat d'avant (93 %) et quand la donnee publiee est cassee, puis repasse au vert (95 %) |
| `i-contre-epreuve-rouge-avec-corpus.txt` | contre-epreuve ROUGE avec le corpus dans l'arbre : 11/11 concluantes |
| `j-mesure-champs-devpost.txt` | les 120 pages de projets Devpost publies mesurees : longueurs observees des champs |
| `k-formulaire-devpost-302-401.txt` | le formulaire du concours QNX est derriere une session : HTTP 302 et HTTP 401 |

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

**95 % des symboles QNX reellement utilises par de vrais projets QNX sont
resolus et cites par l'outil.** Le detail complet (echantillon, commits
epingles, methode, les 100 symboles) est dans
[`docs/mesure-J5-FR.md`](mesure-J5-FR.md).

L'echantillon : **cinq depots QNX publics** - le BSP officiel QNX pour
Raspberry Pi 5, un BSP QNX pour Raspberry Pi, les sources des *resource
managers* de QNX Neutrino, le Signal Framework QNX et un pilote SocketCAN.
Pour chaque depot, on releve les symboles **reellement appeles** dans les
`.c`/`.h` (les symboles definis par le projet lui-meme sont ecartes), on en
retient 20, et l'echantillon compte exactement **100 symboles distincts**.

| etat | J4 (14/11, mesure datee) | J5 (19/11, meme echantillon) |
|---|---:|---:|
| resolu et cite | 93 | **95** |
| resolu mais decrit ailleurs | 3 | **0** |
| non resolu | 4 | **5** |
| **taux** | **93 %** | **95 %** |

Les 5 symboles qui ne comptent pas : quatre ont disparu de la reference 8.0
(ils etaient dans la reference 7.1, l'outil le dit et ne les invente pas), et
le cinquieme, `InterruptAttach`, est signale **retire de la 8.0 selon le guide
officiel de migration** - cite par l'outil : « The following functions have
been removed: InterruptAttach() InterruptAttachArray() InterruptHookIdle2()
InterruptHookTrace() ». C'est le **plafond honnete** du taux sur cet
echantillon : quand le guide officiel dit qu'une fonction a ete retiree,
l'outil le dit au lieu de la compter resolue.

Ce qui change entre les deux mesures : en J4, trois symboles
(`InterruptAttach`, `if_freenameindex`, `setsockopt`) etaient renvoyes par
l'index 8.0 vers une documentation **externe** (pages FreeBSD) ou vers une
autre page de QNX, et comptaient donc "non resolus". En J5, l'outil est
interroge sur la page QNX 8.0 qui decrit reellement ces symboles - le guide
io-sock pour les deux fonctions socket - et cite cette page avec son empreinte
SHA-256. **Dans un vrai depot public, l'outil trouve un appel a
`InterruptAttach()`, une fonction que le guide officiel de migration dit
retiree en QNX 8.0** : depuis le 19/11/2026 l'outil la signale `absent`,
priorite 1, en citant la phrase du guide, au lieu de la compter simplement
"decrite ailleurs" (le taux passe de 96 % a 95 % parce que la reponse est
maintenant la reponse honnete). Le **meme echantillon**, les memes 100
symboles, le meme ordre : le test verifie l'egalite stricte des deux listes.

La mesure J4 reste une **mesure datee** et n'est pas reecrite :
[`docs/mesure-J4-FR.md`](mesure-J4-FR.md).

Les mesures sont **reproductibles** (`tools/mesure_j4.py` et
`tools/mesure_j5.py`, clones en lecture seule) et **verifiees par les
tests** : `tests/test_mesure_j4.py` et `tests/test_mesure_j5.py` recalculent
le taux et le comparent au taux **compte a la main sur dix symboles donnes
dans le test** ; le test echoue si le taux publie ne correspond plus aux
donnees publiees, si un symbole "resolu" n'a pas de page QNX 8.0
verifiable dans le corpus fige, ou si l'echantillon change. Les preuves
ROUGE -> VERT (on casse la regle, le test echoue, on restaure, le test
repasse) sont dans
[`docs/preuves/g-mesure-j4-rouge.txt`](docs/preuves/g-mesure-j4-rouge.txt) et
[`docs/preuves/h-mesure-j5-rouge.txt`](docs/preuves/h-mesure-j5-rouge.txt) ;
l'etat de chaque fonction de l'outil est dans
[`PROGRESSION-FR.md`](../PROGRESSION-FR.md).

## Limites

- Le projet **n'a pas encore ete execute sur une machine QNX 8.0** : cela
  demande la licence QNX SDP 8.0, qui n'est pas disponible dans cet
  environnement. Le code est du Python 3 (bibliotheque standard uniquement) et
  il est compatible POSIX, donc il est concu pour tourner aussi sur QNX 8.0,
  mais cela n'a pas ete demontre. La regle du concours demande de montrer que
  le projet "genuinely builds for or runs on QNX 8.0" ; le segment de video
  qui manque est precisement cette demonstration
  (`VIDEO-YOUTUBE-QNX-PORTMAP.md`, section 4).
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
`NOTICES-DOCS-QNX.md` (page de copyright officielle, consultee le 14/11/2026)
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
