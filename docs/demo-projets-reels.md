# Demo on a real project: plibsys

Date of the measurement: **14/11/2026**. Everything below is reproducible
offline with the frozen corpus of the repository.

## 1. The project studied

| Element | Value |
|---|---|
| Repository | <https://github.com/saprykin/plibsys> |
| Commit | `5a3b06b5e43bced95c2bdfc316d78061ecf833af` (2026-07-17) |
| Licence | MIT (`COPYING` of the project) |
| Local clone | `/tmp/demo_plibsys` (git clone, 14/11/2026) |
| Files read | 101 `.c` + 50 `.h` |

plibsys is a portable C library (threads, mutexes, semaphores, sockets, shared
memory): it is the kind of code one wants to port to QNX 8.0.

## 2. Extraction of the symbols (exact command)

```sh
cd /tmp/demo_plibsys
find . \( -name '*.c' -o -name '*.h' \) | sort | xargs grep -hoE '\b[a-z_][A-Za-z0-9_]*[ ]*\(' \
 | sed 's/[ ]*($//; s/(//' | tr -d ' ' | sort -u \
 | grep -vE '^(_*[A-Z0-9_]+)$' \
 | grep -vE '^(if|for|while|switch|case|default|return|sizeof|defined|do|else|break|continue|goto)$' \
 > /tmp/plibsys_symbols_v2.txt
wc -l /tmp/plibsys_symbols_v2.txt
# 876 /tmp/plibsys_symbols_v2.txt
```

These are the names called or defined in the project, plus the English words
that appear followed by `(` in the comments (`address (`, `argument (`). This
is **on purpose**: it is exactly the kind of noise the tool must be able to
filter out (see section 5).

## 3. QX PORTMAP analysis (exact command and real output)

```sh
cd /work/qnx-portmap
python3 -m qnx_portmap --corpus corpus --file /tmp/plibsys_symbols_v2.txt --format json
```

Exit code: **1** (at least one symbol absent or unknown), in 10 s, without
network.

| Status | Number | What it means here |
|---|---|---|
| `documented` | **122** | official page in the 8.0 C Library Reference (`pthread_create`, `malloc`, `sem_wait`, `mmap`, ...) |
| `described_elsewhere` | **20** | no page of its own in 8.0, but described elsewhere (see section 4) |
| `absent` | **0** | no symbol of the project was in the 7.1 C Library Reference and no longer exists in 8.0 |
| `unknown` | **734** | not found in the frozen corpus: about 324 carry an internal prefix of the project (`p_*`, `psys*`, `puthread*`...), the other 410 are compiler builtins, Windows APIs or English words |

Real extract of the text output (command
`python3 -m qnx_portmap --corpus corpus --file subset.txt`):

```
  socket                       decrit ailleurs
    page   : https://man.freebsd.org/cgi/man.cgi?query=socket&manpath=FreeBSD+14.4-RELEASE+and+Ports
    voir   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html
    citation (index C Library Reference 8.0, section "described elsewhere") :
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=socket&manpath=FreeBSD+14.4-RELEASE+and+Ports ) and
      Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
    * cite par le guide de migration officiel 8.0 : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/bsp_support.html
    note   : decrit dans la documentation 8.0 mais sans page propre dans la C Library Reference

  pthread_create               documente
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_create.html
    citation (index C Library Reference 8.0) :
      Create a thread
    detail :
      The pthread_create() function creates a new thread, with the attributes specified in the
      thread attribute object attr . The created thread inherits the signal mask of the parent
      thread, and its set of pending signals is empty.
    note   : present en 7.1 et en 8.0

  p_atomic_int_add             inconnu du corpus
    note   : introuvable dans le corpus 8.0 fige : symbole inconnu, erreur de saisie, ou ajout posterieur au 2026-11-14
```

English translation of the block above (the block above is the verbatim output
of the tool, in French):

```
  socket                       described elsewhere
    page   : https://man.freebsd.org/cgi/man.cgi?query=socket&manpath=FreeBSD+14.4-RELEASE+and+Ports
    see    : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html
    citation (C Library Reference 8.0 index, section "described elsewhere") :
      FreeBSD documentation (
      https://man.freebsd.org/cgi/man.cgi?query=socket&manpath=FreeBSD+14.4-RELEASE+and+Ports ) and
      Networking APIs in the High-Performance Networking Stack (io-sock) User's Guide .
    * cited by the official 8.0 migration guide: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/bsp_support.html
    note   : described in the 8.0 documentation but without a page of its own in the C Library Reference

  pthread_create               documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_create.html
    citation (C Library Reference 8.0 index) :
      Create a thread
    detail :
      The pthread_create() function creates a new thread, with the attributes specified in the
      thread attribute object attr . The created thread inherits the signal mask of the parent
      thread, and its set of pending signals is empty.
    note   : present in 7.1 and in 8.0

  p_atomic_int_add             unknown to the corpus
    note   : not found in the frozen 8.0 corpus: unknown symbol, typo, or addition published after 2026-11-14
```

## 4. The useful result: the 19 socket APIs returned by QNX 8.0

The 20 `described_elsewhere` symbols are **almost all the BSD socket calls**.
The 8.0 C Library Reference gives them no page of their own: it explicitly
points them to the FreeBSD manual **and** to the io-sock guide:

