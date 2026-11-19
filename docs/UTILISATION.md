# USAGE - QX PORTMAP

Short usage guide: what the tool does, how to run it, and what exactly the
95 % figure means. For the complete explanation of the behaviour (8.0 index,
"described elsewhere" cross-references, two search passes), see the
[README](../README.md); for the detail of the measurement, see
[`mesure-J5.md`](mesure-J5.md).

## 1. What the tool does

QX PORTMAP takes a list of QNX symbols (functions, variables, constants)
and answers, for each one, with the **state of its documentation in QNX 8.0**:

| state | what the tool says |
|---|---|
| `documented` | the symbol has its own page in the 8.0 C Library Reference |
| `described_elsewhere` | no page of its own in 8.0, but the 8.0 documentation does describe it (cross-reference of the index, or a mention in another QNX 8.0 book) |
| `absent` | the symbol was in the 7.1 C Library Reference and has disappeared from the 8.0 corpus |
| `unknown` | not found in the frozen corpus: typo, macro of the project, or an addition published after 14/11/2026 - the tool does not guess |

For every symbol found, the tool displays the **official page**, the **exact
quotation** (the verbatim text of the page) and the **SHA-256 fingerprint** of
the page. It then produces a **work list**: the symbols to deal with, sorted
by priority, with the page to read.

The tool compiles nothing, does not run on a target and needs no network
access by default.

## 2. Install

```bash
# from the root of the repository
pip install .

# or, isolated, with pipx (https://pipx.pypa.io)
pipx install .

# or without installing anything
python3 -m qnx_portmap --help
```

**Python 3.8 or more, standard library only.** No dependency, no API key, no
account, no root privilege.

## 3. Run

```bash
# symbols on the command line
qnx-portmap abort accept bzero

# list in a file (one symbol per line, # comments are ignored)
qnx-portmap --file symbols.txt

# list on standard input (example: the symbols called by a project)
grep -o '[A-Za-z_][A-Za-z0-9_]*' my_code.c | sort -u | qnx-portmap --stdin --format json

# output formats
qnx-portmap --format markdown abort accept bzero > state.md
qnx-portmap --format json abort > state.json

# integrity check of the corpus
qnx-portmap --verify-corpus

# online reload (option, never used by default)
qnx-portmap --fresh --fresh-only
```

### Exit codes

| code | meaning |
|---:|---|
| `0` | every analysed symbol is documented in 8.0 |
| `1` | at least one symbol is `absent` or `unknown` (state of the documentation, not a program error) |
| `2` | execution error: corpus not found, no list given |

Exit code `1` is therefore **not** a failure of the tool: it is the expected
result when a symbol has disappeared from the documentation.

## 4. Where the corpus is

The tool looks for the frozen corpus in this order:

1. the `QX_PORTMAP_CORPUS` environment variable;
2. the `corpus/` directory of the repository (next to the package);
3. the `corpus/` directory of the current working directory.

The repository **does not contain** a `corpus/` directory: the QNX
documentation is not redistributable (see `LICENCE-DOCS-QNX.md`). Without a
corpus, the tool prints `corpus not found` (`corpus introuvable` with
`--lang fr`) and exits with code `2` - it guesses nothing.

### Rebuilding the corpus (one command, one log)

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
```

The script downloads the official QNX 7.1 and 8.0 documentation from
`https://www.qnx.com/developers/docs/`, keeps the download log, and computes
the SHA-256 fingerprint of every page. A quick test (3 pages per book, to
check the network access; 27 pages, 51 seconds measured on 15/11/2026):

```bash
bash scripts/bootstrap_corpus.sh --out /tmp/essai --max-pages 3 --delay 1.0
```

The rebuilt corpus is verifiable: `qnx-portmap --verify-corpus`.

## 5. The 95 % figure: what it means

On the reference sample (100 QNX symbols really called by **five public QNX
repositories**, pinned commits, list of the 100 symbols in
[`mesure-J5.md`](mesure-J5.md)):

| state | number |
|---|---:|
| resolved and quoted (QNX 8.0 page + quotation + SHA-256) | **95** |
| resolved but described elsewhere | 0 |
| not resolved | 5 |
| **rate** | **95 %** |

The 5 unresolved symbols are **honest**: four of them had a page in the 7.1 C
Library Reference and have none in 8.0 (`ND_NODE_CMP`,
`pthread_sleepon_lock`, `pthread_sleepon_unlock`, `fcfgopen`); the fifth,
`InterruptAttach`, is reported as **removed in 8.0 according to the official
migration guide** - the tool quotes the sentence: "The following functions
have been removed: InterruptAttach() InterruptAttachArray() InterruptHookIdle2()
InterruptHookTrace()". The tool declares them `absent` with the link to their
7.1 page or to the page of the guide: it does not invent them, it does not
erase them. This is the **honest ceiling** of the rate on this sample: when
the official guide says a function was removed, the tool says so instead of
counting it resolved (the rate was 96 % before that rule, on 19/11/2026).

**What 95 % does not mean**:

- it is not a guarantee for your project: a sample is a sample;
- the tool analyses the **documentation**, not the binary: `absent` means
  "absent from the frozen 8.0 documentation", not "absent from the system";
- the corpus is a **snapshot** of 14/11/2026: a symbol published since then is
  classified `unknown` as long as the corpus is not rebuilt (`--fresh`);
- a prose mention is enough to classify a symbol as `described_elsewhere`, but
  the quotation then says `mention`: you have to check that the symbol really
  is a function call.

## 6. Check the tool (do not believe it)

```bash
python3 -m unittest discover -s tests -t .
```

Without the corpus: 202 tests, 33 of them skipped (the test says so, it does
not lie). With the corpus: 202 tests, 1 skipped, exit code 0.
(Figures re-measured on 19/11/2026.)

The **RED -> GREEN** proof (a rule is broken, the test fails, the code is
restored, the test passes again) is in [`preuves/`](preuves/); the detail of
the measurements and of the methods in [`mesure-J4.md`](mesure-J4.md) and
[`mesure-J5.md`](mesure-J5.md).

## 7. Troubleshooting

| symptom | cause | solution |
|---|---|---|
| `corpus not found` (`corpus introuvable` with `--lang fr`), code 2 | the corpus is not in the tree | `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`, then `QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort` |
| `unknown` for a symbol that exists | added after 14/11/2026 | rebuild the corpus (`--fresh`) or check the spelling |
| `absent` for a symbol in use | it has disappeared from 8.0 | read the quoted 7.1 page; it is a state of the documentation, not an error |
| a quotation looks badly formatted | the official HTML has an irregular formatting | the text is verbatim, the punctuation is not always so |

## 8. Licence

The code is under the MIT licence (`LICENSE`). **The QNX documentation is not
redistributed**: see `LICENCE-DOCS-QNX.md` and `CORPUS-NON-PUBLIE.txt`.
