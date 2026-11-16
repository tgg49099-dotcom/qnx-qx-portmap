# QX PORTMAP - YouTube demonstration video plan (QNX Global Hackathon)

Prepared on 15 November 2026. This file is the plan of the video: what is on
screen, the commands, and the English text of the voice-over, minute by
minute. **No video is produced and no screen capture is taken in this cycle**;
this is the script the person who films needs.

Target duration: **2 minutes 40 seconds (160 s)**, which leaves 20 seconds of
margin under the limit of the contest.

## 1. The rules the video must obey, quoted

> "Include a demonstration video of your Project. The video portion of the
> Submission: should be less than three (3) minutes. Judges are not required
> to watch beyond three minutes; should include footage that shows the Project
> functioning on the device for which it was built; must be uploaded to and
> made publicly visible on YouTube and a link to the video must be provided on
> the submission form on the Hackathon Website; and must not include third
> party trademarks, or copyrighted music or other material unless the Entrant
> has permission to use such material."
> - `https://qnx.devpost.com/rules`, section "Submission Requirements", read
> 15/11/2026 (HTTP 200, 161 146 bytes)

What this means for the shooting:

| rule | how the plan answers it |
|---|---|
| less than three (3) minutes | 160 s planned, checked with `ffprobe` on the file before it is uploaded |
| shows the Project functioning | the tool is run on screen, for real, on a Linux workstation - that is the device the tool is built for (it is a host tool) |
| public on YouTube | visibility "Public" at upload; the URL replaces the placeholder of block 4.5 of `KIT-SOUMISSION-QNX.md` |
| no third-party trademarks | the only logo on screen is the one of the project; no QNX logo, no BlackBerry logo, no browser tab of a third-party site |
| no copyrighted music | no music track at all; the voice-over only |
| in English | every line of the voice-over is written in English below; the console speaks English by default, so the video shows the real English console (`--lang fr` shows the French one) |

## 2. How to film

- Screen: 1920x1080, one camera angle (a screen recording of the terminal is
  enough), 25 or 30 fps. No face, no voice of the person filming.
- Terminal: a clean shell, the prompt reduced to `$`, the font large enough to
  be read. **No path of a private machine, no account name, no token, no
  password, no browser tab, no notification.**
- The commands are typed on screen, not pasted silently, so the judge sees
  them. The commands are the ones in the kit, block 4.1.
- No third-party logo and no music, as said above.
- The corpus rebuild is the one long step (it downloads the official QNX
  documentation). The filming either uses the short mode
  (`--max-pages 3`, 27 pages downloaded in 51 seconds on 15/11/2026, measured
  on the machine that filmed this plan) or starts the full rebuild before the
  camera and shows the result. The caption on screen says which one is shown.

## 3. Minute by minute

### 0:00 - 0:12 - Title and the problem

**On screen**: black title card, white text, one line at a time.

```
QX PORTMAP
For every QNX symbol your code calls:
is it still documented in QNX 8.0?
```

**Voice-over (English)**:

> "You have a QNX 8.0 source tree. Some of the symbols it calls have a page
> in the QNX 7.1 C Library Reference, and no page in the 8.0 one. You find
> out when the build fails. QX PORTMAP answers that question before the
> build: for each symbol, is it still documented in QNX 8.0, and where
> exactly."

### 0:12 - 0:30 - Getting the tool

**On screen**: terminal, prompt at the top left, three commands typed one
after the other.

```
$ git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
$ cd qnx-qx-portmap && pip install .
$ bash scripts/bootstrap_corpus.sh --out corpus-downloaded --max-pages 3
```

**Voice-over**:

> "It is a host tool: pure Python 3, standard library only, no dependency, no
> API key, no account. The QNX documentation is not redistributed with the
> repository, so the corpus is rebuilt from the official QNX site with one
> command. Here it is the short mode, three pages per book; without it the
> tool refuses to answer rather than guessing."

### 0:30 - 0:48 - What the corpus is

**On screen**: the last lines of the rebuild, then the tool started without a
corpus.

```
bootstrap_corpus : corpus reconstruit dans corpus-downloaded
$ qnx-portmap abort
corpus introuvable
$ echo $?
2
```

**Voice-over**:

> "Without the corpus the tool says 'corpus not found' and exits with code
> 2. It never invents an answer. The corpus is 3,426 pages of the official
> QNX 7.1 and 8.0 documentation, and every page is checked against its
> SHA-256."

