# QX PORTMAP - Devpost submission kit (QNX Global Hackathon)

Prepared on 15 November 2026. Every block below is the text to paste into the
Devpost submission form, in the order of the form. All the text to paste is in
English, because the contest rules require English submission materials:

> "All Submission materials must be in English or, if not in English, the
> Entrant must provide an English translation of the demonstration video, text
> description, and testing instructions as well as all other materials
> submitted."
> - `https://qnx.devpost.com/rules`, section "Language Requirements", read
> 15/11/2026 (HTTP 200, 161 146 bytes)

The order of the blocks follows the official Devpost description of the form
steps ("Know Your Submission Steps", `https://devpost.helpscoutdocs.com/article/126-know-your-submission-steps`,
page says "Last updated on August 12, 2026", read 15/11/2026) and the contest
page "What to Submit" section (`https://qnx.devpost.com/`, read 15/11/2026).

**How the lengths are measured**: the length of a block is the number of
characters of the text between the ``` fences, as pasted, without the final
newline. `python3 tools/mesure_kit.py --check` recomputes every length in this
file and fails if one of them is wrong.

---

## 1. Field limits: what was actually read, and what was not

### 1.1 Limits read in an official Devpost document

| Form field | Limit | Exact source | Date read |
|---|---|---|---|
| Submission name | no limit published | Devpost help, article 145, list of standard questions: "Submission name*" (no number) | 15/11/2026 |
| Submission tagline | **140 characters** | Devpost help, article 145: "Submission tagline (140 characters)*" (page says "Last updated on November 12, 2026") | 15/11/2026 |
| Thumbnail image for the Project Gallery | JPG, PNG or GIF, **5 MB** max file size, 3:2 ratio for best results | Devpost help, article 126: "Thumbnail image for the Project Gallery | This should be a JPG, PNG or GIF format, 5 MB max file size. For best results, use a 3:2 ratio." | 15/11/2026 |
| Project story (Text Description) | **no character limit published** | Devpost help, article 145 lists "Text Description*" with no number; article 126: "Project story* | A text description is required in some format." | 15/11/2026 |
| Built with tags | **25 maximum** | Devpost help, article 126: "Built with tags* | Tag the sponsor's tool and any other technology you included. (25 maximum)" | 15/11/2026 |
| Try it Out links | no limit published | Devpost help, article 126: "Try it Out links | This MAY be required." (no number) | 15/11/2026 |
| Image Gallery | no limit published | Devpost help, article 126: "Image Gallery | Add any relevant screenshots, logos, charts, or images that support your project." | 15/11/2026 |
| Video demo link | no character limit published; the **video** must be under three (3) minutes and public on YouTube | `https://qnx.devpost.com/rules`, section "Submission Requirements", read 15/11/2026 | 15/11/2026 |
| Step 4 fields (submitter type, country, category, repository URL, ...) | no character limit published | Devpost help, article 126, section "Step 4: Additional Details" | 15/11/2026 |
| File upload (if any) | 35 MB max, zip, pdf, word or apk | Devpost help, article 126, section "Step 4: Additional Details" | 15/11/2026 |

The three Devpost help articles behind that table, read on 15/11/2026, each in
HTTP 200, with the update date displayed on the page:

| article | URL | update date displayed |
|---|---|---|
| 145 | `https://help.devpost.com/article/145-how-do-i-set-up-the-submission-period` | November 12, 2026 |
| 126 | `https://help.devpost.com/article/126-know-your-submission-steps` | August 12, 2026 |
| 122 | `https://help.devpost.com/article/122-how-to-enter-a-submission` | May 27, 2026 |

(The older `devpost.helpscoutdocs.com/article/<n>-...` addresses redirect to
these ones, HTTP 301.)

### 1.2 The QNX form itself could not be read: measured, not guessed

The QNX submission form is behind a Devpost session. Measured on **15/11/2026
at 02:05 UTC**, with a browser User-Agent:

```
GET https://qnx.devpost.com/submissions/new
  -> HTTP 302
  -> Location: https://secure.devpost.com/users/register?return_to=https%3A%2F%2Fqnx.devpost.com%2Fsubmissions%2Fnew

GET https://qnx.devpost.com/submissions/new.json
  -> HTTP 401
  -> body: {"error":"Please sign up or log in to continue."}
```

