# Running QX PORTMAP on a QNX 8.0 target

**Status, 16/11/2026**: the procedure below is written from the official QNX
documentation, and the command it gives has been rehearsed on a Linux
workstation. **It has not been run on a QNX 8.0 target yet**, because the QNX
SDP 8.0 is not installed in this environment: the licence is the owner's
action, not a technical step. Nothing in this document claims a run that did
not happen.

This document is the missing segment of the demonstration video: the contest
rules ask that "the repository must show that the project genuinely builds
for or runs on QNX 8.0, not merely that QNX 8.0 is named in the README"
(`https://qnx.devpost.com/rules`, read on 15/11/2026).

## 1. What the tool needs on the target

| need | detail | source |
|---|---|---|
| Python 3, standard library only | The SDP 8.0.3 ships a Python 3.13 **for QNX OS targets**: "QNX SDP 8.0 Utilities - Python 3.13 (QNX OS)", package `com.qnx.qnx800.target.utils.python3`, internal version `3.13.7.00013T202603200501L` | release notes of the 8.0.3 target-side utilities (see section 6) |
| the frozen corpus of the QNX documentation | The QNX documentation is **not redistributed** with this repository (see `CORPUS-NON-PUBLIE.txt`). The corpus must be copied to the target, or built on the target itself | `CORPUS-NON-PUBLIE.txt` |
| nothing else | no compiler, no third-party Python package, no QNX account, no root privilege, no network (once the corpus is there) | the imports of the package are `argparse`, `collections`, `gzip`, `hashlib`, `html`, `json`, `os`, `re`, `string`, `sys`, `time`, `urllib`: the standard library only |

The last point is what makes the tool a **host tool** that also fits a QNX
target: it is the same code, the same command, and the same answers.

**Measured on 16/11/2026, not assumed.** The package `qnx_portmap/` (9 files)
needs **Python 3.4 or later** (`vermin --no-parse-comments --target=3.13-
--violations qnx_portmap/` -> "Minimum required versions: 3.4"), so the
Python 3.13.7 of the SDP 8.0.3 target is new enough for it. The modules it
imports are `argparse`, `collections`, `gzip`, `hashlib`, `html`, `json`, `os`,
`re`, `string`, `sys`, `time`, `urllib`: **none of them is among the modules
that Python 3.13 removed** (PEP 594, "Removal of dead batteries"), and there is
no third-party dependency to install on the target. The measurement is
reproducible with `pip install vermin` and the command above (working copy of
the output: `/work/preuves-qnx13/PROMESSE-PYTHON-CIBLE.txt`); the target
check itself prints a `compat` line, so the day it runs on the real target the
compatibility is shown on the screen and not only in this document.

## 2. Two ways to get a QNX 8.0 target

**a. QNX Everywhere and the Quick Start Target Image (free).** The QNX
Everywhere licence is free for non-commercial use: "This license grants free
access to QNX Software Development Platform 8.0 for individual non-commercial
users". It needs a myQNX account: "To receive your license, you must have a
myQNX account", then the three steps are to log in, complete the QNX
Everywhere licence form, and receive the licence (the page asks to allow up
to one hour). The offer includes the **Quick Start Target Image for
Raspberry Pi**: packages `com.qnx.qnx800.quickstart.rpi4` and
`com.qnx.qnx800.quickstart.rpi5`, installed with the QNX Software Center
next to the SDP 8.0, giving an `.img` file that is written to a microSD card
with Raspberry Pi Imager; the image repository is
`gitlab.com/qnx/quick-start-images/raspberry-pi-qnx-8.0-quick-start-image`.
The September 2025 release notes of QNX Everywhere state that "The Python
package manager (PIP) is now installed by default on the QSTI": the target
image already carries Python. (Release of 11 September 2025: the QSTI and
the Custom Target Image repository for Raspberry Pi 4B are upgraded to the
SDP 8.0.3.)

**b. The SDP 8.0 and a QEMU image.** `mkqnximage` builds a system image for
QEMU: `mkqnximage --type=qemu --arch=x86_64 --run` builds it and starts it
(`--run=-h` runs it headless, with the console output in `output/qemu.out`).
`--getip` gives the address of the running image, and the image ships an ssh
server with the accounts `root`, `qnxuser` and `user1` to `user6`. The x86_64
target of the SDP is also where the target-side Python of section 1 comes
from.

Route (a) is the one that needs the least: a Raspberry Pi 4 or 5, a
microSD card, and the free licence. Route (b) stays on x86_64, on the same
PC as the SDP and the video capture. Both need the licence; neither needs
to buy anything.

## 3. The command to film

From the root of the repository, **on the target**:

    sh scripts/qnx8_target_check.sh /path/to/corpus abort accept bzero

