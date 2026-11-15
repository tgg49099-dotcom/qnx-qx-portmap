# QX PORTMAP

> **This README is entirely in English.** The console output of the tool is
> still in French: it is the program output, so it is not translated. It is
> shown **verbatim** where it is the subject of the test, with an **English
> translation** next to it and a table of the console labels.

## What QX PORTMAP does

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
download log (see [QNX corpus](#qnx-corpus-not-redistributed)).

**Measured on real code**: on the 100 QNX symbols really called by five public
QNX repositories, the tool resolves and quotes **96 %** of them
([`docs/mesure-J5.md`](docs/mesure-J5.md)). The first measurement, on the same
sample, resolved 93 % ([`docs/mesure-J4.md`](docs/mesure-J4.md)): the
difference is explained further down.

### The three things the contest rules ask a submission to state

| | |
|---|---|
| **QNX version** | **QNX SDP 8.0** - every answer is backed by a page of the BlackBerry QNX SDP 8.0 documentation (C Library Reference, io-sock User's Guide, SDP migration guide); each quotation carries the URL, the consultation date and the **SHA-256 of the page** it comes from |
| **Target** | the tool is a **host** tool (Linux, macOS, Windows) that needs **neither a QNX SDP, nor a QNX board, nor a QNX account, nor a network connection**; it is pure Python 3 with the standard library only, so it is POSIX-compatible and **designed to run on QNX 8.0 as well - this has not been demonstrated yet**, because the QNX SDP 8.0 licence is not available in this environment (see [Limits](#limits)) |
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

### Quick start

```console
$ pip install .
$ qnx-portmap abort accept bzero zzz_fonction_inexistante
```

Excerpt of the **real output** (executed on 15 November 2026; the complete
session is further down and is compared line by line by a test - the citation
blocks are elided here). The tool prints in French: the first block is the
**verbatim tool output (French)**, the second one is its **English
translation**.

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

```text
QX PORTMAP - state of the QNX symbols in the 8.0 documentation
frozen corpus: <CORPUS>
pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

  abort                        documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    ...
  accept                       described elsewhere
    ...
  bzero                        absent from 8.0
    ...
  zzz_fonction_inexistante     unknown to the corpus
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

### Build and test

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

Result measured on 15 November 2026: **124 tests, exit code 0**, without any
network access and without any third-party dependency.

| Situation | Result |
|---|---|
| Corpus in `corpus/`, next to the package | 124 tests, **0 skipped**, exit code 0 |
| Corpus through `QX_PORTMAP_CORPUS` | 124 tests, **1 skipped**, exit code 0 |
| Corpus absent | 124 tests, **25 skipped**, exit code 0 |

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

Usage guide: [`docs/UTILISATION.md`](docs/UTILISATION.md). A codelab draft for
`community.qnx.com` is in [`docs/CODELAB-COMMUNITY-QNX.md`](docs/CODELAB-COMMUNITY-QNX.md)
(text only, **not published yet**: the URL of the published codelab will be
added here and in the submission kit when it goes online).

### Honest limits

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
- The 96 % figure is a measurement on one sample of 100 symbols; it is not a
  guarantee for another project.
- The console messages are in French; the JSON output (`--format json`) uses
  English field names, and the status table above is in English.

---

## Requirements

- **Python 3.8 or more.** Nothing to install: standard library only
  (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`).
- **No SDP access is required.** No QNX SDP, no compiler, no target board, no
  QNX account, no API token, no root access. The tool compiles nothing and
  does not run on a target: it reads documentation.
- **The corpus is not shipped with the repository.** The QNX documentation is
  (c) QNX Software Systems Ltd / BlackBerry Limited and is not redistributable:
  see `LICENCE-DOCS-QNX.md` and `CORPUS-NON-PUBLIE.txt`. It is rebuilt with a
  single command, which needs network access to
  `https://www.qnx.com/developers/docs/`:
  `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`.
- The rebuilt corpus is verifiable: `qnx-portmap --verify-corpus`.

## Installation

```bash
# from the root of the repository
pip install .

# or, isolated, with pipx (https://pipx.pypa.io)
pipx install .

# or without installing anything
python3 -m qnx_portmap --help
```

The tool looks for the frozen corpus in this order:

1. the `QX_PORTMAP_CORPUS` environment variable;
2. the `corpus/` directory of the repository (next to the package);
3. the `corpus/` directory of the current working directory.

The repository **does not contain** a `corpus/` directory: after rebuilding the
corpus (see below), you point at it explicitly:

```bash
QX_PORTMAP_CORPUS=/path/to/corpus qnx-portmap abort
qnx-portmap --corpus /path/to/corpus abort
```

Without a corpus, the tool does not guess anything: it prints
`corpus introuvable` and exits with code 2.

## Usage

Short usage guide: [`docs/UTILISATION.md`](docs/UTILISATION.md) (running the
tool, what it does, what the 96 % figure means exactly).

```bash
# symbols on the command line
qnx-portmap abort accept bzero

# list in a file (one symbol per line, # comments are ignored)
qnx-portmap --file symbols.txt

# list on standard input
grep -o '[A-Za-z_][A-Za-z0-9_]*' my_code.c | sort -u | qnx-portmap --stdin --format json

# output formats
qnx-portmap --format markdown abort accept bzero > state.md
qnx-portmap --format json abort > state.json

# integrity check of the corpus
qnx-portmap --verify-corpus

# online reload (option, never used by default)
qnx-portmap --fresh --fresh-only
```

Exit code: `0` if every analysed symbol is documented in 8.0, `1` if at least
one symbol is absent or unknown, `2` on error (corpus absent, no list given).

### Real output example (executed)

Command run on 14/11/2026 in this repository, and replayed on 15/11/2026 by the
test `tests/test_readme.py`, which compares this output line by line with the
real output of the day:

```
$ qnx-portmap abort accept bzero zzz_fonction_inexistante
```

Real output of the command (verbatim tool output, French - the program prints
in French, this block is not translated and is compared byte by byte with the
real output by the test):

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

English translation of the block above (for reading only - the block above is
the byte-exact output of the tool):

```
QX PORTMAP - state of the QNX symbols in the 8.0 documentation
frozen corpus: <CORPUS>
pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

  abort                        documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    citation (C Library Reference 8.0 index) :
      Raise the SIGABRT signal to terminate program execution
    detail :
      The abort() function causes abnormal process termination to occur by means of the function
      call raise ( SIGABRT ) , unless the signal SIGABRT is caught and the signal handler doesn't
      return. If the signal SIGABRT is caught and the signal handler returns, the signal handler is
      removed and raise ( SIGABRT ) is called again. Note that prior to calling raise() , abort()
      ensures that SIGABRT isn't ignored or blocked.
    note   : present in 7.1 and in 8.0

  accept                       described elsewhere
    page   : https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
    see    : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html
    citation (C Library Reference 8.0 index, section "described elsewhere") :
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports ) and
      Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
    * cited by the official 8.0 migration guide: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
    note   : described in the 8.0 documentation but without a page of its own in the C Library Reference

  bzero                        absent from 8.0
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
    citation (C Library Reference 7.1 index, index entry) :
      Set the first part of an object to null bytes
    note   : present in the 7.1 C Library Reference, absent from the whole 8.0 corpus

  zzz_fonction_inexistante     unknown to the corpus
    note   : not found in the frozen 8.0 corpus: unknown symbol, typo, or addition published after 2026-11-14

--- Upgrade work list (2 symbol(s)) ---
P2  bzero                      absent from 8.0
      https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
      Set the first part of an object to null bytes
P3  accept                     described elsewhere
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports )
      and Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
      cited by the migration guide: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
```

English translation of the console labels used above:

| console label | English |
|---|---|
| `documente` | documented in QNX 8.0 |
| `decrit ailleurs` | described elsewhere in the QNX 8.0 documentation |
| `absent de la 8.0` | present in QNX 7.1, absent from the QNX 8.0 corpus |
| `inconnu du corpus` | not found in the frozen corpus |
| `corpus introuvable` | corpus not found (no corpus available) |
| `present en 7.1 et en 8.0` | present in 7.1 and in 8.0 |
| `cite par le guide de migration officiel 8.0` | cited by the official 8.0 migration guide |
| `decrit dans la documentation 8.0 mais sans page propre dans la C Library Reference` | described in the 8.0 documentation but without a page of its own in the C Library Reference |
| `present dans la C Library Reference 7.1, absent de tout le corpus 8.0` | present in the 7.1 C Library Reference, absent from the whole 8.0 corpus |
| `introuvable dans le corpus 8.0 fige : symbole inconnu, erreur de saisie, ou ajout posterieur au 2026-11-14` | not found in the frozen 8.0 corpus: unknown symbol, typo, or addition published after 2026-11-14 |
| `Liste de travail de mise a niveau` | Upgrade work list |
| `voir` | see |

The four statuses appear in the same output: `abort` is documented, `accept`
is described elsewhere (a cross-reference to the FreeBSD documentation and to
the io-sock guide), `bzero` has disappeared from 8.0, and
`zzz_fonction_inexistante` is unknown to the corpus - the tool says so instead
of inventing an answer.

`<CORPUS>` designates the corpus directory used for the command
(`QX_PORTMAP_CORPUS=...`): the path depends on the machine. This block is
compared line by line with the real output by `tests/test_readme.py`, which
fails if the tool changes.

The French version of this README, kept byte-identical to the version that was
published before the translation, is in [`docs/README-FR.md`](docs/README-FR.md).

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

124 tests, no dependency, **no network access**. Two cases:

| Situation | Result |
|---|---|
| Corpus in `corpus/` (next to the package) | 124 tests, **0 skipped**, exit code 0 |
| Corpus via `QX_PORTMAP_CORPUS` | 124 tests, **1 skipped**, exit code 0 |
| Corpus absent | 124 tests, **25 skipped**, exit code 0 |

With the corpus given by `QX_PORTMAP_CORPUS`, the only skipped test is the
one that requires the corpus **inside the installed package** (absent from the
repository, the QNX documentation being not redistributable); it is skipped,
never failed. If the corpus is placed in `corpus/` next to the package, this
test runs and the suite passes without any skip. The three lines of the table
above were re-measured on 15/11/2026.

The 25 skipped tests are the ones that require the complete corpus (SHA-256
integrity of each of the 3 426 pages, index figures for 8.0 and 7.1, answers
on real symbols). They are **skipped, never failed**, with the message:

```
corpus absent : lancer scripts/bootstrap_corpus.sh
```

(the message of the tool, in French: "corpus absent: run
scripts/bootstrap_corpus.sh")

The 99 other tests pass **without the corpus**. Among them, the 21 tests of
`tests/test_fixtures.py` work on the **miniature fixtures**: 12 short extracts
(1 to 3 lines) of real QNX pages, stored in `tests/fixtures/`, with the source
URL, the consultation date and the SHA-256 of the complete page the extract
comes from. These tests rebuild a small corpus from these extracts and run the
real classifier on it: `abort` is documented, `errno` is a variable, `accept`
is described elsewhere, `bzero` has disappeared, `rw_interrupt` is cited in
bold, `getprotobyname_r` is called in another book, `_smalloc` is cited by the
migration guide, and the English word `entire` is **not** reported as a
symbol.

The tests also cover the edge cases of the mission: absent symbol, symbol
described elsewhere, symbol cited in bold, duplicate symbol, empty list,
corrupted corpus file. One test also checks that **the output example of this
README is the real output** of the command written just above it.

To run everything with the complete corpus:

```bash
QX_PORTMAP_CORPUS=/path/to/corpus python3 -m unittest discover -s tests -t .
```

### RED counter-proof

A test that always passes tests nothing. `tools/contre_epreuve.py` breaks one
rule of the code at a time on purpose and checks that the matching test turns
**red**, then restores the repository:

```bash
python3 tools/contre_epreuve.py
```

| Broken rule | Test that must turn red |
|---|---|
| word boundary in the citation search | `test_respects_word_boundaries` |
| verification of the SHA-256 of the corpus pages | `test_detects_a_corrupted_page` |
| verification of the `SHA256SUMS` file | `test_detects_a_corrupted_sha256sums_file` |
| reading of the "described elsewhere" table of the index | `test_described_elsewhere_symbol` |
| extraction of the Description section | `test_description_is_the_description_section_not_the_library_one` |
| unknown status for a symbol outside the corpus | `test_unknown_symbol` |
| deduplication of the symbol list | `test_duplicate_symbol_is_reported_once` |
| integrity of the frozen corpus shipped with the tool | `test_every_page_matches_its_sha256` |
| a prose mention only counts for a name that looks like an API | `test_english_word_mentioned_in_prose_is_not_a_symbol` |
| detection of the symbols cited in bold | `test_symbol_cited_in_bold` |
| the J4 rate only counts the resolved and quoted symbols | `test_le_taux_du_script_egale_le_taux_compte_a_la_main` |
| the J5 rate is 96 % on the same sample as J4 | `test_le_taux_publie_est_96_pour_cent` |
| the J5 sample is strictly the one of J4 | `test_echantillon_identique_a_j4` |
| a verified QNX 8.0 page of the frozen corpus is required for every conversion | `test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256` |

The 11 counter-proofs are conclusive (`11 / 11`, exit code 0); the complete
output is kept in `docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt`
(and in `docs/contre-epreuve-rouge.txt`).

On the tree **without** the corpus, 10 of the 11 rules remain counter-proved
(`10 / 10`, exit code 0): the rule "integrity of the frozen corpus shipped"
covers the 3 426 pages, therefore the corpus itself; without it there is
nothing to corrupt and the matching test is skipped. The two runs are in
`docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt` (11/11) and
`docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt` (10/10).

## QNX corpus: not redistributed

> **the QNX documentation is not redistributed; it is downloaded from the official site on demand**

The QNX documentation is (c) QNX Software Systems Ltd / BlackBerry Limited. The
official copyright page of the 8.0 documentation (consulted on 14/11/2026)
states that the licence information of each file is in the QNX Software Center,
behind a myQNX account; it gives no permission to redistribute the pages:

<https://www.qnx.com/developers/docs/8.0/com.qnx.doc.copyright/topic/coverpage.html>

The public repository therefore ships **the code (MIT), the tests, 12 miniature
fixtures and the rebuild procedure**, but not the 3 426 pages.

### Rebuilding: the exact command

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
```

The script:

1. downloads the documentation from `https://www.qnx.com/developers/docs/`
   (versions 8.0 and 7.1, 9 books), with a **1.0 s delay between requests**
   (the server is respected);
2. **logs every downloaded page** in `corpus-downloaded/download.log`
   (date, status, URL, size, SHA-256);
3. builds the corpus with the same tool as the frozen corpus
   (`tools/build_corpus.py`, deterministic: same cache, same corpus);
4. **refuses to write into an already frozen corpus** (and into any directory
   placed under an archive bearing the `CORPUS-FIGE.txt` marker).

**Time measured** on 15/11/2026, with a 1.0 s delay: **27 pages in 51 s**
(about 2 s per page, request included), 0 failure. For the complete corpus of
3 426 pages, count on **about 1 h 55** at this rate. The command stops at any
time: `--max-pages N` limits the number of pages per book (useful for a test).

```bash
# quick test (3 pages per book)
bash scripts/bootstrap_corpus.sh --out /tmp/essai --max-pages 3 --delay 1.0

# use the rebuilt corpus
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort accept bzero
```

### Corpus structure

```
corpus-downloaded/
  MANIFEST.json        metadata, counts per book and per version, sources
  SHA256SUMS           SHA-256 fingerprint of every stored file
  NOTICE               copy notice
  download.log         download log (one line per page)
  index/pages.jsonl    one line per page: URL, book, topic, SHA-256, size
  pages/8.0/<book>/topic/<topic>.html.gz
  pages/7.1/<book>/topic/<topic>.html.gz
```

| Version | Pages | Books |
|---|---|---|
| 8.0 | 2 226 | C Library Reference (1 600), io-sock (37), user guide (169), system architecture (179), building (190), technotes (19), migration guide (23), system tuning (9) |
| 7.1 | 1 200 | C Library Reference (1 200) |

The pages are gzip-compressed **as they were downloaded** on 14/11/2026; the
SHA-256 fingerprint of the original bytes is written in `index/pages.jsonl`
and verified by `qnx-portmap --verify-corpus`.

### The original frozen corpus (local archive, not published)

The corpus used to develop the tool is kept in a local archive, outside this
repository, with its anchoring:

| Element | Value |
|---|---|
| Origin commit that froze the corpus | `6a2c442` |
| Git tree of the corpus at this commit | `a80c34bbe7873514ee031e6ea746c1157ece8393` |
| Files | 3 430 |
| Size | 44 942 705 bytes (44.9 MB) |
| SHA-256 of `corpus/SHA256SUMS` | `e312cea466329a76053be0160911cf378ffb1c6ea80050a66c66186ca0023efd` |
| SHA-256 of `corpus/MANIFEST.json` | `df762fecc0b67c7f5dd7116ae38daf080b8159843dd9dbf6abcf8971e692b3fc` |
| SHA-256 of `corpus/index/pages.jsonl` | `292185a3cf9bd615f3709d5c52cac54cb87129ad9a5d08f4055a896bfe5d5595` |

The SHA-256 fingerprint of **every page** is in `index/pages.jsonl`:
`qnx-portmap --verify-corpus` recomputes them all (3 426 pages, ~2 s).

### Anti-leak control

`scripts/controle_fuite_corpus.py` checks that the publishable tree contains
no page of the QNX documentation. It performs six checks:

1. SHA-256 of every published file compared with the SHA-256 of the 3 426 pages
   and with the SHA-256 of the files stored in the corpus;
2. decompressed content of every gzip file of the tree;
3. every git object of the repository (raw content and decompressed content);
4. lines of the tree identical word for word to a line of the corpus;
5. longest common substring, file by file (fragments);
6. copy budget: **no file may contain more than 4 000 bytes of QNX verbatim
   text**.

Result measured on 15/11/2026: **0 match**. The whole tree contains only
**6 037 bytes** of QNX verbatim text, and the file that contains the most
counts **633 bytes** (the mini corpus rebuilt in `tests/helpers.py`); **0 file**
exceeds the 4 000-byte budget. The citation files of the J4 and J5 measurements
(`docs/mesure-J4/citations-*.txt`, `docs/mesure-J5/citations-*.txt`) are analysed
fragment by fragment like the fixtures: they contain 54 to 187 bytes of QNX
verbatim text each. The complete output is in
`docs/preuves/d-controle-fuite-corpus.txt`; the number of files it analyses
there is the one at the time of the measurement (submission kit, video plan and
proof files included).

```bash
python3 scripts/controle_fuite_corpus.py --tree . \
    --corpus /path/to/corpus
```

The control is complete (end to end, about 15 minutes: it decompresses and
compares 350 MB of documentation).

`MANIFESTE-PUBLIE.txt` (at the root) lists, for every publishable file, the
path, the size and the SHA-256; it is regenerated with:

```bash
python3 scripts/manifeste_publie.py            # regenerates the manifest
python3 scripts/manifeste_publie.py --check    # checks that it is up to date
```

### Evidence

The evidence of 14/11 and 15/11/2026 (command and real output for each one)
is in `docs/preuves/`:

| File | Evidence |
|---|---|
| `a-tests-sans-corpus.txt` | 124 tests on a copy **without** the corpus: 99 pass, 25 are skipped, exit code 0 |
| `b-tests-avec-corpus.txt` | the same command **with** the corpus: 124 tests, 0 skipped, exit code 0 |
| `c-contre-epreuve-rouge-sans-corpus.txt` | RED counter-proof without the corpus: 10/10 conclusive, 1 rule not testable |
| `d-controle-fuite-corpus.txt` | anti-leak control: 0 match |
| `e-fresh-sans-corpus.txt` | `--fresh --fresh-max-pages 3` on the copy without the corpus: exit code 0, frozen corpus unchanged |
| `f-manifeste-publie.txt` | `MANIFESTE-PUBLIE.txt`: number of files, total size, 3 biggest files |
| `garde-fou-bootstrap.txt` | the rebuild script refuses to write into a frozen corpus |
| `g-mesure-j4-rouge.txt` | the J4 measurement: the test fails when the rate or the published data is faked, then passes again |
| `h-mesure-j5-rouge.txt` | the J5 measurement: the test fails on the previous state (93 %) and when the published data is broken, then passes again (96 %) |
| `i-contre-epreuve-rouge-avec-corpus.txt` | RED counter-proof with the corpus in the tree: 11/11 conclusive |
| `j-mesure-champs-devpost.txt` | the 120 published Devpost project pages measured: observed field lengths |
| `k-formulaire-devpost-302-401.txt` | the contest form is behind a session: HTTP 302 and HTTP 401 |

## Sources

All consulted on **14/11/2026**:

- QNX OS 8.0 documentation - <https://www.qnx.com/developers/docs/8.0/>
  - C Library Reference: <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic>
  - Migration guide: <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic>
  - Networking APIs (io-sock): <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html>
- QNX OS 7.1 documentation - <https://www.qnx.com/developers/docs/7.1/>
- FreeBSD documentation (cited by the 8.0 C Library Reference for the retired
  BSD APIs): <https://man.freebsd.org/>

## Measurement on real public QNX repositories (J4 criterion, then J5)

**96 % of the QNX symbols really used by real QNX projects are resolved and
quoted by the tool.** The complete detail (sample, pinned commits, method, the
100 symbols) is in [`docs/mesure-J5.md`](docs/mesure-J5.md).

The sample: **five public QNX repositories** - the official QNX BSP for
Raspberry Pi 5, a QNX BSP for Raspberry Pi, the sources of the QNX Neutrino
*resource managers*, the QNX Signal Framework and a SocketCAN driver. For each
repository, the symbols **really called** in the `.c`/`.h` files are collected
(the symbols defined by the project itself are discarded), 20 of them are kept,
and the sample counts exactly **100 distinct symbols**.

| state | J4 (14/11, dated measurement) | J5 (14/11, same sample) |
|---|---:|---:|
| resolved and quoted | 93 | **96** |
| resolved but described elsewhere | 3 | **0** |
| not resolved | 4 | **4** |
| **rate** | **93 %** | **96 %** |

The 4 symbols that do not count have disappeared from the 8.0 reference: they
were in the 7.1 reference, the tool says so and does not invent them. This is
the **honest ceiling** of the rate on this sample.

What changes between the two measurements: in J4, three symbols
(`InterruptAttach`, `if_freenameindex`, `setsockopt`) were returned by the 8.0
index towards **external** documentation (FreeBSD pages) or towards another
QNX page, and therefore counted as "not resolved". In J5, the tool is asked on
the QNX 8.0 page that really describes these three symbols - the migration
guide for `InterruptAttach`, the io-sock guide for the two socket functions -
and quotes that page with its SHA-256 fingerprint. The **same sample**, the
same 100 symbols, the same order: the test checks the strict equality of the
two lists.

The J4 measurement remains a **dated measurement** and is not rewritten:
[`docs/mesure-J4.md`](docs/mesure-J4.md).

The measurements are **reproducible** (`tools/mesure_j4.py` and
`tools/mesure_j5.py`, read-only clones) and **verified by the tests**:
`tests/test_mesure_j4.py` and `tests/test_mesure_j5.py` recompute the rate and
compare it with the rate **counted by hand on ten symbols given in the test**;
the test fails if the published rate no longer matches the published data, if a
"resolved" symbol has no verifiable QNX 8.0 page in the frozen corpus, or if
the sample changes. The RED -> GREEN proofs (the rule is broken, the test
fails, the code is restored, the test passes again) are in
[`docs/preuves/g-mesure-j4-rouge.txt`](docs/preuves/g-mesure-j4-rouge.txt) and
[`docs/preuves/h-mesure-j5-rouge.txt`](docs/preuves/h-mesure-j5-rouge.txt);
the state of each function of the tool is in
[`PROGRESSION.md`](PROGRESSION.md).

## Limits

- The project **has not been run on a QNX 8.0 machine yet**: that requires the
  QNX SDP 8.0 licence, which is not available in this environment. The code is
  Python 3 (standard library only) and it is POSIX-compatible, so it is
  designed to run on QNX 8.0 as well, but that has not been demonstrated. The
  contest rule asks to show that the project "genuinely builds for or runs on
  QNX 8.0"; the missing video segment is precisely that demonstration
  (`VIDEO-YOUTUBE-QNX-PORTMAP.md`, section 4).
- The corpus is a **snapshot**: it dates from 14/11/2026. A symbol added in a
  later version of the documentation is classified `unknown`, never guessed.
  `--fresh` rebuilds the corpus from the official site.
- The analysis concerns the **documentation**, not the binary code: a symbol
  `absent` means "absent from the frozen 8.0 documentation", not "absent from
  the system". The 8.0 documentation does not say everything, and the tool does
  not pretend otherwise.
- The search in the corpus ignores the navigation menus and keeps only the
  body of the pages. A prose mention is enough to classify a symbol as
  `described_elsewhere`, but the citation then says `mention`: you have to
  check that the symbol is still a function call.
- The versions **6.5** and **6.6** of the QNX documentation are not public
  (`https://www.qnx.com/developers/docs/6.5.0/` redirects to a download page,
  `6.6/` returns 404). The tool therefore covers the 7.1 -> 8.0 axis.
- The citations are extracted from the official HTML pages: the formatting of
  the text is sometimes irregular (spaces around the parentheses, for example).
  The text is verbatim, the punctuation is not always so.
- The tool does not replace reading the documentation: it tells you **where**
  to read, and **what** the page says.

## Licence

The code is under the MIT licence (see `LICENSE`).

**The QNX documentation is not redistributed with this repository.** The pages
remain the property of QNX Software Systems Ltd / BlackBerry Limited. The 12
fixtures of `tests/fixtures/` and the citations of the J4 and J5 measurements
(`docs/mesure-J4/`, `docs/mesure-J5/`) are short extracts quoted with their
URL, their consultation date and the SHA-256 fingerprint of the source page;
the MIT licence does not cover them. See `LICENCE-DOCS-QNX.md` (official
copyright page, consulted on 14/11/2026) and `CORPUS-NON-PUBLIE.txt`.

## How the status is decided

1. **8.0 index**: the A-Z index pages of the 8.0 C Library Reference
   (26 pages) are read. A symbol found in the navigation tree has its own page
   -> `documented`, with the short official description as the quotation.
2. **"described elsewhere" cross-references**: the table of the same index page
   points to the FreeBSD documentation or to the io-sock guide for a certain
   number of symbols -> `described_elsewhere`, with the exact sentence of the
   cross-reference.
3. **Body of the corpus**: otherwise, the body of all the 8.0 pages is scanned
   in **two passes**. 1st pass: an occurrence of the form `symbol(`. 2nd pass:
   a simple prose mention. In both passes, the symbol must **look like an API
   name**: be listed in a QNX index, or be written with an upper-case letter or
   an underscore (`pthread_create`, `MSG_NOTIFY`). Without this condition, an
   English word met in a sentence (`argument`, `current`, `valid`) or a
   parameter name followed by `(` in a code extract would be reported as a QNX
   symbol: that would be wrong. The quotation states the nature of the match:
   `appel de fonction` (function call) or `mention`; a mention in **bold** in
   the official page is reported as `cite en gras` (cited in bold), because it
   is a deliberate mention by the documentation.
4. **Absent**: the symbol is in the 7.1 index but nowhere in the 8.0 corpus ->
   `absent`, with its 7.1 page and its description.
5. **Unknown**: otherwise -> `unknown`.

The official 8.0 migration guide is consulted in addition for every symbol of
the work list: a symbol cited by the guide is reported, because it is the only
official source that says what to do.
