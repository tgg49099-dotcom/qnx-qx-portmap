# qnx_portmap - working folder of QX PORTMAP

Sub-folder of the product **QX PORTMAP** (root: `qnx-portmap/`).
Read `../LISEZMOI.md` before starting: it describes the tool, the state of the
tests and the rules (the QNX corpus is not in the repository, no secret, no
CJK / Cyrillic / Greek character, no network access by default).

What this folder contains:

- `qnx_portmap/`: the package itself (6 modules). The fixes are made here.
  The logic of the tool does not change: the repository is publishable as is.

Verification commands (from the `qnx-portmap/` root):

```bash
python3 -m unittest discover -s tests -t .   # 164 tests: green, 26 skipped without corpus
python3 tools/contre_epreuve.py               # 10/10 counter-proofs must be conclusive
```

The French version of this file is kept byte-identical in
`qnx_portmap/LISEZMOI-FR.md`.
