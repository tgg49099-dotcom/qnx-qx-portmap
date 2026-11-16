# tests - working folder of QX PORTMAP

Sub-folder of the product **QX PORTMAP** (root: `qnx-portmap/`).
Read `../LISEZMOI.md` before starting: it describes the tool, the state of the
tests and the rules (the QNX corpus is not in the repository, no secret, no
CJK / Cyrillic / Greek character, no network access by default).

What this folder contains:

- `test_*.py`: the tests (unittest, no dependency). The new tests go here; they
  must all be green.
- `fixtures/`: 12 short extracts (1 to 3 lines) of QNX pages, with the source
  URL and the consultation date. They are the only traces of QNX documentation
  present in the repository.
- `helpers.py`: common tools, among them `build_fixture_corpus()` which
  rebuilds a miniature corpus in the real format from the fixtures, and the
  skip message `corpus absent : lancer scripts/bootstrap_corpus.sh`.

Verification commands (from the root `qnx-portmap/`):

```bash
python3 -m unittest discover -s tests -t .   # 184 tests: green, 32 skipped without corpus
python3 tools/contre_epreuve.py               # 10/10 counter-proofs must be conclusive
```

Without the complete corpus, the tests that depend on it are **skipped** (never
failed); the tests based on the fixtures always pass.