`accept`, `bind`, `connect`, `freeaddrinfo`, `getaddrinfo`, `getpeername`,
`getsockname`, `getsockopt`, `inet_ntop`, `inet_pton`, `listen`, `recv`,
`recvfrom`, `send`, `sendto`, `setsockopt`, `shutdown`, `socket`, `sysctl`.

For someone porting a project, this is the most useful signal of the lot:
**on QNX 8.0, the socket layer is no longer in the C Library Reference, it is
in `io_sock` and the contract is the FreeBSD one.** Each line of the
cross-reference also quotes the official 8.0 migration guide.

The 20th symbol is `__attribute__`, found in a code example of the page
`_register_ioctl_handler.html`: it is a mention in the documentation, not a
QNX API. The tool reports it as such (mention, not documentation).

## 5. Measurement of the "API name" rule on this project

Same list of 876 symbols, rule disabled in a **copy** of the code
(`/tmp/portmap_sans_regle`, the repository is not touched):

| | `documented` | `described_elsewhere` | `unknown` |
|---|---|---|---|
| with the rule (shipped) | 122 | **20** | 734 |
| without the rule (measurement) | 122 | **117** | 637 |

The **97** added symbols are English words or parameter names found in the
prose of the documentation:

`address`, `any`, `architectures`, `argument`, `barrier`, `binary`, `bit`,
`blocking`, `brackets`, `bytes`, `capabilities`, `character`, `characters`,
`collisions`, `compiler`, `cores`, `create`, `current`, `deadlock`,
`descriptor`, ... (the 97 are in the JSON output of the "without the rule"
run).

Announcing these words as "described elsewhere in the 8.0 documentation" would
be wrong: the rule "the symbol must look like an API name" (present in a QNX
index, or written with an upper-case letter or an underscore) filters them
out.

## 6. What this demo does NOT prove

- **It does not prove that plibsys compiles on QNX 8.0.** The tool reads the
  documentation; it compiles nothing, it tests nothing on a target, it has no
  SDP. A `documented` symbol means "the 8.0 C Library Reference has a page
  for that name", not "this code will work".
- **It does not measure the compatibility of the structures, the socket
  options or the error values.** Those details are in the cited pages, which
  the tool points to but does not summarize.
- **`unknown` does not mean "absent from QNX".** 410 standard symbols or
  project builtins (`__atomic_fetch_add`, `_beginthreadex`, ...) are not in
  the C Library Reference index: they may be in another book of the
  documentation, or supported by the compiler and not documented. The tool
  does not guess.
- **The corpus is a snapshot of 14/11/2026.** A page published the next day
  changes nothing in the result.
- **The extraction of the symbols is a prototype.** A real port would use a C
  preprocessor (`gcc -E`) or a parser; the command of section 2 also takes
  the words of the comments, which feeds the noise measured in section 5.

## 7. A second real project: a QNX input driver (26/11/2026)

This is the case shown on the first screen of the README.

| Element | Value |
|---|---|
| Repository | <https://github.com/varghes/Raspberry-QNX> (also one of the five repositories of the J5 measurement) |
| Commit | `043582a94ac94e8311ff7c845beb450a9a718f04` |
| Directory read | `Bsp_Rasp/src/hardware/devi` (input driver): 28 `.c` and 18 `.h` files |
| QX PORTMAP | commit `594dcf1`, quick mode, Linux, Python 3.13 |

Exact commands, from a fresh clone of this repository:

```bash
git clone https://github.com/varghes/Raspberry-QNX ../Raspberry-QNX && git -C ../Raspberry-QNX checkout 043582a
python3 -m qnx_portmap --quick --scan-dir ../Raspberry-QNX/Bsp_Rasp/src/hardware/devi --worklist
```

Real output (start of the standard output; the second line prints the local
path of the clone and is shown here as `<clone>`; the other entries of the
work list, all `described elsewhere`, are elided):

```text
QX PORTMAP - status of QNX symbols in the 8.0 documentation
quick-mode small corpus: <clone>/corpus-quick
pages: 242 (7.1: 26, 8.0: 216) - downloaded on 2026-11-26 - quick mode (A-Z indexes and migration guide only; "absent" only when the guide announces the removal)

--- Upgrade worklist (8 symbol(s)) ---
P1  InterruptAttach            absent
      https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/kernel.html
      The following functions have been removed: InterruptAttach() InterruptAttachArray()
      InterruptHookIdle2() InterruptHookTrace()
      cited by the migration guide: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/kernel.html
      called at: lib/ps2api.c:131, lib/ps2api.c:158, lib/ser8250.c:506
...
```

Last line of the standard error: `qnx-portmap: small corpus ready: 242 pages in 303.3 s`.
Exit code: **1** (at least one symbol needs work).

The three call lines were checked in the clone: lines 131 and 158 of
`lib/ps2api.c` and line 506 of `lib/ser8250.c` each call `InterruptAttach`.
The same official page says that "Interrupt Service Routines (ISRs) are no
longer supported" and that "the new InterruptAttachThread() function allows
you to attach a thread to an interrupt source": that is where the port starts.

What this case does **not** prove: the quick mode reads the A-Z indexes and the
migration guide only, so its `unknown` entries are decided by the full corpus,
and nothing here compiles or runs the driver on QNX 8.0.
