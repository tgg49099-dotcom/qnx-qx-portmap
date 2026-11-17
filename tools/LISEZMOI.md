# tools - working folder of QX PORTMAP

Sub-folder of the product **QX PORTMAP** (root: `qnx-portmap/`).
Read `../LISEZMOI.md` before starting: it describes the tool, the state of the
tests and the rules (no modification of the corpus `../corpus/`, no secret, no
CJK / Cyrillic / Greek character, no network access by default).

What this folder contains:

- `tools/`: `build_corpus.py` (deterministic construction of the corpus) and
  `contre_epreuve.py` (RED counter-proof).
- `tools/controle_placeholders.py`: the control of the placeholders of the
  published documents (no field of the submission kit and no section of the
  README may keep a placeholder, and the demonstration video URL must be the
  same in the README and in the kit). It is check 8 of
  `scripts/verify-all.sh`.

Verification commands (from the root `qnx-portmap/`):

```bash
python3 -m unittest discover -s tests -t .   # all the tests must pass
python3 tools/contre_epreuve.py               # 10/10 counter-proofs must be conclusive
python3 tools/controle_placeholders.py        # no placeholder must be left
```
