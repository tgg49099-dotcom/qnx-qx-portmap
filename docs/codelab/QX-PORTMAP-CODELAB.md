# QX PORTMAP codelab: which QNX calls of your project still exist in QNX 8.0?

**In this tutorial you will produce the work list of the QNX calls your project
makes that no longer exist in the QNX 8.0 documentation, each one with the
official page and the exact quotation taken from it.**

URL of this codelab:
<https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/codelab/QX-PORTMAP-CODELAB.md>

Repository: <https://github.com/tgg49099-dotcom/qnx-qx-portmap>

---

## Prerequisites

- **QNX 8.0 / SDP 8.0 is the target of the analysis, not a prerequisite of the
  tool.** QX PORTMAP is a *host* tool: it reads the official QNX 8.0
  documentation from your own machine, so it needs **no SDP, no QNX board, no
  QNX account and no API key**. (Running the tool on a real QNX 8.0 target is
  still pending the SDP 8.0 licence: **to be confirmed on QNX 8.0 on 20
  November 2026**.)
- **A Linux, macOS or Windows host with Python 3.8 or later** - standard
  library only, nothing to install.
- **About 15 minutes** for steps 1 to 4 and 8 to 9. Step 3 downloads 76 pages
  of the official documentation at one request per second (**150.7 s**
  measured on 19 November 2026), step 4 downloads 27 pages (**51 s**, measured
  on 19 November 2026).
- **About 2 hours** for steps 5 to 7: they need the complete snapshot of the
  official documentation (3 973 pages in 2 h 03, measured on 18 November
  2026).
- **A network connection for steps 3, 4 and 5 only** - they download the
  official QNX documentation. After that the tool works offline.

## What the tool does

QX PORTMAP takes a list of QNX symbols (functions, variables, constants) and
tells you, for each one, whether it is still documented in QNX 8.0, with the
official page and the exact quotation taken from that page. It also produces
a **work list** of the calls to fix, sorted by priority.

It answers with four statuses, and never with anything else:

| Status | Meaning |
|---|---|
| `documented` | the symbol has its own page in the QNX 8.0 C Library Reference |
| `described_elsewhere` | no page of its own in 8.0, but the 8.0 documentation still describes it |
| `absent` | it was in the C Library Reference 7.1 and is gone from the 8.0 corpus |
| `unknown` | not in the frozen corpus: a typo, a macro of your project, or a symbol published after 14 November 2026 - the tool does not guess |

---

## Step 1 - Get the repository

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
```

**You should see:** `Cloning into 'qnx-qx-portmap'...` and a new directory
`qnx-qx-portmap/`. The command exits with code 0.

## Step 2 - Run the tool, with nothing to install

```bash
cd qnx-qx-portmap && python3 -m qnx_portmap --help
```

**You should see:** the usage of the command, ending with:

```text
Examples: qnx-portmap abort pthread_create bzero qnx-portmap --file
symbols.txt --format markdown cat symbols.txt | qnx-portmap --stdin --format
json qnx-portmap --verify-corpus
```

`python3 -m qnx_portmap` is the same program as the `qnx-portmap` command that
`pip install .` adds, so installing is optional. A system Python protected by
PEP 668 refuses `pip install .`: use `python3 -m venv .venv` in that case.

## Step 3 - Your first answer, in quick mode (about 3 minutes)

```bash
cd qnx-qx-portmap && python3 -m qnx_portmap --quick abort accept bzero zzz_fonction_inexistante
```

**You should see** (the real output of 19 November 2026, complete; only the
path of the small corpus, the date and the duration of the run change from one
machine to another):

```text
qnx-portmap: quick mode, downloading to <REPO>/corpus-quick
  index 8.0: 26 pages
  index 7.1: 26 pages
  migration guide 8.0: 23 pages
  own pages of the documented symbols: 1
qnx-portmap: small corpus ready: 76 pages in 150.7 s
QX PORTMAP - status of QNX symbols in the 8.0 documentation
quick-mode small corpus: <REPO>/corpus-quick
pages: 76 (7.1: 26, 8.0: 50) - downloaded on 2026-11-19 - quick mode (A-Z indexes and migration guide only; "absent" only when the guide announces the removal)

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

  bzero                        unknown
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
    citation (index C Library Reference 7.1, index entry) :
      Set the first part of an object to null bytes
    note   : quick mode: in the 7.1 C Library Reference index, not in the 8.0 index; the other 8.0 books were not read, so absent or described elsewhere is decided by the full corpus (scripts/bootstrap_corpus.sh)

  zzz_fonction_inexistante     unknown
    note   : quick mode: in neither the 8.0 nor the 7.1 index; the other 8.0 books were not read (full corpus: scripts/bootstrap_corpus.sh)