### 0:48 - 1:28 - The demonstration (the core of the video)

**On screen**: the tool running on four symbols, in full, then the same in
JSON.

```
$ QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort accept bzero zzz_fonction_inexistante
QX PORTMAP - status of QNX symbols in the 8.0 documentation
frozen corpus: corpus-downloaded
pages: 3426 (7.1: 1200, 8.0: 2226) - consulted on 2026-11-14 - offline mode

  abort                        documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    citation (index C Library Reference 8.0) :
      Raise the SIGABRT signal to terminate program execution
    note   : present in 7.1 and in 8.0

  accept                       described elsewhere
    page   : https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
    see    : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html
    note   : described in the 8.0 documentation but without a page of its own in the C Library Reference

  bzero                        absent
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
    note   : present in the C Library Reference 7.1, absent from the whole 8.0 corpus

  zzz_fonction_inexistante     unknown
    note   : not found in the frozen 8.0 corpus: unknown symbol, typo, or added after 2026-11-14
```

**Voice-over**:

> "Four symbols, four different answers. 'abort' is documented in QNX 8.0,
> and the tool prints the exact sentence taken from the page, with the URL
> and the SHA-256 of the page. 'accept' has no page of its own in 8.0, but the
> 8.0 documentation still describes it, so the tool gives the page that does.
> 'bzero' was in the 7.1 C Library Reference and is gone from the 8.0
> corpus: the tool says so and keeps the 7.1 page, it does not drop the
> symbol. And a name that does not exist is reported as unknown, not
> guessed. The console is in English by default (`--lang fr` shows the
> French one): documented, described elsewhere, absent, unknown."

### 1:28 - 1:42 - The work list

**On screen**: the end of the same run, the work list.

```
--- Upgrade worklist (2 symbol(s)) ---
P2  bzero                      absent
      https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
P3  accept                     described elsewhere
      https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
```

**Voice-over**:

> "It also produces the work list: the symbols to fix, sorted by priority,
> each one with the page to read."

### 1:42 - 2:02 - Measured on real QNX code

**On screen**: the JSON output, then the README section of the measurement.

```
$ qnx-portmap --format json abort | head -20
{
 "tool": "QX PORTMAP",
 "corpus": { "pages_total": 3426, ... },
 "symbols": [ { "symbol": "abort", "status": "documented", ... } ]
}
```

Then the README, scrolled to the table:

| resolu et cite (page QNX 8.0 + citation + SHA-256) | 96 |
| resolu mais decrit ailleurs | 0 |
| non resolu | 4 |
| taux | 96 % |

**Voice-over**:

> "The tool was measured on the 100 QNX symbols really called by five public
> QNX repositories, at pinned commits. 96 of them are resolved and quoted
> with the URL and the SHA-256 of the cited page. The four that are not
> resolved are honest: they had a page in 7.1 and have none in 8.0. The
> sample, the citations and the SHA-256 of each page are in the repository."

### 2:02 - 2:18 - The tests

**On screen**: the test suite running, then the result.

```
$ QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m unittest discover -s tests -t .
...
Ran 170 tests in 14.590s
OK (skipped=1)
```

**Voice-over**:

> "170 tests, no network access, no dependency. And a test that always
> passes tests nothing, so the repository also contains a red to green proof:
> the script breaks one rule of the code at a time and checks that the
> matching test turns red, then restores the code."

### 2:18 - 2:34 - The honest limit and the call to action

**On screen**: the README section "Honest limits", then the repository page.

```
QX PORTMAP - a documentation map for the QNX 8.0 symbols your code calls
https://github.com/tgg49099-dotcom/qnx-qx-portmap
MIT licence - 170 tests - AI-assisted development
```

**Voice-over**:

> "What it does not do: it does not analyse a binary, it does not run on the
> target, and it does not redistribute the QNX documentation. And here is the
> honest limit: this project has not been run on a QNX 8.0 machine yet,
> because that needs the QNX SDP 8.0 licence. The code is POSIX-compatible
> Python with the standard library only; the next step, once that licence is
> available, is to run it on QNX 8.0 itself. The repository is public, MIT
> licensed, and the development was AI-assisted: every statement about a QNX
> symbol is backed by a quotation of an official page."

### 2:34 - 2:40 - End card

**On screen**: the repository URL and the three links, nothing else.

```
github.com/tgg49099-dotcom/qnx-qx-portmap
```

