# QX PORTMAP

> **This README is entirely in English.** The console output of the tool is
> in English by default; add **`--lang fr`** to get the same output in French.
> The French output is shown **verbatim** where it is the subject of a test,
> with the English output next to it and a table of the console labels.

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
QNX repositories, the tool resolves and quotes **95 %** of them
([`docs/mesure-J5.md`](docs/mesure-J5.md)). The first measurement, on the same
sample, resolved 93 % ([`docs/mesure-J4.md`](docs/mesure-J4.md)): the
difference is explained further down. One of the symbols the tool used to
resolve, `InterruptAttach`, is now reported as **removed in 8.0 according to
the official migration guide**, with the sentence of the guide quoted: that is
the honest answer, and the rate follows it down, from 96 % to the 95 %
published here.

### The three things the contest rules ask a submission to state

| | |
|---|---|
| **QNX version** | **QNX SDP 8.0** - every answer is backed by a page of the BlackBerry QNX SDP 8.0 documentation (C Library Reference, io-sock User's Guide, SDP migration guide); each quotation comes from a page whose URL, consultation date and **SHA-256** are recorded in the corpus index, and `qnx-portmap --verify-corpus` checks every page of the snapshot against its fingerprint |
| **Target** | the tool is a **host** tool (Linux, macOS, Windows) that needs **neither a QNX SDP, nor a QNX board, nor a QNX account**; it needs **no network connection to run** once the corpus has been downloaded (the corpus is a local snapshot; downloading it for the first time is the only step that needs the network - see [Quick start](#quick-start)); it is pure Python 3 with the standard library only, so it is POSIX-compatible and **designed to run on QNX 8.0 as well - this has not been demonstrated yet**, although the QNX SDP 8.0 licence arrived here on 24 November 2026, and the answers have since been checked against the real QNX 8.0 headers (see [Limits](#limits)); the SDP 8.0.3 does ship a **Python 3.13 for QNX OS targets** (package `com.qnx.qnx800.target.utils.python3`), so the same command fits a QNX 8.0 target, and the one-command target check is ready: [`docs/QNX-8.0-CIBLE.md`](docs/QNX-8.0-CIBLE.md) |
| **Toolchain** | **Python 3.8+, standard library only** (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`) - no compilation step, no third-party dependency, no API key |

### AI-assisted development

This project was written with the help of an AI coding assistant
(**AI-assisted development**). The assistant wrote the code, the tests and this
documentation. Nothing about QNX is taken on trust: every statement about a QNX
symbol is backed by an **exact quotation of an official page** (URL, date, and
the SHA-256 of the page in the corpus index), and the behaviour of the tool is
checked by a test suite
plus a **RED -> GREEN proof** that breaks a rule on purpose and shows the test
catching it. The measurement itself is counted by hand on ten symbols given in
the test, and compared with the published number.

### Quick start

Three commands, copied as they are, give a first answer in about two to three
minutes, on Linux, macOS or Windows, with no QNX SDP, no board and no account:

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap && pip install .   # optional: the tool needs only the standard library
python3 -m qnx_portmap --quick abort accept bzero zzz_fonction_inexistante
```

The second command is optional and may fail on a locked-down Python (a system
Python protected by PEP 668 refuses it, measured on 16 November 2026): the
third command works with or without it, because `python3 -m qnx_portmap` is
the same program as the `qnx-portmap` command that the install adds.

The third command is the **quick mode** (76 pages downloaded in 127 s and, in
an independent replay from a clean environment, in 144 s, both measured on
16 November 2026 at one request per second). Real output of the quick mode
(one status line and one note line per symbol; the page,
citation and detail lines are elided here, like in the full-mode output below):

```text
  abort                        documented
    note   : present in 7.1 and in 8.0
  accept                       described elsewhere
    note   : described in the 8.0 documentation but without a page of its own in the C Library Reference
  bzero                        unknown
    note   : quick mode: in the 7.1 C Library Reference index, not in the 8.0 index; the other 8.0 books were not read, so absent or described elsewhere is decided by the full corpus (scripts/bootstrap_corpus.sh)
  zzz_fonction_inexistante     unknown
    note   : quick mode: in neither the 8.0 nor the 7.1 index; the other 8.0 books were not read (full corpus: scripts/bootstrap_corpus.sh)
```

The exit code of that run is **1**, and that is expected: `0` when every
symbol is documented in 8.0, `1` when at least one is absent or unknown, `2`
on error. The quick mode says `absent` **only** when the official migration
guide - which the quick mode reads in full - announces the removal of the
symbol, and it then quotes the sentence of the guide; for any other symbol of
the 7.1 index that it cannot resolve (a statement about the whole 8.0
documentation, which it has not read), it stays prudent: `bzero` stays
`unknown`.

The quick mode writes its small corpus in `corpus-quick/`, in the clone. That
directory is ignored by git and by the published manifest - the QNX
documentation is not redistributable, so it is not part of the published tree
- so the clone stays clean (`git status` prints nothing) and the [one command
that replays every published proof](#one-command-to-replay-every-published-proof)
still answers in that same clone.

**The full answer** (quotations, SHA-256 of every page, and `absent`) needs
the complete corpus: **about 4,000 pages** of the official QNX documentation,
downloaded once from the official QNX site (the frozen snapshot used for the
proofs below holds 3,426 pages). **Budget about two hours** at one
request per second (1.7 to 2 s per page, measured on 15 and 16 November
2026; a complete judge replay on 18 November 2026 downloaded **3,973 pages in
2 h 03**, 1.87 s per page, 0 failure -- the live documentation now serves 547
more pages than the frozen snapshot, all of them in the 7.1 C Library
Reference). After that download the tool runs offline, with no network
request:

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m qnx_portmap abort accept bzero zzz_fonction_inexistante
```

Excerpt of the **real output** (executed on 15 November 2026; the citation
blocks are elided here, and this excerpt is compared with the real output by
`tests/test_readme_en.py`):

```text
QX PORTMAP - status of QNX symbols in the 8.0 documentation
frozen corpus: <CORPUS>
pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

  abort                        documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    ...
  accept                       described elsewhere
    ...
  bzero                        absent
    ...
  zzz_fonction_inexistante     unknown
    ...
```

With `--lang fr`, the tool prints the same output in French (kept
byte-identical to the published proofs; the complete French session is
further down and is compared line by line by `tests/test_readme.py`):

```text
QX PORTMAP - etat des symboles QNX dans la documentation 8.0
corpus fige : <CORPUS>
pages : 3426 (7.1 : 1200, 8.0 : 2226) - consulte le 2026-11-14 - mode hors ligne

  abort                        documente
    ...
  accept                       decrit ailleurs
    ...
  bzero                        absent de la 8.0
    ...
  zzz_fonction_inexistante     inconnu du corpus
    ...
```

How the quick mode works: it downloads only the 26 A-Z index pages of the
8.0 and 7.1 C Library Reference, the official migration guide to 8.0 and the
own page of each documented symbol, into `corpus-quick/`, then runs the same
classifier. It answers `documented` and `described elsewhere` exactly like the
full mode; `tests/test_quick.py` checks, on the frozen corpus, that the quick
mode never contradicts the full mode.

Without a corpus, the full mode says `corpus not found` (`corpus introuvable`
with `--lang fr`) and exits with code 2: it never invents an answer.

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

Result measured on 24 November 2026: **246 tests, exit code 0**, without any
network access and without any third-party dependency.

| Situation | Result |
|---|---|
| Corpus in `corpus/`, next to the package | 246 tests, **0 skipped**, exit code 0 |
| Corpus through `QX_PORTMAP_CORPUS` | 246 tests, **1 skipped**, exit code 0 |
| Corpus absent | 246 tests, **33 skipped**, exit code 0 |

The skipped tests are the ones that need the corpus: they are skipped, never
failed. A test that always passes tests nothing, so the repository also
contains a **RED -> GREEN proof**: one rule of the code is broken on purpose
and the matching test must turn red, then the code is restored.

```bash
python3 tools/contre_epreuve.py
```

12 rules, 12 conclusive (12/12, exit code 0) when the frozen corpus is in the
tree, 11 of the 12 conclusive without it - the tool prints `11 / 11`, because
the rule about the integrity of the frozen corpus itself cannot be tested
without the corpus; the archived outputs are kept in
[`docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt`](docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt)
(11/11, archived on 15/11/2026) and
[`docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt`](docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt)
(10/10, archived on 15/11/2026).

### Submission kit and video plan

- [`KIT-SOUMISSION-QNX.md`](KIT-SOUMISSION-QNX.md) - the text to paste into
  the Devpost submission form, block by block, in the order of the form, with
  the measured length of every block and the limit of every field.
- [`VIDEO-YOUTUBE-QNX-PORTMAP.md`](VIDEO-YOUTUBE-QNX-PORTMAP.md) - the plan of
  the demonstration video, minute by minute, and the one segment that is
  still missing.
- [`media/`](media/) - the demonstration video, its thumbnail, and the four
  images of the Devpost gallery: `galerie-miniature-3x2.png` (the thumbnail
  of the project gallery, 3:2), and the three screenshots
  `galerie-1-statuts.png`, `galerie-2-json.png`, `galerie-3-tests.png`.
  Every line drawn in them is the verbatim output of a real command.

Usage guide: [`docs/UTILISATION.md`](docs/UTILISATION.md). The codelab /
tutorial is **published** in this repository:
[`docs/CODELAB-COMMUNITY-QNX.md`](docs/CODELAB-COMMUNITY-QNX.md)
(<https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/CODELAB-COMMUNITY-QNX.md>)
- it teaches a task for QNX 8.0: find out which of the QNX calls your
project makes are still documented in QNX 8.0. The same task, as a tutorial
with numbered steps and one command per step, is
[`docs/codelab/QX-PORTMAP-CODELAB.md`](docs/codelab/QX-PORTMAP-CODELAB.md)
(<https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/codelab/QX-PORTMAP-CODELAB.md>).
The proposal of a post on
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
[`media/qx-portmap-demo-final.mp4`](media/qx-portmap-demo-final.mp4)
(1 832 957 bytes), with its thumbnail
[`media/qx-portmap-demo-thumbnail.png`](media/qx-portmap-demo-thumbnail.png).
The plan of the video and the YouTube fields are in
[`VIDEO-YOUTUBE-QNX-PORTMAP.md`](VIDEO-YOUTUBE-QNX-PORTMAP.md).

### Honest limits

- The project **has not been run on a QNX 8.0 machine yet**: that needs the QNX
  SDP 8.0 licence, which arrived here on 24 November 2026: the tool itself has not
  been run on a target yet. The code is
  Python 3 with the standard library only and is POSIX-compatible, so it is
  designed to run on QNX 8.0 as well, but that has not been demonstrated. The
  missing video segment is exactly that demonstration (see
  [`VIDEO-YOUTUBE-QNX-PORTMAP.md`](VIDEO-YOUTUBE-QNX-PORTMAP.md), section 4).
  The procedure and the one-command target check are ready in
  [`docs/QNX-8.0-CIBLE.md`](docs/QNX-8.0-CIBLE.md) and
  [`scripts/qnx8_target_check.sh`](scripts/qnx8_target_check.sh).
  What *is* measured (16/11/2026): the package needs **Python 3.4 or later**
  (`vermin`), imports **none** of the modules that Python 3.13 removed
  (PEP 594), and has no third-party dependency - so the Python 3.13 of the
  SDP 8.0.3 target is new enough for it, and the target check prints a
  `compat` line to show it on the day it runs.
- The corpus is a **snapshot** of the official QNX documentation, taken on
  14 November 2026: a symbol published since then is reported as `unknown`,
  never guessed.
- The tool analyses the **documentation**, not a binary: `absent` means
  "absent from the frozen 8.0 documentation", not "absent from the system".
- The 95 % figure is a measurement on one sample of 100 symbols; it is not a
  guarantee for another project.
- The console messages are in English by default and in French with
  `--lang fr`; the JSON output (`--format json`) uses English field names in
  both modes.
- The **documentation** of this repository is in English (this README, the
  manuals, the licences, the submission kit, the video plan, the codelab),
  and so are the **comments and docstrings of the source code**. Every
  document translated into English keeps its French original byte-identical
  next to it (table below). The archived outputs of `docs/preuves/` are the
  frozen proofs of the day they were measured: they keep the wording of that
  day.

---

## Requirements

- **Python 3.8 or more.** Nothing to install: standard library only
  (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`).
- **No SDP access is required.** No QNX SDP, no compiler, no target board, no
  QNX account, no API token, no root access. The tool compiles nothing and
  does not run on a target: it reads documentation.
- **One internet access is needed for the first answer.** The quick start of
  this README downloads the 76 pages it needs from
  `https://www.qnx.com/developers/docs/` (measured on 23 November 2026 in a
  fresh clone of this repository: 76 pages in 138 s; 127 s and 144 s on
  16 November 2026). After that download the tool reads its corpus locally and
  makes **no network request** any more.
- **The corpus is not shipped with the repository.** The QNX documentation is
  (c) QNX Software Systems Ltd / BlackBerry Limited and is not redistributable:
  see `NOTICES-DOCS-QNX.md` and `CORPUS-NON-PUBLIE.txt`. It is rebuilt with a
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
`corpus not found` (`corpus introuvable` with `--lang fr`) and exits with
code 2.

## Usage

Short usage guide: [`docs/UTILISATION.md`](docs/UTILISATION.md) (running the
tool, what it does, what the 95 % figure means exactly).

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

Command run on 15/11/2026 in this repository, and replayed by the test
`tests/test_readme_en.py`, which compares this output line by line with the
real output of the day:

```
$ qnx-portmap abort accept bzero zzz_fonction_inexistante
```

Real output of the command (verbatim tool output, English - English is the
default language of the console, this block is not translated and is compared
byte by byte with the real output by the test):

```
QX PORTMAP - status of QNX symbols in the 8.0 documentation
frozen corpus: <CORPUS>
pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

  abort                        documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    citation (index C Library Reference 8.0) :
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
    citation (index C Library Reference 8.0, section "described elsewhere") :
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports ) and
      Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
    * cited by the official migration guide 8.0: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
    note   : described in the 8.0 documentation but without a page of its own in the C Library Reference

  bzero                        absent
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
    citation (index C Library Reference 7.1, index entry) :
      Set the first part of an object to null bytes
    note   : present in the C Library Reference 7.1, absent from the whole 8.0 corpus

  zzz_fonction_inexistante     unknown
    note   : not found in the frozen 8.0 corpus: unknown symbol, typo, or added after 2026-11-14

--- Upgrade worklist (2 symbol(s)) ---
P2  bzero                      absent
      https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
      Set the first part of an object to null bytes
P3  accept                     described elsewhere
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports )
      and Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
      cited by the migration guide: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
(+ 1 unknown symbol(s), not in this list: zzz_fonction_inexistante - check the spelling, or a symbol added after the corpus date)
```

The same command with `--lang fr` (real output of the French mode, compared
line by line with the real output by `tests/test_readme.py` and
`tests/test_readme_en.py`):

```
$ qnx-portmap --lang fr abort accept bzero zzz_fonction_inexistante
```

French output (real):

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

English translation of the French console labels used above:

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
(`QX_PORTMAP_CORPUS=...`): the path depends on the machine. The English block
is compared line by line with the real output by `tests/test_readme_en.py`,
and the French one by `tests/test_readme.py`: both fail if the tool changes.

The French version of this README, kept byte-identical to the version that was
published before the translation, is in [`docs/README-FR.md`](docs/README-FR.md).

Every document that was translated into English keeps its **French original,
byte-identical**, next to the English one:

| English (published) | French original (kept, byte-identical) |
|---|---|
| [`PROGRESSION.md`](PROGRESSION.md) | [`PROGRESSION-FR.md`](PROGRESSION-FR.md) |
| [`docs/mesure-J4.md`](docs/mesure-J4.md) | [`docs/mesure-J4-FR.md`](docs/mesure-J4-FR.md) |
| [`docs/mesure-J5.md`](docs/mesure-J5.md) | [`docs/mesure-J5-FR.md`](docs/mesure-J5-FR.md) |
| [`qnx_portmap/LISEZMOI.md`](qnx_portmap/LISEZMOI.md) | [`qnx_portmap/LISEZMOI-FR.md`](qnx_portmap/LISEZMOI-FR.md) |
| `docs/mesure-J4/citations-*.txt` | `docs/mesure-J4/citations-*-FR.txt` |
| `docs/mesure-J5/citations-*.txt` | `docs/mesure-J5/citations-*-FR.txt` |

The French files are there for the record; the published documentation is the
English one.

## One command to replay every published proof

Everything this repository publishes is replayed by **one command**, from the
root of the clone:

```bash
bash scripts/verify-all.sh
```

The command prints one line per verification and answers one question: *did
any published proof turn out to be false?*

| Exit code | Meaning |
|---|---|
| 0 | no published proof was contradicted (only `OK` and `NOT CHECKED` rows) |
| 1 | at least one row is `FAILED`: a published proof is false, or the code is broken |
| 2 | the command itself could not run (`python3` is absent) |

`OK`, `FAILED` and `NOT CHECKED` are never mixed. A check that could not run
on this machine - the frozen QNX corpus is absent, because the QNX
documentation is not redistributed - is reported `NOT CHECKED`: it is never
counted as `OK`, and it never makes the exit code fail. The verdict counts the
two apart, so `0` means "nothing was disproved", not "everything was checked".

The eight checks, in this order: the unit test suite, the anti-leak control
of the corpus, the published manifest, the published numbers (every test and
file count written in this README and in the two LISEZMOI files must be the
real one), the parity of the output block of this README, the RED
counter-proof, the measured lengths of the submission kit, and the
placeholders and draft banners of the published documents (no field of the
submission kit and no section of the README may keep a placeholder, the
published tutorial may not announce itself as a draft any more, and the
demonstration video URL must be the same in the README and in the kit). The command writes nothing in the repository: the RED counter-proof,
which breaks a rule of the code on purpose, is replayed on a temporary copy
of the tree, never on the checkout of the reader.

Real output, on a fresh clone without the corpus (replayed on 24 November 2026):

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap
bash scripts/verify-all.sh
```

```
======================================================================================================
QX PORTMAP - replay every published proof of this repository
======================================================================================================
checks     : 8

======================================================================================================
SUMMARY - one line per verification
======================================================================================================
VERIFICATION                               RESULT       DETAIL                                         EXIT
------------------------------------------ ------------ ------------------------------------------------ ----
unit test suite                            OK           246 tests, 33 skipped                          0
anti-leak control of the QNX corpus        NOT CHECKED  the frozen QNX corpus is absent here           -
published manifest                         OK           MANIFESTE-PUBLIE.txt lists 132 files           0
published numbers of the README            OK           every published count is the real one          0
parity of the README output block          NOT CHECKED  the frozen corpus is absent here               0
RED counter-proof                          OK           11 / 11 rules counter-proved                   0
lengths of the submission kit              OK           every measured length matches the text         0
placeholders and draft banners             OK           nothing left in the 72 published documents     0
======================================================================================================
VERDICT: NO CHECK FAILED - 6/8 OK, 2 NOT CHECKED (RC 0)
         the check(s) that could not run on this machine are named in the
         table above and are never reported as OK: nothing was disproved,
         but these proofs were NOT re-run here.
======================================================================================================
```

The output above is the real one: the command prints no path and no timing,
so it is the same on every machine.

**You can run it in the clone where you already ran the quick start.** The
quick start writes `corpus-quick/` in the clone; that directory is ignored by
git and by the published manifest (the QNX documentation is not
redistributable, so it is not part of the published tree), so the clone stays
clean and the command answers the same verdict there. Measured on 25 November
2026, in a fresh clone where the quick start had just run: `git status` prints
nothing, the `published manifest` row is `OK` (`MANIFESTE-PUBLIE.txt lists
132 files`), the `RED counter-proof` row is `OK` (`11 / 11 rules
counter-proved`), and the verdict is the one printed above (`6/8 OK, 2 NOT
CHECKED, RC 0`).

The contract of the command itself - exit code 0 when nothing is disproved,
exit code 1 when a published proof is false - is proved by
`tests/verify_all_contract.py`. It breaks a published proof on purpose in a
temporary copy and checks that the exit code becomes 1:

```bash
python3 -m unittest tests.verify_all_contract
```

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

246 tests, no dependency, **no network access**. Three cases:

| Situation | Result |
|---|---|
| Corpus in `corpus/` (next to the package) | 246 tests, **0 skipped**, exit code 0 |
| Corpus via `QX_PORTMAP_CORPUS` | 246 tests, **1 skipped**, exit code 0 |
| Corpus absent | 246 tests, **33 skipped**, exit code 0 |

With the corpus given by `QX_PORTMAP_CORPUS`, the only skipped test is the
one that requires the corpus **inside the installed package** (absent from the
repository, the QNX documentation being not redistributable); it is skipped,
never failed. If the corpus is placed in `corpus/` next to the package, this
test runs and the suite passes without any skip. The three lines of the table
above were re-measured on 24 November 2026, on fresh clones of the published
repository.

The 33 skipped tests are the ones that require the complete corpus (SHA-256
integrity of each of the 3 426 pages, index figures for 8.0 and 7.1, answers
on real symbols). They are **skipped, never failed**, with the message:

```
corpus absent : lancer scripts/bootstrap_corpus.sh
```

(the message of the tool, in French: "corpus absent: run
scripts/bootstrap_corpus.sh")

The 213 other tests pass **without the corpus**. Among them, the 21 tests of
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

**Run it on a clean checkout.** The tool refuses to touch a tree that is not
clean: it breaks the code on purpose and then restores it, so it only runs
where there is nothing to restore. In a tree where files were written (the
codelab leaves `calls.txt`, `my_code.c` and `state.json` behind; the corpus
directories it downloads are ignored by git and do not make the tree dirty),
it prints `contre_epreuve: the repository must be
clean (git status not empty)` and exits with code 2.

| Broken rule | Test that must turn red |
|---|---|
| word boundary in the citation search | `test_respects_word_boundaries` |
| a file name is not a symbol (`recv.c`, `/dev/socket`) | `test_path_is_ignored` |
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
| the J5 rate is 95 % on the same sample as J4 | `test_le_taux_publie_est_95_pour_cent` |
| the J5 sample is strictly the one of J4 | `test_echantillon_identique_a_j4` |
| a verified QNX 8.0 page of the frozen corpus is required for every conversion | `test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256` |

The table lists **15** broken rules: **12** of them are counter-proved by
`tools/contre_epreuve.py` (**12 / 12** with the corpus in the tree, **11 / 11**
without it, exit code 0), and the **three J5 rules** have their own red proof in
`docs/preuves/h-mesure-j5-rouge.txt`.

On the tree **without** the corpus, 11 of the 12 rules remain counter-proved
(`11 / 11`, exit code 0): the rule "integrity of the frozen corpus shipped"
covers the 3 426 pages, therefore the corpus itself; without it there is
nothing to corrupt and the matching test is skipped. The archived runs are in
`docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt` (11/11, archived on
15/11/2026) and `docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt`
(10/10, archived on 15/11/2026).

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

**Time measured** with a 1.0 s delay: on 15/11/2026, **27 pages in 51 s**
(about 2 s per page, request included), 0 failure; on 16/11/2026, **592 pages in
1 030 s** in two tranches (about 1.7 s per page), 0 failure; on 18/11/2026, a
complete judge replay downloaded **3,973 pages in 7,413 s** (2 h 03, 1.87 s per
page), 0 failure. For the complete corpus (about 4,000 pages, 3,973 measured on
18 November 2026; the frozen snapshot used for the proofs below holds 3,426
pages), count on **about two hours** at this rate. The command stops at any
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

Result measured on 15/11/2026: **0 match**: no page of the QNX documentation is
present in the publishable tree, in any form. The whole tree contains only a
few kilobytes of QNX verbatim text - the exact figure of the last measurement,
and the file that contains the most of it, are written in
`docs/preuves/d-controle-fuite-corpus.txt` - and **no file** exceeds the
4 000-byte budget. The citation files of the J4 and J5 measurements
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

The control is complete (end to end, it decompresses and compares 350 MB of
documentation). It takes about three minutes on the container of the build
machine (180.0 s measured on 24 November 2026, on the tree of this
repository).

#### The memory of the control, and why its result cannot change

The control used to keep a set of the 27 684 783 distinct 30-character
pieces of the corpus (1.70 GB, measured on 19 November 2026) and to search a
350 MB text built in three copies. On the container of the build machine
(cgroup limit 2 621 440 000 bytes, no swap) the kernel killed it after 10
seconds: `RC 137`, peak 2 621 251 584 bytes - measured on 24 November 2026,
on a fresh clone of the published commit `ffee935`.

It now keeps a **Bloom filter of 64 MiB** instead of that set, builds the
searched text in one allocation, and releases the complete text of the corpus
before the search index is built. A Bloom filter has **no false negative**:
every piece of the corpus is inserted in it, so a window that is in the corpus
is always searched. A false positive is still possible, and it only costs one
useless search in the same text: the control can be **stricter** than before,
never more lenient, so the verdict cannot become green where it was red.

Measured on the same machine, with the same corpus and the same tree, on
24 November 2026: the control ends with `RESULTAT : 0 correspondance` and
`RC 0` in **180.0 s** (about three minutes), with a peak of
**1 793 519 616 bytes** (about 1.7 Go). The duration and the peak depend on
the machine and on its cache state: another run of the same day gave 177.0 s
and 1 577 209 856 bytes, with the same verdict.

The proof of the equivalence is in
[`docs/preuves/m-anti-fuite-memoire.txt`](docs/preuves/m-anti-fuite-memoire.txt):
the output of the corrected control and the output of the reference
implementation (`a2b42cc`, which searches the corpus line by line) are
identical line for line, and the sabotage test still turns the control red.

`MANIFESTE-PUBLIE.txt` (at the root) lists, for every publishable file, the
path, the size and the SHA-256; it is regenerated with:

```bash
python3 scripts/manifeste_publie.py            # regenerates the manifest
python3 scripts/manifeste_publie.py --check    # checks that it is up to date
```

### Evidence

The evidence of 14/11, 15/11 and 24/11/2026 (command and real output for each
one) is in `docs/preuves/`:

| File | Evidence |
|---|---|
| `a-tests-sans-corpus.txt` | archived run of 15/11/2026 (commit `5653bb2`, before the English mode was added): 147 tests on a copy **without** the corpus, 122 pass, 25 are skipped, exit code 0 |
| `b-tests-avec-corpus.txt` | the same archived run **with** the corpus: 147 tests, 0 skipped, exit code 0 |
| `c-contre-epreuve-rouge-sans-corpus.txt` | archived run of 15/11/2026: RED counter-proof without the corpus, 10/10 conclusive (the 11 rules of that day), 1 rule not testable |
| `d-controle-fuite-corpus.txt` | anti-leak control: 0 match |
| `e-fresh-sans-corpus.txt` | `--fresh --fresh-max-pages 3` on the copy without the corpus: exit code 0, frozen corpus unchanged |
| `f-manifeste-publie.txt` | `MANIFESTE-PUBLIE.txt`: number of files, total size, 3 biggest files |
| `garde-fou-bootstrap.txt` | the rebuild script refuses to write into a frozen corpus |
| `g-mesure-j4-rouge.txt` | the J4 measurement: the test fails when the rate or the published data is faked, then passes again |
| `h-mesure-j5-rouge.txt` | the J5 measurement: the test fails on the previous state (93 %) and when the published data is broken, then passes again (95 %) |
| `i-contre-epreuve-rouge-avec-corpus.txt` | archived run of 15/11/2026: RED counter-proof with the corpus in the tree, 11/11 conclusive (the 11 rules of that day) |
| `j-mesure-champs-devpost.txt` | the 120 published Devpost project pages measured: observed field lengths |
| `k-formulaire-devpost-302-401.txt` | the contest form is behind a session: HTTP 302 and HTTP 401 |
| `m-anti-fuite-memoire.txt` | anti-leak control of 24/11/2026: the memory of the control, the proof that the corrected control gives the same verdict as the reference implementation (identical output, line for line) and the sabotage test that still turns it red |

## Sources

All consulted on **14/11/2026**:

- QNX OS 8.0 documentation - <https://www.qnx.com/developers/docs/8.0/>
  - C Library Reference (A-Z index, page A): <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html>
  - Migration guide (about page): <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/about.html>
  - Networking APIs (io-sock): <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html>
- QNX OS 7.1 documentation - <https://www.qnx.com/developers/docs/7.1/>
- FreeBSD documentation (cited by the 8.0 C Library Reference for the retired
  BSD APIs): <https://man.freebsd.org/>

## Measurement on real public QNX repositories (J4 criterion, then J5)

**95 % of the QNX symbols really used by real QNX projects are resolved and
quoted by the tool.** The complete detail (sample, pinned commits, method, the
100 symbols) is in [`docs/mesure-J5.md`](docs/mesure-J5.md).

The sample: **five public QNX repositories** - the official QNX BSP for
Raspberry Pi 5, a QNX BSP for Raspberry Pi, the sources of the QNX Neutrino
*resource managers*, the QNX Signal Framework and a SocketCAN driver. For each
repository, the symbols **really called** in the `.c`/`.h` files are collected
(the symbols defined by the project itself are discarded), 20 of them are kept,
and the sample counts exactly **100 distinct symbols**.

| state | J4 (14/11, dated measurement) | J5 (19/11, same sample) |
|---|---:|---:|
| resolved and quoted | 93 | **95** |
| resolved but described elsewhere | 3 | **0** |
| not resolved | 4 | **5** |
| **rate** | **93 %** | **95 %** |

The 5 symbols that do not count: four of them have disappeared from the 8.0
reference (they were in the 7.1 reference, the tool says so and does not
invent them), and the fifth, `InterruptAttach`, is reported as **removed in
8.0 according to the official migration guide** - quoted by the tool: "The
following functions have been removed: InterruptAttach() InterruptAttachArray()
InterruptHookIdle2() InterruptHookTrace()". This is the **honest ceiling** of
the rate on this sample: when the official guide says a function was removed,
the tool says so instead of counting it resolved.

What changes between the two measurements: in J4, three symbols
(`InterruptAttach`, `if_freenameindex`, `setsockopt`) were returned by the 8.0
index towards **external** documentation (FreeBSD pages) or towards another
QNX page, and therefore counted as "not resolved". In J5, the tool is asked on
the QNX 8.0 page that really describes these symbols - the migration
guide for `InterruptAttach`, the io-sock guide for the two socket functions -
and quotes that page with its SHA-256 fingerprint. **In a real public
repository, the tool finds a call to `InterruptAttach()`, a function that the
official migration guide says was removed in QNX 8.0**: since 19/11/2026 the
tool reports it `absent`, priority 1, quoting the sentence of the guide,
instead of counting it as merely "described elsewhere" (the rate goes from
96 % down to 95 % because the answer is now the honest one). The **same
sample**, the same 100 symbols, the same order: the test checks the strict
equality of the two lists.

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
  QNX SDP 8.0 licence, which arrived here on 24 November 2026: the tool itself has not
  been run on a target yet. The code is
  Python 3 (standard library only) and it is POSIX-compatible, so it is
  designed to run on QNX 8.0 as well, but that has not been demonstrated. The
  contest rule asks to show that the project "genuinely builds for or runs on
  QNX 8.0"; the missing video segment is precisely that demonstration
  (`VIDEO-YOUTUBE-QNX-PORTMAP.md`, section 4). The procedure is written in
  [`docs/QNX-8.0-CIBLE.md`](docs/QNX-8.0-CIBLE.md), with the one-command
  target check [`scripts/qnx8_target_check.sh`](scripts/qnx8_target_check.sh),
  already rehearsed on a workstation.
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
the MIT licence does not cover them. See `NOTICES-DOCS-QNX.md` (official
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
