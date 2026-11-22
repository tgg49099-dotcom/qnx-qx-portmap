# Licence of the QNX documentation and of the QX PORTMAP code

**Date the sources were consulted: 14/11/2026.**

## 1. The QNX documentation is not redistributed

The QNX documentation pages cited by this tool (C Library Reference,
User's Guide, io-sock User's Guide, Programming Guide, System Tuning Guide,
Migration Guide) are:

> (c) QNX Software Systems Ltd / BlackBerry Limited.

They are **not redistributed** with this repository. No verbatim copy, neither
complete nor partial beyond the 12 short extracts stored in
`tests/fixtures/`, is published. See `CORPUS-NON-PUBLIE.txt` for the detail and
the rebuild procedure.

Official copyright page of the QNX 8.0 documentation (consulted on
14/11/2026):

  https://www.qnx.com/developers/docs/8.0/com.qnx.doc.copyright/topic/coverpage.html

That page states that the licence information specific to each file is in the
QNX Software Center, accessible with a myQNX account. It gives no permission
to redistribute the documentation pages. No request for permission has been
addressed to QNX or to BlackBerry: the choice made is not to redistribute.

The 12 fixtures of `tests/fixtures/` are extracts of 1 to 3 lines, quoted with
their source URL and the consultation date, as a proof that the tool works on
real documentation. Each fixture also carries the SHA-256 fingerprint of the
complete page it is taken from.

## 2. The code is free (MIT)

The code of QX PORTMAP (in `qnx_portmap/`, `tests/`, `tools/`, `scripts/`) is
distributed under the MIT licence: see the file `LICENSE` at the root of the
repository.

Copyright (c) 2026 QX PORTMAP contributors.

The MIT licence does not apply to the QNX documentation: it covers neither the
documentation pages nor the fixtures, which remain the property of QNX
Software Systems Ltd / BlackBerry Limited and are quoted as extracts.

## 3. The other cited sources

The cross-references of the QNX documentation point to third-party pages,
cited without being reproduced:

- the FreeBSD documentation (`man.freebsd.org`), cited by the QNX
  documentation itself in its "described elsewhere" cross-references;
- the official QNX documentation site (`www.qnx.com/developers/docs/`), the
  only source of the cited pages.

## 4. Summary

| Element | Status |
|---|---|
| Code of the tool (`qnx_portmap/`, `tests/`, `tools/`, `scripts/`) | MIT, redistributable |
| QNX documentation (3 426 pages) | (c) QNX Software Systems Ltd / BlackBerry Limited - **not redistributed** |
| 12 fixtures (extracts of 1 to 3 lines) | (c) QNX Software Systems Ltd / BlackBerry Limited - quoted with URL and date |
| Frozen corpus (local archive of the slot) | outside the repository, never published |