**Voice-over**: none (10 seconds of silence is fine).

## 4. The one segment that is missing: the run on QNX 8.0

**Name of the segment**: *"QX PORTMAP running on QNX 8.0 itself"* - the same
`qnx-portmap` command executed **inside a QNX 8.0 system**, on the target,
instead of on the Linux workstation.

**Why it is missing**: the QNX SDP 8.0 is not installed in this environment.
The licence is a free non-commercial licence delivered through a myQNX
account, and the account is not accessible from here. Installing the SDP
without the licence is not possible.

**What is needed to produce it**:

| need | detail |
|---|---|
| the QNX SDP 8.0 licence | free non-commercial licence, requested with a myQNX account (`https://qnx.software/en/developers/get-started/qnx-everywhere`); it is a gesture of the repository owner, not a technical step |
| the SDP itself | the QNX SDP 8.0 installation (several GB), installed on the same machine as the video |
| a QNX 8.0 target to run on | the QNX 8.0 x86_64 QEMU image that comes with the SDP, or a physical board |
| a Python 3 on the target | the SDP 8.0.3 ships one: "QNX SDP 8.0 Utilities - Python 3.13 (QNX OS)", package `com.qnx.qnx800.target.utils.python3`; the Quick Start Target Image for Raspberry Pi has PIP installed by default |
| the corpus on the target | the QNX documentation is not redistributed: the corpus is built on the host (`bash scripts/bootstrap_corpus.sh --out corpus`) and copied to the target |
| the video capture | the same terminal capture, with the QNX console prompt instead of the Linux one |
| the expected content of the segment | `qnx-portmap abort accept bzero` executed on the QNX 8.0 console, with the same four answers, plus the `qnx-portmap --verify-corpus` output proving the corpus integrity on the target |

**The exact command to film**, from the root of the repository, on the target:

    sh scripts/qnx8_target_check.sh /path/to/corpus abort accept bzero

One command, one screen: the system and its version, the interpreter, the
integrity of the corpus page by page, the answers of the tool, and the
verdict. The whole procedure, with the sources, is in
[`docs/QNX-8.0-CIBLE.md`](docs/QNX-8.0-CIBLE.md); the script is
[`scripts/qnx8_target_check.sh`](scripts/qnx8_target_check.sh), already
rehearsed on a workstation.

**What the segment would prove**: that the tool really builds and runs on
QNX 8.0, which the rules ask for: "The repository must show that the project
genuinely builds for or runs on QNX 8.0, not merely that QNX 8.0 is named in
the README." (`https://qnx.devpost.com/rules`, section "Submission
Requirements", read 15/11/2026).

**Until that segment exists**, the video says out loud, in the segment
2:18 - 2:34, that the project has not been run on a QNX 8.0 machine yet. It
must not suggest the opposite.

**Fallback if the licence does not arrive before 8 December 2026**: the video
is published without that segment, and the sentence in 2:18 - 2:34 stays. The
tool is a host tool, and the rules accept host tools explicitly: "for
host-based developer tools, output or functionality specifically intended to
build, analyze, test, deploy, debug, or manage software for QNX 8.0"
(`https://qnx.devpost.com/rules`, section "Submission Requirements", read
15/11/2026).

## 5. Before publishing

| check | how |
|---|---|
| duration under 3 minutes | `ffprobe -v error -show_entries format=duration -of default=nw=1 video.mp4` |
| no music, no third-party logo | `ffprobe -v error -show_streams -of default=nw=1 video.mp4` (no audio stream), and every frame looked at once |
| no secret on screen | the whole capture looked at once: no token, no account name, no private path, no browser tab |
| English | the voice-over text of this file is the text to record |
| public on YouTube | the video is uploaded as "Public", and the URL replaces the placeholder of block 4.5 of `KIT-SOUMISSION-QNX.md` |
| the URL is in the kit | `python3 tools/mesure_kit.py --check` still passes after the placeholder is replaced |
| the URL is in the repository | the same URL is added to the README and to the description block 4.1 |

## Update 2026-11-15 - the filmed console now speaks English

The console speaks English by default; `--lang fr` prints the same output in
French, byte for byte (pinned by `tests/test_lang_en.py`). The video MUST
film the English console: the contest rules require English for all
submission material.