One command, one screen. It proves four things, in this order: the system is
a QNX system and which version; a Python 3 interpreter is there, and new
enough for the package; the corpus is there and **every page matches its
SHA-256**; the tool answers for the symbols that are asked. The last lines are
the verdict:

    -- verdict --
    verify-corpus exit code : 0 (0 = every page matches its SHA-256)
    symbols exit code       : 1 (0 = every symbol documented, 1 = at least one absent or unknown, 2 = error)
    compat exit code        : 0 (0 = the interpreter is new enough for the package)
    RESULT      : PASS

The exit code 1 of the second line is the expected one: it means the tool
answered and that at least one symbol is not documented in 8.0.

Two variables replace the arguments when needed: `QX_PORTMAP_CORPUS` for the
directory of the corpus, and `QX_PORTMAP_PYTHON` for the path of the
interpreter when it is not in the `PATH` of the console of the target (the
release notes of the target-side utilities do not publish the path of the
interpreter on the target).

## 4. Getting the corpus onto the target

**Offline (recommended).** On the host, with the network:

    bash scripts/bootstrap_corpus.sh --out corpus

then copy the `corpus` directory to the target (ssh, `qconn`, a USB key or
the microSD card, depending on the route of section 2). The corpus is the
QNX documentation: copy it for your own use, do not publish it.

**Online.** The quick mode builds a small corpus on the machine that runs it,
at one request per second: `python3 -m qnx_portmap --quick abort accept
bzero`. On the target it needs a network and a Python built with `ssl`.

## 5. The rehearsal, on a Linux workstation (what is verified today)

The same command, run on 16/11/2026 on a Debian 12 workstation with
`/bin/sh` (dash) and with `bash`, from the root of the repository and from
another directory:

    sh scripts/qnx8_target_check.sh /work/qnx-portmap-corpus-local/corpus abort accept bzero

Real output (the answers are the real output of the tool on the frozen
corpus, not a transcription):

    system      : Linux 6.8.0-149-generic (x86_64)
    target      : NOT a QNX system - this run is a rehearsal on Linux
    python      : Python 3.11.2
    compat      : OK - the package needs Python 3.4 or later
    corpus      : /work/qnx-portmap-corpus-local/corpus

    -- corpus integrity --
    corpus: /work/qnx-portmap-corpus-local/corpus
    pages checked: 3426
    page SHA-256: OK
    SHA256SUMS: OK (3427 files)

    -- symbols --
    QX PORTMAP - status of QNX symbols in the 8.0 documentation
    frozen corpus: /work/qnx-portmap-corpus-local/corpus
    pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

      abort                        documented
        page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
        citation (index C Library Reference 8.0) :
          Raise the SIGABRT signal to terminate program execution
        note   : present in 7.1 and in 8.0
    ...

    -- verdict --
    verify-corpus exit code : 0 (0 = every page matches its SHA-256)
    symbols exit code       : 1 (0 = every symbol documented, 1 = at least one absent or unknown, 2 = error)
    compat exit code        : 0 (0 = the interpreter is new enough for the package)
    RESULT      : PASS

What this proves today: the script is POSIX shell, it runs from any
directory, it detects the system and the interpreter, it checks that the
interpreter is new enough for the package, it verifies the corpus page by
page, and it runs the tool and reports its real exit code. What it does
**not** prove: that a QNX 8.0 system answers the same way. The `target` line
is the one that changes on a real target, and the day it says
`QNX system detected`, the segment is filmed.

The complete output of this rehearsal (64 lines) is kept in
`/work/preuves-qnx13/rehearsal-cible-16-11-2026.txt` (working copy); the same
command was also run with `bash` and from another directory, with the same
result.

## 6. Sources

All of them were read on 16/11/2026.

- Target-side utilities of the SDP 8.0.3 (Python 3.13 for QNX OS):
  `https://www.qnx.com/developers/docs/relnotes8.0/com.qnx.doc.release_notes/topic/8.0.3_prod_release_notes/8.0.3_target_side_utilities.html`
- QNX Everywhere (free non-commercial licence, myQNX account, Quick Start
  Target Image for Raspberry Pi):
  `https://qnx.software/en/developers/get-started/qnx-everywhere`
- QNX Everywhere, release of 11 September 2025 (the QSTI and the CTI
  repository for Raspberry Pi 4B are upgraded to the SDP 8.0.3, and PIP is
  installed by default on the QSTI):
  `https://qnx.software/en/blog/2026/qnx-everywhere-september-release`
- Guide of the Quick Start Target Image for Raspberry Pi 4 and 5:
  `https://www.qnx.com/developers/docs/qnxeverywhere/com.qnx.doc.target_images/topic/qsti/intro.html`
- `mkqnximage`, the builder of the QEMU system image:
  `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkqnximage.html`
- The rules of the contest (the segment that is missing, and the acceptance
  of host tools): `https://qnx.devpost.com/rules`, read on 15/11/2026.
- The modules that Python 3.13 removed (PEP 594, "Removal of dead
  batteries"): `https://peps.python.org/pep-0594/`, read on 16/11/2026.
- `vermin`, the tool that measures the minimum Python version of a source
  tree: `https://pypi.org/project/vermin/`, run on 16/11/2026.