**Consequence**: the constraint that the form prints for a given field cannot
be read from outside a session. No limit is declared here for those fields.
This is not a claim that the field has no limit: it is a statement that the
limit was not read. The commands and the raw headers are kept in
`docs/preuves/k-formulaire-devpost-302-401.txt`.

### 1.3 Lower bound by observation, on the same platform

To bound what the platform accepts, 120 **public** Devpost project pages were
measured on 15/11/2026 (sampled from five public hackathon galleries; the
scripts are in the repository, `tools/mesure_champs_devpost.py` and
`tools/table_mesure_devpost.py`; the per-page table is in
`docs/preuves/j-mesure-champs-devpost.txt`):

| Published element | Observed range (120 pages) | Median |
|---|---|---|
| project description (text of the project details column) | 637 to 48 663 characters | 3 659 |
| project name | 3 to 45 characters | 9 |
| number of "Built with" tags | 1 to 14 | 4 |
| "try it out" URL | 17 to 168 characters | 42 |

No page showed a description truncated at 1 200 characters. The description
measurement includes a few dozen characters of page furniture, so it is an
upper estimate of the submitted text. **The QNX contest has no public project
yet**: its gallery `https://qnx.devpost.com/project-gallery` (read 15/11/2026,
HTTP 200) says "The hackathon managers haven't published this gallery yet, but
hang tight!", so the observation is made on the platform, not on this contest.

---

## 2. Step 1 - Manage your team

No questions in this step (Devpost help, article 126). The entry is made by a
single person: see block 4.1.

---

## 3. Step 2 - Project Overview

### 3.1 Project name

<!-- BLOC:2_1 -->

```text
QX PORTMAP
```

- Length (measured): 10 characters
- Field limit: no limit published (Devpost help, article 145, read 15/11/2026)

### 3.2 Project tagline

<!-- BLOC:2_2 -->

```text
QX PORTMAP tells you, for every QNX symbol your code calls, whether QNX 8.0 still documents it - with the page, the quote and the SHA-256.
```

- Length (measured): 138 characters
- Field limit: **140 characters** (Devpost help, article 145: "Submission tagline (140 characters)*", page dated "Last updated on November 12, 2026", read 15/11/2026)

### 3.3 Thumbnail image for the Project Gallery

Not a text field. Format JPG, PNG or GIF, 5 MB max, 3:2 ratio (Devpost help,
article 126, read 15/11/2026). **Status: no thumbnail is committed to the
repository yet.** A 3:2 image of the terminal output of
`qnx-portmap abort accept bzero` is the intended one; the file has to be
produced and uploaded before the submission is sent.

---

## 4. Step 3 - Project Details

### 4.1 Project story (Text Description)

<!-- BLOC:3_1 -->

