# Codelab: find out which QNX calls your project makes are still documented in QNX 8.0

**Codelab / tutorial - QNX 8.0 - 17 November 2026**

Published as a tutorial in this repository; the owner may also post it on
community.qnx.com.

URL of this tutorial:
<https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/CODELAB-COMMUNITY-QNX.md>

---

## The task

You maintain C code that calls the QNX C Library, and you have to move it to
QNX 8.0. The call itself is not the hard part. The hard part is knowing
**which of the calls your code makes still exist in the QNX 8.0
documentation**, which ones have moved to another book, and which ones have
disappeared - because each case needs a different decision in your port.

**In this codelab you will do exactly that job**, on a small but real task:
take a list of QNX symbols, find out for each one whether QNX 8.0 still
documents it, and produce the work list of the calls you have to deal with.

You will do it twice:

- **by hand**, on the official QNX 8.0 documentation (about 10 minutes) - this
  is the method that works when you have no tool at all;
- **with QX PORTMAP**, the tool of this repository (about 5 minutes) - the
  same work, automated, reproducible and quotable.

## What you will build

A command that takes the symbols your QNX 8.0 code calls and tells you, for
each one, **whether the symbol is still documented in QNX 8.0, and where
exactly**: the official page and the exact quotation taken from it. The
SHA-256 of every page of the snapshot is recorded in the corpus index, and
step 7 shows how to check them.

No guessing, no search engine, no account, no network access once the
documentation snapshot is built.

## Why it is useful

When you port or maintain QNX code, the hard part is not calling an API - it is
knowing whether that API still exists in the documentation you are targeting.
A symbol can be documented, described somewhere else (the 8.0 index points to
another book or to the FreeBSD manuals for the retired BSD calls), or gone
from the reference entirely. QX PORTMAP tells those three cases apart, and
tells you the fourth one - `unknown` - instead of inventing an answer.

It also produces a **work list**: the symbols to deal with, sorted by
priority, with the page to read for each.

## Who it is for

- developers porting QNX 6.x / 7.1 code to QNX 8.0 ;
- anyone who wants an offline, reproducible index of the QNX 8.0 C Library
  Reference ;
- teachers and students who want to show, on real code, how a documentation
  gap looks.

## Prerequisites

- Python 3.8 or later (standard library only, no dependency to install).
- A network connection **for step 3 only** (the corpus download). After that,
  the tool works offline.
- No QNX SDP, no QNX board, no QNX account, no API key.

---

## Step 1 - Do it by hand, once (the QNX 8.0 documentation)

Before any tool, look at the documentation yourself. The QNX 8.0 C Library
Reference has one A-Z index page per letter:

```text
https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html
https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-b.html
```

(there are 26 of them, `lib-a.html` to `lib-z.html`).

**You should see:** the page titled `B` is the index of the symbols that start
with a `b`.

Now look for two symbols in it:

1. **`abort`** - open
   <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html>
   and search for `abort`.
   **You should see:** one entry, `abort`, whose link points to
   `topic/a/abort.html`. Open it: the page of the function, with its
   synopsis and its description. The call is **documented in QNX 8.0**.

2. **`bzero`** - search for `bzero` in the `B` index of the 8.0 reference.
   **You should see: nothing.** No entry, no link.
   Now open the same index of the **7.1** reference:
   <https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/lib-b.html>
   **You should see:** one entry, `bzero`, pointing to
   `topic/b/bzero.html`. The call **was documented in 7.1 and is not in 8.0**:
   that is the call you have to deal with in your port.

This is the whole method. It works, but it is slow, and it does not scale:
a project calls hundreds of symbols.

## Step 2 - Get the tool

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap
pip install .
qnx-portmap --help
```

**You should see:** the usage of the command, ending with

```text
Examples: qnx-portmap abort pthread_create bzero qnx-portmap --file
symbols.txt --format markdown cat symbols.txt | qnx-portmap --stdin --format
json qnx-portmap --verify-corpus
```

If `pip` refuses to install (PEP 668), use a virtual environment instead:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

## Short on time? The 2-minute path (quick mode)

Step 3 builds the full snapshot, which takes more than an hour at one request
per second. If you only want to see the tool answer first, the **quick mode**
downloads only the 26 A-Z index pages of 8.0 and of 7.1, the migration guide
and the page of each documented symbol (76 pages, **about two to three
minutes**: 127 s and 144 s measured on 16 November 2026, 94 s and 151 s on
17 November 2026 - the QNX site is not always as fast; the tool writes the
real duration of **your** run in `corpus-quick/MANIFEST.json`, under
`quick.seconds`), and answers at once:

```bash
qnx-portmap --quick abort accept bzero zzz_fonction_inexistante
```

**You should see** (the four symbol lines; the details are the same as in
step 4):

```text
  abort                        documented
  accept                       described elsewhere
  bzero                        unknown
  zzz_fonction_inexistante     unknown
