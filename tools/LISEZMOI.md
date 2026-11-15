# tools - working folder of QX PORTMAP

Sub-folder of the product **QX PORTMAP** (root: `qnx-portmap/`).
Read `../LISEZMOI.md` before starting: it describes the tool, the state of the
tests and the rules (no modification of the corpus `../corpus/`, no secret, no
CJK / Cyrillic / Greek character, no network access by default).

What this folder contains:

- `tools/`: `build_corpus.py` (deterministic construction of the corpus) and
  `contre_epreuve.py` (RED counter-proof).

Verification commands (from the root `qnx-portmap/`):

```bash
python3 -m unittest discover -s tests -t .   # all the tests must pass
python3 tools/contre_epreuve.py               # 10/10 counter-proofs must be conclusive
```