```markdown
QX PORTMAP - a documentation map for the QNX 8.0 symbols your code calls
## How this differs from our other entry

The rules of this hackathon allow one entrant to submit several projects, but
"each Submission must be unique and substantially different from each of the
Entrant's other Submissions". This project is not a variant of our other entry,
QX-PROBE. QX-PROBE is a source checker: it reads the C source of a QNX 8.0
resource manager and reports the access gates and dispatch tables that the QNX 8.0
documentation requires (11 rules, in the QX-PROBE repository). QX PORTMAP is a
documentation mapper: it reads the list of QNX symbols that a C or SDK source tree
calls and answers, for each one, whether it is still documented in QNX 8.0, with
the official page and the exact quotation. The first one audits resource-manager
code, the second one guides the port of existing code to QNX 8.0; they read
different inputs, produce different outputs, share no code, no rule and no
document, and each one is a complete submission on its own.

## The problem

QNX 8.0 changed its C library. A symbol your code still calls can have a page
in the QNX 7.1 C Library Reference and no page in the 8.0 one. You find out
when the build fails, on a target you cannot reach, the day before the
release.

## What the tool does

QX PORTMAP takes a list of QNX symbols (functions, variables, constants) and
answers, for each one, with the state of its documentation in QNX 8.0:

| status | meaning |
|---|---|
| `documented` | it has its own page in the QNX 8.0 C Library Reference |
| `described_elsewhere` | no page of its own in 8.0, but the 8.0 documentation still describes it |
| `absent` | it was in the C Library Reference 7.1 and is gone from the 8.0 corpus; the tool still shows its 7.1 page |
| `unknown` | not in the frozen corpus: a typo, a macro of your project, or a symbol published after 14 November 2026. The tool never guesses. |

For every symbol it resolves, QX PORTMAP prints the official page, the exact
quotation taken from that page, and the SHA-256 of the page, so a reviewer can
check the answer without trusting the tool. It then prints a work list of the
symbols to fix, sorted by priority.

## What it does not do

- It does not analyse a binary and it does not run on the target: it analyses
  the documentation.
- It does not redistribute the QNX documentation. The corpus (about 3,400 pages,
  QNX 7.1 and 8.0) is rebuilt on demand from the official QNX site with one
  command and one download log. **The first download takes about 1 h 40 to 2 h**
  at one request per second (1.7 to 2 s per page, measured on 15 and 16 November
  2026); after that the tool works offline. A **quick mode** (`--quick`,
  about two to three minutes, 76 pages) gives a first answer without that
  download.
- It makes no network request by default; the online refresh is an opt-in
  flag.
- It does not check licences, CVEs, or symbols published after the corpus
  snapshot.

## QNX version, target, toolchain

| | |
|---|---|
| QNX version | QNX SDP 8.0. Every answer is backed by a page of the official BlackBerry QNX SDP 8.0 documentation (C Library Reference, io-sock User's Guide, SDP migration guide). Each quotation carries the URL, the consultation date and the SHA-256 of the page it comes from. |
| Target | A host tool (Linux, macOS, Windows). It needs no QNX SDP, no QNX board and no QNX account. It needs no network connection **to run** once the corpus has been downloaded: the corpus is a local snapshot, and downloading it for the first time is the only step that needs the network (see "Run it in three commands"). It is pure Python 3 and uses the standard library only, so it is POSIX-compatible and designed to run on QNX 8.0 as well. **This has not been demonstrated yet**: the project has not been run on a QNX 8.0 machine, because the QNX SDP 8.0 licence is not available in this environment (see "Honest limits" below). |
| Toolchain | Python 3.8+, standard library only (`argparse`, `gzip`, `hashlib`, `json`, `re`, `urllib`). No compilation step, no third-party dependency, no API key. |

## Run it in three commands

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap && pip install .   # optional: the tool needs only the standard library
python3 -m qnx_portmap --quick abort accept bzero zzz_fonction_inexistante
```

The second command is optional and can fail on a locked-down Python. Measured
on 16 November 2026: a system Python protected by PEP 668 refuses the install,
and inside a virtual environment with `PIP_USER` set, pip refuses a `--user`
install. The tool is pure standard library, so the third command works with or
without the install: `python3 -m qnx_portmap` is the same program as the
`qnx-portmap` command the install gives, and it needs nothing else.

The third command is the **quick mode**: a first answer in about two to three
minutes (76 pages downloaded in 127 s in the build environment, and in 144 s
in an independent replay from a clean virtual environment, both measured on
16 November 2026, one request per second). It reads only the A-Z indexes of
the QNX 8.0 and 7.1 C Library Reference, the official migration guide to 8.0
and the own page of each documented symbol. It answers `documented` and
`described elsewhere` like the full mode, but it **never says `absent`**: a
symbol that only the full corpus can decide is reported `unknown`, with a note
that says why.
The exit code of that run is **1**, and that is the expected code: `0` when
every analysed symbol is documented in 8.0, `1` when at least one symbol is
absent or unknown, `2` on error. The quick mode answers `unknown` for the two
symbols it cannot decide, so `1` is the right code here.
Real output of that run (one line per symbol):