### Exact commands to film (QNX 8.0 target, segment "on QNX 8.0")

    python3 -m qnx_portmap --corpus <shared-corpus-dir> --verify-corpus
    python3 -m qnx_portmap --corpus <shared-corpus-dir> abort pthread_create bzero

### Expected English text on screen (first lines, verbatim)

    corpus: <shared-corpus-dir>
    pages checked: 8
    page SHA-256: OK
    SHA256SUMS: OK (N files)

    QX PORTMAP - status of QNX symbols in the 8.0 documentation
    frozen corpus: <shared-corpus-dir>
    pages: 8 (7.1: 2, 8.0: 6) - consulted on 2026-11-14 - offline mode

      abort                        documented
        page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
        citation (index C Library Reference 8.0) :
          Raise the SIGABRT signal to terminate program execution
        note   : new symbol in 8.0 (absent from the 7.1 reference)

    --- Upgrade worklist (0 symbol(s)) ---
    (nothing to migrate: every analyzed symbol is documented in 8.0)

Every English label is pinned by `tests/test_lang_en.py`: a French label
left in the default (English) mode turns the suite red.

## Update 2026-11-16 - the video is filmed (supersedes sections 2 and 3 for timings)

The demonstration video now exists. It was filmed on 16/11/2026 from the
**public repository** (first command: a fresh `git clone`, commit `c43f60c`
shown on screen), in a real terminal: every command is really executed, the
session is recorded with `script -T` and replayed frame by frame; nothing is
retyped. Only the network wait of the first quick-mode run is shortened, and
the screen says so (">> wait shortened").

| fact | value | how it was measured |
|---|---|---|
| duration | **111.04 s** (under the 3-minute limit) | `ffprobe` on the file |
| streams | one H.264 video stream, 1920x1080, 25 fps, **no audio track** (no music) | `ffprobe` |
| quick mode, first run | 76 pages downloaded from qnx.com in 151.2 s, exit code 1 | shown on screen |
| quick mode, second run | cached, 77 pages in 2.5 s, exit code 0 | shown on screen |
| test suite on the fresh clone | 194 tests, OK (skipped=33) | shown on screen |

Scenes: title card; clone and Python version; `--quick abort bzero
zzz_fonction_inexistante` (`abort` documented with its official page, `bzero`
and the typo `unknown`, never `absent`, the worklist names the two unknown
symbols); `--quick accept MsgSend` (`accept` described elsewhere, in the
worklist; `MsgSend` documented); the same answer in JSON; the tests; then
three cards: the measure on real QNX code (96 of 100 symbols), the honest
limits (not yet run on a QNX 8.0 target: that needs the QNX SDP 8.0 licence;
the QNX documentation is not redistributed; AI-assisted development), and the
end card (repository, MIT licence). English captions are burned in.

Reproduce it: `scripts/video/record_demo.sh` (recording, about 2 minutes) then
`scripts/video/render_demo.py` (rendering, under a minute). These two video
scripts need `pyte`, `Pillow` and `ffmpeg`; the tool itself does not.

### YouTube fields (ready to paste; the upload is done by the entrant)

- Title: `QX PORTMAP - is every QNX symbol your code calls still documented in QNX 8.0?`
- Visibility: Public. Made for kids: No.
- Description:

```
QX PORTMAP is a host tool for the QNX Global Hackathon (Developer Tooling & Host Tools).
For each QNX symbol your C code calls, it tells you whether it is still documented in
QNX 8.0, and quotes the official QNX page that says so. Python 3, standard library only.

Shown in this video (real terminal, nothing retyped; only the network wait is shortened):
- a fresh clone of the public repository;
- quick mode: 76 official pages (A-Z indexes of the 7.1 and 8.0 C Library Reference and
  the 8.0 migration guide) downloaded at one request per second; it never guesses "absent";
- the upgrade worklist, the JSON output, and the test suite (194 tests).

Not shown: the tool running on a QNX 8.0 target (that needs the QNX SDP 8.0 licence).
The QNX documentation is not redistributed. Developed with AI assistance.

Code (MIT licence): https://github.com/tgg49099-dotcom/qnx-qx-portmap
The video file itself, downloadable: https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/qx-portmap-demo-final.mp4
Thumbnail: https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/qx-portmap-demo-thumbnail.png
```

The URL that YouTube gives replaces `<YOUTUBE_URL_TO_BE_FILLED_AFTER_THE_VIDEO_IS_UPLOADED>`
in `KIT-SOUMISSION-QNX.md`.