```

and at the end:

```text
(+ 2 unknown symbol(s), not decided by the quick mode: bzero, zzz_fonction_inexistante - the full corpus decides them)
```

The exit code of that command is `1`, because two symbols are `unknown` (see
step 5): that is the expected code, not a failure of the tool.

`bzero` is `unknown` here, not `absent`: the quick mode has read only the
indexes, so it cannot prove that no other 8.0 book describes the call. It
**never** says `absent`; only the full snapshot of step 3 can. That is the
same rule as in step 1: what you have not read, you do not claim.

## Step 3 - Build the snapshot of the QNX documentation (once)

The QNX documentation is proprietary and is **not** redistributed with the
repository. One command downloads the official pages (QNX 7.1 and 8.0), keeps a
download log and computes the SHA-256 of every page:

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
```

A quick 3-pages-per-book trial, to check the access (27 pages, 51 seconds
measured on 15 November 2026):

```bash
bash scripts/bootstrap_corpus.sh --out /tmp/essai --max-pages 3 --delay 1.0
```

**You should see** (the trial):

```text
bootstrap_corpus : sortie   /tmp/essai
bootstrap_corpus : cache    /tmp/essai/cache
bootstrap_corpus : journal  /tmp/essai/download.log
bootstrap_corpus : delai    1.0s entre deux requetes
bootstrap_corpus : versions 8.0,7.1
```

and at the end, the list of the pages that were downloaded, one line per page
in `corpus-downloaded/download.log`, with the SHA-256 of each one.

The full run downloads about 4 000 pages of the official documentation
(3 973 pages measured on 18 November 2026: 1 747 pages of 7.1 and 2 226 pages
of 8.0; the frozen snapshot used by the project holds 3 426 pages), at one
request per second: plan **about two hours** (1.7 to 2 s per page, measured on
15 and 16 November 2026; 1.87 s per page over the complete judge replay of
18 November 2026: 3 973 pages in 2 h 03, 0 failure). Start it, and do step 5
while it runs.

If the last line says `N echec(s)` (pages the network cut off), run **the same
command again**: the pages already downloaded are kept in the `cache/` folder
and are not downloaded twice; only the missing ones are fetched.
After that, the tool never uses the network again.

## Step 4 - Ask about your symbols

```bash
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort accept bzero
```

**You should see** (the `<CORPUS>` line is the path where you built the
snapshot, it is the only line that changes from one machine to another):

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

and the exit code:

```bash
echo $?
```

**You should see:** `1` - one symbol (`bzero`) is `absent`. That is the
expected code, not a failure of the tool.

Compare with what you found by hand in step 1: `abort` is documented,
`bzero` has disappeared, and `accept` - which you would not have found in the
A-Z index of the C Library Reference - is described elsewhere in the QNX 8.0
documentation, in the io-sock User's Guide and in the FreeBSD manuals. The
migration guide of QNX 8.0 points to it explicitly.

And if one of the symbols does not exist at all - a typo, or a macro of your
own project?

```bash
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap zzz_fonction_inexistante
```

**You should see:**

```text
QX PORTMAP - status of QNX symbols in the 8.0 documentation
frozen corpus: <CORPUS>
pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

  zzz_fonction_inexistante     unknown
    note   : not found in the frozen 8.0 corpus: unknown symbol, typo, or added after 2026-11-14

--- Upgrade worklist (0 symbol(s)) ---
(nothing to migrate among the decided symbols)
(+ 1 unknown symbol(s), not in this list: zzz_fonction_inexistante - check the spelling, or a symbol added after the corpus date)
```

The tool does **not** invent a page for it, and it does not drop it silently:
an unknown symbol is always named after the work list.

## Step 5 - Read the answer

For each symbol, the output gives the status, the official page and the exact
quotation. Four statuses:

| Status | Meaning |
|---|---|
| `documented` | the symbol has its own page in the QNX 8.0 C Library Reference |
| `described_elsewhere` | no page of its own in 8.0, but the 8.0 documentation still describes it |
| `absent` | it was in the C Library Reference 7.1 and is gone from the 8.0 corpus |
| `unknown` | not in the frozen corpus - typo, project macro, or published after 14 November 2026 |

The exit code tells you the same thing: `0` if every symbol is documented,
`1` if at least one is `absent` or `unknown`, `2` if the corpus is missing.

## Step 6 - Work on your own project

The point of the tool is your own code. Extract the symbols your project
calls, and give them to the tool:

```bash
grep -ohE '[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(' my_code.c \
  | tr -d '( \t' | sort -u \
  | grep -vxE 'if|for|while|switch|return|sizeof|main' > calls.txt
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded \
  qnx-portmap --stdin --format json < calls.txt > state.json
```

The first command keeps only the words followed by `(` - the calls - and
drops the C keywords and `main`. Without it, every word of the file (types,
variables, `include`, `h`...) would come back as `unknown` and hide the real
work list.

With this two-line file:

```c
#include <stdlib.h>
void f(void) { abort(); bzero(p, 10); }
```

the first command gives 3 calls (`abort`, `bzero`, `f`), and the tool answers:
`abort` is `documented`, `bzero` is `absent`, `f` is `unknown` - it is your
own function, not a QNX call.