```text
  abort                        documented
    note   : present in 7.1 and in 8.0
  accept                       described elsewhere
    note   : described in the 8.0 documentation but without a page of its own in the C Library Reference
  bzero                        unknown
    note   : quick mode: in the 7.1 C Library Reference index, not in the 8.0 index; the other 8.0 books were not read, so absent or described elsewhere is decided by the full corpus (scripts/bootstrap_corpus.sh)
  zzz_fonction_inexistante     unknown
    note   : quick mode: in neither the 8.0 nor the 7.1 index; the other 8.0 books were not read (full corpus: scripts/bootstrap_corpus.sh)
```

For the full answer (quotations, SHA-256, and `absent`), download the
complete corpus once: **about 3,400 pages** of the official QNX
documentation, one request per second. **Budget about 1 h 40 to 2 h**
(1.7 to 2 s per page, measured on 15 and 16 November 2026). The tool then
runs offline:

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded qnx-portmap abort accept bzero
```

Real output, executed on 15 November 2026 against the 3,426-page corpus (the
corpus is a snapshot of the official documentation taken on 14 November 2026;
offline mode, the citation blocks are elided here, the complete session is in
the repository README):

```text
  abort                        documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    citation (index C Library Reference 8.0) :
      Raise the SIGABRT signal to terminate program execution
  accept                       described elsewhere
    page   : https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
    see    : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html
  bzero                        absent
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html
```

The console labels used above, and their French translation (`--lang fr`):

| console label (English, default) | French (`--lang fr`) |
|---|---|
| `documented` | `documente` (documented in QNX 8.0) |
| `described elsewhere` | `decrit ailleurs` (described elsewhere in the QNX 8.0 documentation) |
| `absent` | `absent de la 8.0` (present in QNX 7.1, absent from the QNX 8.0 corpus) |
| `unknown` | `inconnu du corpus` (not found in the frozen corpus) |

The console messages of this version are in English by default; `--lang fr`
prints the same messages in French (see the README), and the JSON output
(`--format json`) uses English field names. Without a corpus the tool prints
`corpus not found` and exits with code 2: it never invents an answer.

## Measured on real QNX code

The 100 QNX symbols really called by five public QNX repositories (pinned
commits) are classified by the tool: **96 of them are resolved and quoted**
(96 %), 4 are not, and the 4 are honest: they had a page in the 7.1 C Library
Reference and have none in the 8.0 corpus, so the tool reports them as
`absent` with their 7.1 page rather than dropping them. The list of the 100
symbols, the citation of each one and the SHA-256 of the cited page are in
`docs/mesure-J5.md` and `docs/mesure-J5/`. The figure was reproduced on
15 November 2026 with `tools/mesure_j5.py`.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

200 tests, no third-party dependency, no network access. Measured on
17 November 2026 in the three possible configurations: with the corpus in
`corpus/` next to the package, 200 tests and 0 skipped; with the corpus
pointed to by the environment variable `QX_PORTMAP_CORPUS`, 200 tests and 1
skipped; without any corpus, 200 tests and 33 skipped (the skipped ones are
the ones that need the corpus). The suite also contains
a RED -> GREEN proof: `tools/contre_epreuve.py` breaks one rule of the code
at a time and checks that the matching test turns red, then restores the
repository. The 11 rules and their output are in `docs/contre-epreuve-rouge.txt`.

## Honest limits

- The tool itself is a host tool: it needs no QNX 8.0 target to run, and it
  does not run on the target.
- The project has **not** been compiled or executed on a QNX 8.0 target yet:
  that requires the QNX SDP 8.0 licence, which is not available in this
  environment. The code is Python 3 standard library only and POSIX-compatible,
  but this has not been demonstrated on a QNX 8.0 machine.
- The 96 % figure is a measurement on one sample of 100 symbols; it is not a
  guarantee for another project.
- The corpus is a snapshot of the official QNX documentation taken on
  14 November 2026. A symbol published since then is reported as `unknown`
  until the corpus is rebuilt.
- The console messages are in English by default; `--lang fr` prints the same
  messages in French (the labels used above are translated in the table).

## Repository, licence, codelab

- Public repository: https://github.com/tgg49099-dotcom/qnx-qx-portmap (MIT
  licence, file `LICENSE` at the top of the repository page).
- The QNX documentation is not redistributed with the repository; see
  `LICENCE-DOCS-QNX.md` and `CORPUS-NON-PUBLIE.txt`.
- Codelab draft for community.qnx.com: `docs/CODELAB-COMMUNITY-QNX.md` in the
  repository.

## AI-assisted development

This project was written with the help of an AI coding assistant. The
assistant wrote the code, the tests and the documentation. Nothing about QNX
is taken on trust: every statement about a QNX symbol is backed by an exact
quotation of an official page (URL, date, SHA-256), and the behaviour of the
tool is checked by the test suite and by the RED -> GREEN proof described
above.
```