--- Upgrade worklist (1 symbol(s)) ---
P3  accept                     described elsewhere
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports )
      and Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
      cited by the migration guide: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html
(+ 2 unknown symbol(s), not decided by the quick mode: bzero, zzz_fonction_inexistante - the full corpus decides them)
```

The exit code of the command is **1**: at least one symbol is not `documented`.
That is the expected answer, not a failure of the tool.

The quick mode reads only the 26 A-Z index pages of the 8.0 and 7.1 C Library
Reference, the 23 pages of the official migration guide and the page of each
symbol it needs: 76 pages in total, 150.7 seconds at one request per second
(measured on 19 November 2026; a second run in a fresh clone of the published
commit took 147.5 s; the tool prints the duration of **your** run).
It writes its small snapshot in `corpus-quick/`, which the tool prints on its
first line; you can delete that directory at the end.

## Step 4 - Check that the official documentation is reachable (about 1 minute)

```bash
cd qnx-qx-portmap && bash scripts/bootstrap_corpus.sh --out /tmp/essai --max-pages 3 --delay 1.0
```

**You should see** (only the path changes from one machine to another; the
script prints in French):

```text
bootstrap_corpus : sortie   /tmp/essai
bootstrap_corpus : cache    /tmp/essai/cache
bootstrap_corpus : journal  /tmp/essai/download.log
bootstrap_corpus : delai    1.0s entre deux requetes
bootstrap_corpus : versions 8.0,7.1
bootstrap_corpus : version 8.0 (8 livres)
  telecharge 1 pages
  ...
bootstrap_corpus : 27 page(s) telechargee(s), 0 echec(s)
pages figees : 27
   7.1       3 pages       0.1 Mo
   8.0      24 pages       1.0 Mo
fichiers dans corpus : 56
```

27 pages in **51 seconds** (measured on 19 November 2026). The pages come from
the official QNX site; the script keeps a download log with the SHA-256 of
each page.

## Step 5 - Build the complete snapshot of the documentation (about 2 hours)

```bash
cd qnx-qx-portmap && bash scripts/bootstrap_corpus.sh --out corpus-downloaded
```

**You should see:** the same progress, page by page, and then:

```text
bootstrap_corpus : corpus reconstruit dans <REPO>/corpus-downloaded
bootstrap_corpus : journal de telechargement : <REPO>/corpus-downloaded/download.log
bootstrap_corpus : sha256 du fichier SHA256SUMS : <SHA-256>
bootstrap_corpus : pour l'utiliser :
  QX_PORTMAP_CORPUS=<REPO>/corpus-downloaded qnx-portmap abort accept bzero