Without the filter, the same file would give 8 "symbols" (`abort`, `bzero`,
`f`, `h`, `include`, `p`, `stdlib`, `void`), 6 of them `unknown`. Check
`calls.txt` by eye: your own functions are in it too (`f` above), and the
tool rightly calls them `unknown`.

**You should see:** a `state.json` file with one entry per call. Here is the
real output for one symbol (`qnx-portmap --format json abort`), so that you
know every field it gives:

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
   "citation_kind": "",
   "see_urls": [],
   "mentioned_in_migration_guide": false,
   "migration_urls": [],
   "detail": "The abort() function causes abnormal process termination to occur by means of the function call raise ( SIGABRT ) , unless the signal SIGABRT is caught and the signal handler doesn't return. If the signal SIGABRT is caught and the signal handler returns, the signal handler is removed and raise ( SIGABRT ) is called again. Note that prior to calling raise() , abort() ensures that SIGABRT isn't ignored or blocked.",
   "note": "present in 7.1 and in 8.0",
   "priority": 0
  }
 ],
 "worklist": [],
 "counts": {
  "symbols": 1,
  "documented": 1,
  "described_elsewhere": 0,
  "absent": 0,
  "unknown": 0
 }
}
```

With your own list, the `symbols` array holds one entry per symbol, and
`counts` gives the number of symbols in each status.

The JSON uses English field names in both languages (`--lang fr` translates
the console messages, not the JSON), so it can be diffed in a CI job.

To see only the calls you have to deal with, ask for the work list (the
symbols are still needed: `--worklist` is a filter, not a source):

```bash
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap --worklist abort accept bzero
```

**You should see:** the same answer, and at the end the work list - the
symbols to deal with, sorted by priority, each one with the page to read and
the reason:

| Priority | Meaning |
|---|---|
| `P1` | absent from the 8.0 documentation **and** cited by the official migration guide: the vendor says it is gone |
| `P2` | absent from the 8.0 documentation, with no official mention |
| `P3` | described elsewhere in the 8.0 documentation (index cross-reference) |

In the example above, `bzero` is `P2` and `accept` is `P3`.

## Step 7 - Check that the tool tells the truth

```bash
python3 -m unittest discover -s tests -t .
```

**You should see:**

```text
Ran 202 tests in 1.0s

OK (skipped=33)
```

The 33 skipped tests are the ones that need the complete frozen snapshot; with
the snapshot in `corpus/` next to the package, they run too. The suite also
contains a RED -> GREEN proof: `tools/contre_epreuve.py` breaks one rule of
the code at a time and checks that the matching test turns red, then restores
the repository.

The corpus itself can be verified, page by page, against the SHA-256 of the
official pages:

```bash
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap --verify-corpus
```

**You should see:**

```text
corpus: <CORPUS>
pages checked: 3426
page SHA-256: OK
SHA256SUMS: OK (3427 files)
```

that is: every page of the snapshot matches the fingerprint of the official
page it was downloaded from, and the checksum file of the snapshot matches
too.

## Step 8 - How well does it work?

On the reference sample - the 100 QNX symbols really called by **five public
QNX repositories** (the official QNX BSP for Raspberry Pi 5, another QNX BSP
for Raspberry Pi, the QNX Neutrino resource-manager sources, the QNX Signal
Framework and a SocketCAN driver), with pinned commits - the tool resolves and
quotes **96 %** of the symbols.

The four it does not resolve are honest misses: they had a page in the 7.1
reference and have none in the 8.0 one. The tool says so and gives the 7.1
link; it does not invent a page. The full list of the 100 symbols, the pinned
commits and the method are in `docs/mesure-J5.md` in the repository.

## What it does not do

- It does not analyze binaries: it reads **documentation**.
- It does not distribute the QNX documentation.
- It does not guess: `unknown` stays `unknown`.
- It does not need the network once the corpus is built.
- It is a **host** tool: it does not run on a QNX 8.0 target, it reads the
  QNX 8.0 documentation from your own machine.

## AI-assisted development

The code, the tests and this codelab were written with an AI coding assistant
(**AI-assisted development**). Every claim about a QNX symbol is backed by an
exact quotation of an official page (URL, consultation date, and the SHA-256 of
the page recorded in the corpus index), the behaviour of the tool is verified
by an automated test suite, and the published resolution rate is counted by
hand on ten symbols given in the test and compared with the number in the
documentation.

## Links

- Repository: <https://github.com/tgg49099-dotcom/qnx-qx-portmap>
- Usage guide: `docs/UTILISATION.md` in the repository
- Measurement: `docs/mesure-J5.md` in the repository
- QNX 8.0 documentation: <https://www.qnx.com/developers/docs/8.0/>
- QNX 8.0 C Library Reference index: <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/lib-a.html>

## Licence and copyright

The tool is MIT-licensed (`LICENSE`). The QNX documentation is (c) QNX Software
Systems Ltd / BlackBerry Limited and is neither redistributed nor included in
the repository; the short quotations in the tests and in the measurements are
cited with their URL, their date and the SHA-256 of the source page
(`LICENCE-DOCS-QNX.md`).