- Length (measured): 11554 characters
- Field limit: **no character limit published** (Devpost help, articles 145
  and 126, read 15/11/2026). Observation on the same platform: 120 public
  project pages measured on 15/11/2026, published descriptions from 637 to
  48 663 characters, median 3 659; no truncation observed at any lower bound.

### 4.2 Built with tags

<!-- BLOC:3_2 -->

```text
python
qnx
qnx-8.0
qnx-sdp
developer-tooling
documentation
static-analysis
porting
migration
offline
cli
```

- Length (measured): 104 characters, 11 tags
- Field limit: **25 maximum** (Devpost help, article 126: "Built with tags* |
  Tag the sponsor's tool and any other technology you included. (25 maximum)",
  read 15/11/2026). Observation on the same platform: 1 to 14 tags on the 120
  public project pages measured on 15/11/2026.

### 4.3 Try it Out links

<!-- BLOC:3_3 -->

```text
https://github.com/tgg49099-dotcom/qnx-qx-portmap
```

- Length (measured): 49 characters
- Field limit: no limit published (Devpost help, article 126: "Try it Out links
  | This MAY be required.", read 15/11/2026). Observation on the same
  platform: 17 to 168 characters on the 120 public project pages measured on
  15/11/2026.
- There is no hosted instance: the tool is installed and run by the judge, in
  the three commands given in block 4.1. The rules ask for "a URL to your
  public code repository for judging and testing on either GitHub, GitLab, or
  Bitbucket" (`https://qnx.devpost.com/rules`, section "Submission
  Requirements", read 15/11/2026); that is the URL above.

### 4.4 Image Gallery

Not a text field, no limit published (Devpost help, article 126, read
15/11/2026). **Status: no screenshot is committed to the repository yet.**
The three screenshots to produce, with the exact command that fills each one:

| screenshot | command | what it shows |
|---|---|---|
| 1 | `qnx-portmap abort accept bzero` | the four statuses, with the official page and the quotation |
| 2 | `qnx-portmap --format json abort` | the same answer in JSON, with English field names |
| 3 | `python3 -m unittest discover -s tests -t .` | the test suite result |

### 4.5 Video demo link

<!-- BLOC:3_5 -->

```text
<YOUTUBE_URL_TO_BE_FILLED_AFTER_THE_VIDEO_IS_UPLOADED>
```

- Length (measured): 54 characters
- Field limit: no character limit published. The **video** must be under three
  (3) minutes and public on YouTube: "Include a demonstration video of your
  Project. The video portion of the Submission: should be less than three (3)
  minutes. Judges are not required to watch beyond three minutes; should
  include footage that shows the Project functioning on the device for which
  it was built; must be uploaded to and made publicly visible on YouTube and a
  link to the video must be provided on the submission form on the Hackathon
  Website; and must not include third party trademarks, or copyrighted music
  or other material unless the Entrant has permission to use such material."
  (`https://qnx.devpost.com/rules`, section "Submission Requirements", read
  15/11/2026).
- The placeholder is deliberate: no video is published yet, so no URL is
  claimed. The plan of the video is in `VIDEO-YOUTUBE-QNX-PORTMAP.md` in the
  repository.

---

## 5. Step 4 - Additional Details

The exact set of questions in this step is specific to the contest and can
only be seen in the form (section 1.2). The questions named by the contest
page "What to Submit" section and by the rules are prepared below.

### 5.1 Submitter Type

<!-- BLOC:4_1 -->

```text
Individual
```

- Length (measured): 10 characters
- Field limit: no limit published. The question is listed as "Submitter Type:
  Individual, Team, or Organization*" in the Devpost help, article 126, read
  15/11/2026.

### 5.2 Countries of Residence

<!-- BLOC:4_2 -->

```text
Switzerland
```

- Length (measured): 11 characters
- Field limit: no limit published. The question is listed as "Countries of
  Residence*" in the Devpost help, article 126, read 15/11/2026. Switzerland is
  not an excluded country: the QNX rules exclude "Brazil, Russia, Crimea,
  Cuba, Iran, North Korea" and the countries sanctioned by OFAC, and
  Switzerland is not among them (`https://qnx.devpost.com/rules`, section
  "Eligibility", read 15/11/2026).

### 5.3 Category

<!-- BLOC:4_3 -->

```text
Developer Tooling & Host Tools
```

- Length (measured): 30 characters
- Field limit: no limit published. The rules ask for exactly one category:
  "Select the one (1) category you are submitting to." (`https://qnx.devpost.com/rules`,
  section "Submission Requirements", read 15/11/2026). The name of the
  category is taken from the contest page: "Developer Tooling & Host Tools .
  Tools that make building for QNX easier, on the host or the target."
  (`https://qnx.devpost.com/`, read 15/11/2026).

### 5.4 URL to your code repository

<!-- BLOC:4_4 -->

```text
https://github.com/tgg49099-dotcom/qnx-qx-portmap
```

- Length (measured): 49 characters
- Field limit: no limit published (Devpost help, article 145 lists the
  standard question "[URL field] Please provide a URL to your code repository.",
  read 15/11/2026). Observation on the same platform: 17 to 168 characters for
  a "try it out" URL on the 120 public project pages measured on 15/11/2026.
- The repository is public and was checked from outside the build environment
  on 15/11/2026 (HTTP 200 on the repository page and on the raw README).

### 5.5 MIT License

<!-- BLOC:4_5 -->

```text
Yes - the repository contains an MIT licence file (LICENSE) at the top of the repository page.
```

- Length (measured): 94 characters
- Field limit: no limit published. The question is listed as "MIT License*" in
  the Devpost help, article 126, read 15/11/2026. The rules require an open
  source licence file: "The repository must be public and open source by
  including an open source license file. This license should be detectable and
  visible at the top of the repository page (in the About section)."
  (`https://qnx.devpost.com/rules`, section "Submission Requirements", read
  15/11/2026).

### 5.6 Publicly available

<!-- BLOC:4_6 -->

```text
Yes - the repository is public and can be cloned without an account.
```

- Length (measured): 68 characters
- Field limit: no limit published. The question is listed as "Publicly
  available*" in the Devpost help, article 126, read 15/11/2026.

### 5.7 Evidence of QNX use

<!-- BLOC:4_7 -->

```text
QX PORTMAP is a host tool whose output exists to analyse software written for
QNX 8.0: it tells a QNX 8.0 developer whether each symbol their code calls is
still documented in the official QNX SDP 8.0 documentation, and where.

The relevant files, in the public repository
https://github.com/tgg49099-dotcom/qnx-qx-portmap :

- `qnx_portmap/extract.py` parses the index page of the QNX 8.0 C Library
  Reference (`parse_index_page`) and the topic pages (`parse_topic_page`), and
  extracts the "Description" section of a symbol page.
- `qnx_portmap/classify.py` (`Classifier`) decides the four states of a symbol
  in QNX 8.0: documented, described elsewhere, absent, unknown. The
  "described elsewhere" case is what links a symbol to the page of the QNX 8.0
  io-sock User's Guide or of the QNX SDP 8.0 migration guide that describes
  it.
- `qnx_portmap/corpus.py` reads the frozen corpus (`corpus/index/pages.jsonl`)
  and verifies the SHA-256 of every page against `corpus/SHA256SUMS`, so the
  quotation comes from the page it names.
- `qnx_portmap/cli.py` and `qnx_portmap/report.py` produce the output.

The output to look at: for each symbol, the official QNX 8.0 page, the exact
quotation taken from that page, and the SHA-256 of the page. Example, executed
on 15 November 2026:

  abort    documented
    page   : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/abort.html
    citation (index C Library Reference 8.0) :
      Raise the SIGABRT signal to terminate program execution

  accept   described elsewhere
    page   : https://man.freebsd.org/cgi/man.cgi?query=accept&manpath=FreeBSD+14.4-RELEASE+and+Ports
    see    : https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html

  bzero    absent
    page   : https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/b/bzero.html

The same three symbols are shown in French with `--lang fr` in the
description block, and the table of the console labels is in the repository
README.

The measurement on real QNX code is in `docs/mesure-J5.md`: 100 QNX symbols
really called by five public QNX repositories, pinned commits, classified by
the tool, 96 resolved and quoted with the URL and the SHA-256 of the cited
page. The cited pages are in `docs/mesure-J5/citations-*.txt`.

What is not claimed: the project has not been compiled or executed on a QNX
8.0 target, because the QNX SDP 8.0 licence is not available in this
environment. The tool itself needs no QNX target to run, it is pure Python 3
with the standard library only, and its output is specifically intended to
analyse and manage software for QNX 8.0.
```

- Length (measured): 2661 characters
- Field limit: no limit published for this field. The requirement comes from
  the rules: "Evidence of QNX use : Your submission must explain how the
  project uses or supports QNX. Evidence may include QNX-specific source code
  or APIs; QNX libraries, headers, buildfiles, toolchains, system images, or
  configuration files in the repository; a demonstration running on QNX 8.0;
  or, for host-based developer tools, output or functionality specifically
  intended to build, analyze, test, deploy, debug, or manage software for
  QNX 8.0. [...] Entrants should identify the relevant files, functions,
  output, or demonstration in your submission description so that reviewers can
  verify the QNX connection." (`https://qnx.devpost.com/rules`, section
  "Submission Requirements", read 15/11/2026).

