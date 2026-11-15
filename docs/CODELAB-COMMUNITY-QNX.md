# CODELAB (draft) - community.qnx.com

**Status: DRAFT, not published.** This file is the text proposed for a codelab
post on `community.qnx.com`. The owner publishes it (the forum needs an
account); the tool itself does not create accounts and does not post.

Suggested title: **"Codelab: map every QNX 8.0 symbol of your project to the
official documentation"**

---

## What you will build

A command that takes the symbols your QNX 8.0 code calls and tells you, for
each one, **whether the symbol is still documented in QNX 8.0, and where
exactly**: the official page, the exact quotation, and the SHA-256 of the page
the quotation comes from.

No guessing, no search engine, no account, no network access.

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
- A network connection **for step 2 only** (the corpus download). After that,
  the tool works offline.
- No QNX SDP, no QNX board, no QNX account, no API key.

## Step 1 - Get the tool

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap
pip install .
qnx-portmap --help
```

## Step 2 - Rebuild the QNX documentation corpus (once)

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

## Step 3 - Ask about your symbols

```bash
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort accept bzero
```

or, on a real project:

```bash
grep -o '[A-Za-z_][A-Za-z0-9_]*' mon_code.c | sort -u \
  | qnx-portmap --stdin --format json > state.json
```

## Step 4 - Read the answer

For each symbol, the output gives the status, the official page, the exact
quotation and the SHA-256 of the page. Four statuses:

| Status | Meaning |
|---|---|
| `documented` | the symbol has its own page in the QNX 8.0 C Library Reference |
| `described_elsewhere` | no page of its own in 8.0, but the 8.0 documentation still describes it |
| `absent` | it was in the C Library Reference 7.1 and is gone from the 8.0 corpus |
| `unknown` | not in the frozen corpus - typo, project macro, or published after 14 November 2026 |

The exit code tells you the same thing: `0` if every symbol is documented,
`1` if at least one is `absent` or `unknown`, `2` if the corpus is missing.

## Step 5 - How well does it work?

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

## AI-assisted development

The code, the tests and this codelab were written with an AI coding assistant
(**AI-assisted development**). Every claim about a QNX symbol is backed by an
exact quotation of an official page (URL, consultation date, SHA-256 of the
page), the behaviour of the tool is verified by an automated test suite, and
the published resolution rate is counted by hand on ten symbols given in the
test and compared with the number in the documentation.

## Links

- Repository: <https://github.com/tgg49099-dotcom/qnx-qx-portmap>
- Usage guide: `docs/UTILISATION.md` in the repository
- Measurement: `docs/mesure-J5.md` in the repository
- QNX 8.0 documentation: <https://www.qnx.com/developers/docs/8.0/>

## Licence and copyright

The tool is MIT-licensed (`LICENSE`). The QNX documentation is (c) QNX Software
Systems Ltd / BlackBerry Limited and is neither redistributed nor included in
the repository; the short quotations in the tests and in the measurements are
cited with their URL, their date and the SHA-256 of the source page
(`LICENCE-DOCS-QNX.md`).