```

The snapshot holds about 4 000 pages (3 973 pages in 2 h 03, 0 failure,
measured on 18 November 2026) and three files you will use:

- `corpus-downloaded/index/pages.jsonl` - the index of the pages, with the
  SHA-256 of the original bytes of each page;
- `corpus-downloaded/SHA256SUMS` - the fingerprints of the stored files;
- `corpus-downloaded/download.log` - one line per downloaded page.

If the last line says `N echec(s)` (the pages the network cut off), run **the
same command again**: the pages already downloaded are kept in
`corpus-downloaded/cache/` and only the missing ones are fetched.

## Step 6 - The full answer, offline, with the quotations

```bash
cd qnx-qx-portmap && QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m qnx_portmap abort accept bzero
```

**You should see** (the real output measured on 19 November 2026 against the
frozen snapshot of the repository, 3 426 pages; with your own download only the
path, the page count and the consultation date change):

```text
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
```

The exit code of the command is **1**: `bzero` is `absent`, that is the symbol
your port has to deal with.

The three statuses you see here are the three cases of the method:

- `abort` has its own page in the 8.0 C Library Reference;
- `accept` has none in that reference, but the 8.0 documentation still
  describes it, in the io-sock User's Guide and in the FreeBSD manuals, and
  the official migration guide points to it explicitly;
- `bzero` was in the 7.1 reference and is gone from the whole 8.0 corpus.

You can check each of them by hand on the official documentation: the A-Z
index of the 8.0 C Library Reference is
<https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html>
and the one of the 7.1 reference is
<https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/lib-b.html>.

## Step 7 - Check that the snapshot is the official one

```bash
cd qnx-qx-portmap && QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m qnx_portmap --verify-corpus
```

**You should see:**

```text
corpus: <CORPUS>
pages checked: <N>
page SHA-256: OK
SHA256SUMS: OK (<N>+1 files)
```

`<N>` is the number of pages your own download produced: 3 973 pages measured
on 18 November 2026, while the frozen snapshot used for the proofs of this
repository holds 3 426 pages. Every page is compared with the SHA-256 of the
official page it was downloaded from, and the checksum file of the snapshot is
checked too. The command exits with code 0.

## Step 8 - Extract the calls of your own code

```bash
grep -ohE '[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(' my_code.c | tr -d '( \t' | sort -u | grep -vxE 'if|for|while|switch|return|sizeof|main' > calls.txt
```

**You should see:** a `calls.txt` file with one call per line. With this file:

```c
#include <stdlib.h>
void f(void) { abort(); bzero(p, 10); }
```

`calls.txt` holds 3 lines: `abort`, `bzero` and `f` (measured on 19 November
2026). Your own function `f` is in the list too - the tool will call it
`unknown`, which is right: it is not a QNX call. The last filter of the
pipeline removes the C keywords that the pattern catches as well (`if`,
`for`, `while`, `switch`, `return`, `sizeof`, `main`): on this three-line
example it changes nothing, on a real file it keeps a dozen keywords out of
the `unknown` symbols and out of the work list.

## Step 9 - Ask about your own calls

```bash
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m qnx_portmap --stdin --format json < calls.txt > state.json
```

**You should see:** a `state.json` file with one entry per call. Here is the
real output for the three calls of step 8, measured on 19 November 2026
against the frozen snapshot of the repository (with your own download, the
path of the corpus, the page counts and the consultation date change):

```json
{
 "tool": "QX PORTMAP",
 "version": "8.0",
 "previous_version": "7.1",
 "corpus": {
  "path": "<CORPUS>",
  "pages_total": 3426,
  "pages_by_version": {
   "7.1": 1200,
   "8.0": 2226
  },
  "consulted": "2026-11-14",
  "offline": true,
  "mode": "full"
 },
 "symbols": [
  {
   "symbol": "abort",
   "status": "documented",
   "kind": "function",
   "in_71": true,
   "in_80": true,
   "url": "https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html",
   "citation": "Raise the SIGABRT signal to terminate program execution",
   "citation_source": "index C Library Reference 8.0",
   "priority": 0
  },
  {
   "symbol": "bzero",
   "status": "absent",
   "kind": "function",
   "in_71": true,
   "in_80": false,
   "url": "https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html",
   "citation": "Set the first part of an object to null bytes",
   "citation_source": "index C Library Reference 7.1",
   "priority": 2
  },
  {
   "symbol": "f",
   "status": "unknown",
   "kind": "function",
   "in_71": false,
   "in_80": false,
   "url": "",
   "citation": "",
   "citation_source": "",
   "priority": 0
  }
 ],
 "worklist": [
  {
   "symbol": "bzero",
   "status": "absent",
   "priority": 2,
   "url": "https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html",
   "citation": "Set the first part of an object to null bytes"
  }
 ],
 "counts": {
  "symbols": 3,
  "documented": 1,
  "described_elsewhere": 0,
  "absent": 1,
  "unknown": 1
 }
}
```

The exit code of the command is **1**: `bzero` is `absent`.

The priority of a symbol is the order in which to deal with it:

| Priority | Meaning |
|---|---|
| `P1` | absent from the 8.0 documentation **and** cited by the official migration guide: the vendor says it is gone |
| `P2` | absent from the 8.0 documentation, with no official mention |
| `P3` | described elsewhere in the 8.0 documentation (index cross-reference) |

---

## How to verify

The repository replays every published proof of the project with one command:

```bash
cd qnx-qx-portmap && bash scripts/verify-all.sh
```

**You should see:** a table with one row per check, and then the verdict:

```text
VERDICT: NO CHECK FAILED - 6/8 OK, 2 NOT CHECKED (RC 0)
```

The eight checks are the unit test suite, the anti-leak control of the corpus,
the published manifest, the published numbers, the parity of the README, the
RED counter-proof, the lengths of the submission kit and the placeholders of
the documents. The two rows that need the corpus - the anti-leak control and
the parity of the README - are reported `NOT CHECKED`, never `OK`, because the
QNX documentation is not redistributed; the command still exits with code 0,
because nothing was disproved.

With the corpus of the project - the one the published proofs were made with,
that the repository does not redistribute - the same command replays every
proof and prints:

```text
VERDICT: EVERY CHECK PASSED - 8/8 OK (RC 0)
```

(measured on 19 November 2026: 202 tests and 1 skipped, 0 match with the QNX
documentation, `MANIFESTE-PUBLIE.txt lists 127 files`, every published count
is the real one, 10 / 10 rules counter-proved, nothing left in the 71
published documents.)

The unit test suite alone:

```bash
cd qnx-qx-portmap && python3 -m unittest discover -s tests -t .
```

**You should see:**

```text
Ran 202 tests in 1.335s