### 5.8 Codelab URL (only if the Best Codelab / Tutorial bonus is claimed)

<!-- BLOC:4_8 -->

```text
<CODELAB_URL_TO_BE_FILLED_AFTER_THE_CODELAB_IS_PUBLISHED_ON_COMMUNITY.QNX.COM>
```

- Length (measured): 78 characters
- Field limit: no limit published. The requirement comes from the rules: "If
  you are entering the Best Codelab/Tutorial bonus prize: Provide the URL of
  your codelab or tutorial in the designated field on the submission form."
  (`https://qnx.devpost.com/rules`, section "Submission Requirements", read
  15/11/2026).
- The placeholder is deliberate: the codelab text is ready in the repository
  (`docs/CODELAB-COMMUNITY-QNX.md`) but is not published on community.qnx.com
  yet, so no URL is claimed. The bonus is 3,500 USD, 1 winner
  (`https://qnx.devpost.com/`, section "Prizes", read 15/11/2026).

---

## 6. Step 5 - Submit

- Check the box "Agree to the Terms and Conditions" (Devpost help, article
  126, step 5, read 15/11/2026), then click "Submit project".
- The form shows the steps that are still missing; a submission can be edited
  until the deadline (Devpost help, article 122, read 15/11/2026).

## 7. Step 6 - Proofread

Before submitting, check with the "View" button (Devpost help, article 126,
step 6, read 15/11/2026):

| check | expected |
|---|---|
| Project name | `QX PORTMAP` |
| Project tagline | the block 3.2 text, at the length measured in block 3.2 (138 characters, limit 140) |
| Project story | the block 4.1 text, at the length measured in block 4.1 |
| Built with tags | the 11 tags of block 4.2 |
| Try it out | the public repository URL of block 4.3 |
| Video demo link | the public YouTube URL, replacing the placeholder of block 4.5 |
| Category | `Developer Tooling & Host Tools` |
| Repository URL | the public repository URL of block 5.4 |
| Licence | the MIT file is visible at the top of the repository page |
| Thumbnail and gallery | the three screenshots listed in block 4.4 |
| No secret in the text | no token, no account identifier, no private URL |

## 8. Deadlines

| what | when | source |
|---|---|---|
| Submission closes | 15 December 2026, 14:00 EST | `https://qnx.devpost.com/rules`, section "Dates and Timing", read 15/11/2026 |
| Judging | 15 January to 29 January 2027 | same |
| Winners announced | around 4 February 2027 | same |
