# QX PORTMAP - product package

**Tool**: given a list of QNX symbols (functions, variables, constants), tell
for each one its state in the official QNX 8.0 documentation - `documented`,
`described_elsewhere`, `absent` or `unknown` - with **the official page** and
**the exact quotation**, then produce the **upgrade work list**.

**Single function** (this is the criterion of the contest: tool 2, different
from QX Probe). Input: a list of symbols. Output: a documentation status per
symbol. Source: the official QNX 7.1 and 8.0 documentation. No SDP access, no
compilation, no network by default.

## State

Working V0 (14/11/2026). **200 tests, all green** (33 of them are skipped when
the corpus is absent). RED counter-proof: 11/11 with
the corpus, 10/10 without it (the rule on the integrity of the frozen corpus
cannot be tested without it).

**Measurement J4 (14/11/2026)**: on the 100 QNX symbols really called by 5
public QNX repositories, the tool resolves and quotes **93 %**
(`docs/mesure-J4.md`).

```
python3 -m unittest discover -s tests -t .        # 200 tests (33 skips without corpus)
python3 tools/contre_epreuve.py                    # 11/11 conclusive counter-proofs
python3 tools/mesure_j4.py --clones <folder>      # re-measure J4 (public QNX clones)
qnx-portmap abort accept bzero                    # real example (see README.md)
```

## Tree

The repository is **publishable**: it no longer contains the QNX documentation.

| Path | Content | Size |
|---|---|---|
| `qnx_portmap/` | the package (6 modules, standard library only) | ~66 KB |
| `tests/` | 200 tests, among them 21 on the miniature fixtures and 16 on the J4 measurement | ~130 KB |
| `tests/fixtures/` | 12 short extracts (1 to 3 lines) of QNX pages, with URL and date | ~4 KB |
| `tools/` | corpus construction, fixtures, RED counter-proof, J4 measurement | ~136 KB |
| `scripts/` | corpus bootstrap, published manifest, anti-leak control | ~30 KB |
| `docs/` | RED counter-proof, demonstration, proofs, J4 and J5 measurements | ~170 KB |
| `PROGRESSION.md` | one line per function of the tool (state + the test that proves it) | ~16 KB |
| `MANIFESTE-PUBLIE.txt` | path, size and SHA-256 of every publishable file | ~9 KB |
| `corpus/` | **absent from the repository** - rebuilt on demand, see below | 0 |

## Frozen corpus: read this before touching it

The QNX documentation corpus (3 426 official HTML pages, 44.9 MB compressed) is
**no longer in this repository**: it is (c) QNX Software Systems Ltd /
BlackBerry Limited and is not redistributed. The documentation remains the
source, it is downloaded on demand from the official site.

- The local archive of the slot (outside the repository, never published) is in
  `/work/qnx-portmap-corpus-local/corpus/`, with its `CORPUS-FIGE.txt`
  anchoring file.
- To rebuild a corpus: `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`
  (delay between the requests, `download.log` log, refuses to write into a
  frozen corpus).
- For the tool: `QX_PORTMAP_CORPUS=/path/to/corpus qnx-portmap ...`.
- **The frozen corpus is never modified, never republished.** Every QNX page
  that appears in this repository is a short extract: 12 extracts of 1 to 3
  lines in `tests/fixtures/` and the 100 citations of the J4 measurement in
  `docs/mesure-J4/citations-*.txt`, quoted with their URL, the consultation
  date and the SHA-256 fingerprint of the source page.
- The control `python3 scripts/controle_fuite_corpus.py --tree . --corpus <corpus>`
  proves that no publishable file contains a QNX page (0 match) and that no
  file exceeds 4 000 bytes of verbatim QNX text.

## Product rules

- **Python 3.8+**, standard library only: no dependency to add.
- **No network access** in the default mode. `--fresh` is an option, not the
  normal mode.
- Every symbol absent from the corpus must stay `unknown`: **never guess** a
  status.
- A quotation must be **verbatim** from the official page, never reworded.
- A test that always passes does not test anything: every test has at least
  one case that makes it fail.
- A test that requires the complete corpus is **skipped** (never failed) when
  the corpus is absent; the message is
  `corpus absent : lancer scripts/bootstrap_corpus.sh` (the exact message of the
  test framework, in French, quoted as it is printed).
- `MANIFESTE-PUBLIE.txt` is **regenerated after every change**:
  `python3 scripts/manifeste_publie.py` (verification: `--check`).
- No CJK / Cyrillic / Greek character in the files written.
- No secret, no key, no API URL with a key.