OK (skipped=33)
```

(202 tests, 33 skipped, exit code 0 - measured on 19 November 2026; only the
duration changes from one machine to another. The 33 skipped tests are the
ones that need the corpus: they are skipped, never failed.)

**One warning about the suite:** if you exported `QX_PORTMAP_CORPUS` in your
shell, unset it first. The README example is the output of the project
against *its* corpus, so the comparison test fails by design with another one
(`FAIL: test_readme_shows_the_real_output`, measured on 19 November 2026 with
a 76-page corpus). The commands of steps 6 and 7 set the variable for that
command only, so a plain `unset QX_PORTMAP_CORPUS` is enough. The suite also
needs room in the temporary directory (145 MB, see trap 4).

And the RED counter-proof, which breaks one rule of the code at a time and
checks that the matching test turns red:

```bash
cd qnx-qx-portmap && python3 tools/contre_epreuve.py
```

**You should see:** `10 / 10 contre-epreuves concluantes` (10 rules broken, 10
tests caught them, exit code 0) and the line `regle non testable ici (corpus
absent) : integrite du corpus fige livre`: the eleventh rule checks the
SHA-256 of every page of the corpus shipped with the tool, and the corpus is
not redistributed, so it cannot be tested in your clone. The output of the day
is kept in
[`docs/preuves/i-contre-epreuve-rouge-avec-corpus.txt`](../preuves/i-contre-epreuve-rouge-avec-corpus.txt)
(11 / 11 with the corpus present) and in
[`docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt`](../preuves/c-contre-epreuve-rouge-sans-corpus.txt)
(10 / 10 without it).

## The traps

1. **The corpus is not in the repository, and that is on purpose.** The QNX
   documentation is (c) QNX Software Systems Ltd / BlackBerry Limited and is
   not redistributable, so `corpus/index/pages.jsonl` and `corpus/SHA256SUMS`
   do **not** exist in your clone: the snapshot is rebuilt with
   `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`, which writes
   `corpus-downloaded/index/pages.jsonl` and `corpus-downloaded/SHA256SUMS`.
   Without it the tool says `corpus not found` and exits with code 2 - that
   is the correct behaviour, not a broken tool.
2. **`unknown` is not `absent`.** In the quick mode, `bzero` is `unknown`,
   because only the A-Z indexes and the migration guide were read; only the
   complete snapshot can decide `absent` or `described_elsewhere` for a symbol
   of the 7.1 index. The tool never claims to have read a book it has not
   read.
3. **The exit code 1 is the answer, not a failure.** `0` means every symbol
   is documented in 8.0, `1` means at least one symbol is `absent` or
   `unknown`, `2` means an error (the corpus is missing). After steps 3, 6 and
   9, the code `1` is the expected result.
4. **The test suite needs room in the temporary directory.** With the corpus
   present, the suite rebuilds a quick corpus of every symbol of the snapshot
   in `TMPDIR`: 145 MB measured on 19 November 2026. On a small `/tmp` the
   suite stops with `No space left on device`. Point the temporary directory
   somewhere with room before running the suite with the corpus:
   `TMPDIR=/tmp/qxpm python3 -m unittest discover -s tests -t .`

## Next step

Run the tool on the calls of your own project (steps 8 and 9) and work
through the work list: `P1` means the official migration guide of QNX 8.0
announces the removal of the call, `P2` that it has disappeared without any
official mention - the demonstration of the tool on a real QNX 8.0 target is
still pending the SDP 8.0 licence, **to be confirmed on QNX 8.0 on 20 November
2026**.

---

## AI-assisted development

The code, the tests and this codelab were written with an AI coding assistant
(**AI-assisted development**). Every claim about a QNX symbol is backed by an
exact quotation of an official page (URL, consultation date, and the SHA-256
of the page recorded in the corpus index), and the behaviour of the tool is
verified by an automated test suite plus a RED -> GREEN proof that breaks a
rule on purpose and shows the test catching it.

## Links

- Repository: <https://github.com/tgg49099-dotcom/qnx-qx-portmap>
- Usage guide: [`docs/UTILISATION.md`](../UTILISATION.md)
- Measurement on 100 real symbols: [`docs/mesure-J5.md`](../mesure-J5.md)
- QNX 8.0 documentation: <https://www.qnx.com/developers/docs/8.0/>
- QNX 8.0 C Library Reference, index of the A-Z symbols:
  <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html>

## Licence and copyright

The tool is MIT-licensed ([`LICENSE`](../../LICENSE)). The QNX documentation is
(c) QNX Software Systems Ltd / BlackBerry Limited and is neither redistributed
nor included in the repository; the short quotations in the tests and in the
measurements are cited with their URL, their date and the SHA-256 of the
source page ([`LICENCE-DOCS-QNX.md`](../../LICENCE-DOCS-QNX.md)).
