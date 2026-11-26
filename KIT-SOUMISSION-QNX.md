# QX PORTMAP - Devpost submission kit (QNX Global Hackathon)

**Published version of 19 November 2026.** This file replaces the kit of
18/11/2026, which stays in the git history of this repository at commit
`1b46b69`, and the version of 19/11/2026 published at commit `2b0704f`,
which stays there too. Another version of 18/11/2026 (md5
`3d57c6aae4b9efe06407aef5e1ce9c79`) was never added to this repository. What
changed in the version of 18/11, and what changed on top of it:

| # | Change | Why | Evidence |
|---|---|---|---|
| C1 | The project story is now given in **two blocks ready to paste**: **4.1a** (1 170 characters, for the "Text Description" field) and **4.1c** (1 187 characters, for the "Project story" field). Both are under the 1 200 characters of the reference table (tableau 1.1). | The story of the 18/11 kit is 12 263 characters: ten times the 1 200 characters of the reference table (the kits of 15/11 carried 6 816 to 7 566 characters, and the one published at 00:42 on 16/11 carried 8 146). Devpost publishes no limit for this field and 119 public descriptions measured go from 637 to 48 663 characters, so the form would accept the long one - but no paste must exceed the declared limit, so two short versions are given instead. | § 1.4, § 4.1a, § 4.1c |
| C2 | A new block **5.8b** gives the text of the bonus field (1 176 characters). | The kit of 15/11 prepared only a URL for the "Best Codelab / Tutorial" field. The form asks for a text as well; the kit now prepares it. | § 5.8b |
| C3 | The list of excluded countries is quoted verbatim. | The kit of 15/11 put a paraphrase between quotation marks. | § 5.2, the rules page of 18/11/2026 |
| C4 | A table "champ par champ" with the measured length, the limit and the verdict of the 10 fields. | The owner pastes on Sunday: the table says what to paste, how long it is and whether it fits. | § 1.4 |
| C5 | The complete story (12 263 characters, unchanged in the version of 18/11; 12 645 characters after C8, 12 656 after C9) stays in the kit but is **not a block to paste** any more: it is declared as documentation. | The form has no field for it: the two fields of the form get 4.1a and 4.1c, both under the declared limit. The long text is kept as the source of the codelab and of the repository documentation. | § 4.1b |
| C6 | **Every block now declares the field it goes into** ("- Devpost field: **Description**"). | The verifier must not guess where a block goes: the official help gives two names ("Text Description", article 145, and "Project story", article 126) and the form of the contest is behind a session, so the kit says which block goes where. | § 1.4 and the output of the verifier |
| C7 | A new block **4.1d** gives the testing instructions ready to paste (2 552 characters in the version of 18/11; 2 673 characters after C8, 2 687 after C9), added on 19/11/2026. | The kit of 15/11 carried the testing instructions only inside its own story, which measured 6 816 to 7 566 characters; the reference table gives the "Instructions d'installation" field a 3 000-character limit and no short block existed for it. The block is the same text, same commands, same measured numbers, shortened to fit. | § 4.1d |
| **C8** | **The rate is 95 %, not 96 %: `InterruptAttach` is reported "retiré selon le guide".** The blocks that quote the J5 measurement (4.1a, 4.1b, 4.1c, 5.7) now say 95 resolved and quoted, 5 not resolved, and name `InterruptAttach` as removed in 8.0 according to the official migration guide, with the sentence of the guide quoted. | The tool was changed on 19/11/2026: it now reports a function that the official 8.0 migration guide says was removed as `absent`, priority 1, quoting the sentence of the guide - the honest answer. The rate follows it down, from 96 % to 95 %. | § 4.1a, § 4.1b, § 4.1c, § 5.7, `docs/mesure-J5.md` |
| **C9** | **26/11/2026: the testing block can be pasted and run as written.** Block 4.1d said `cd qnx-portmap` right after `git clone .../qnx-qx-portmap.git`, so its second command failed (the folder git creates is `qnx-qx-portmap`); it is now `cd qnx-qx-portmap`. Blocks 4.1b and 4.1d ran the full answer with `qnx-portmap`, a command that exists only after the optional install the same block says can fail (PEP 668); they now run `python3 -m qnx_portmap`, like the quick start. | A judge copies the testing instructions first. `tools/mesure_kit.py --check` now also fails when a `cd` after a `git clone` does not enter the cloned folder, or when a block to paste calls the console script. | § 4.1b, § 4.1d, `tools/mesure_kit.py` |

The verifier that produced this table is the author's own program (one program,
one kit at a time); its register of facts and its measurement log are kept
outside this repository. The lengths of the blocks of this file are recomputed
by a command of this repository, which fails if one of them is wrong:

```
python3 tools/mesure_kit.py --check
```

Prepared on 15 November 2026, revised on 19 November 2026 and on 26 November 2026 (C9). Every block below
is the text to paste into the Devpost submission form, in the order of the form.
All the text to paste is in English, because the contest rules require English
submission materials:

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
newline. The verifier of 19/11/2026 recomputes every length of this file and
fails if one of them is wrong (section 6 of its output), and the tool of the
repository does the same, with the command below:

```
python3 tools/mesure_kit.py --check
```

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

### 1.4 The 10 fields of the form, block by block

What to paste on Sunday, its measured length, the declared limit (tableau 1.1)
and the verdict. Measured by `verif-kit-devpost.py` on 19/11/2026 on this
file; the published limits are in § 1.1 and the observations in § 1.3.

| Devpost field | Block | Measured | Declared limit | Verdict |
|---|---|---|---|---|
| Titre ("Submission name") | § 3.1 / 2_1 | 10 | 60 | OK |
| Tagline ("Submission tagline") | § 3.2 / 2_2 | 138 | 140 | OK |
| Description ("Text Description") | § 4.1a / 3_1a | 1 170 | 1 200 | OK |
| Description etendue ("Project story") | § 4.1c / 3_1c | 1 187 | 1 200 | OK |
| Instructions d'installation (testing) | § 4.1d / 3_1d | 2 687 | 3 000 | OK |
| Mots-cles ("Built with tags", 11 tags) | § 4.2 / 3_2 | 104 | 200 | OK |
| Video ("Video demo link") | § 4.5 / 3_5 | 28 | 1 000 | OK |
| Categorie ("Category") | § 5.3 / 4_3 | 30 | 120 | OK |
| Lien d'installation ("URL to your code repository") | § 5.4 / 4_4 | 49 | 2 000 | OK |
| Description du bonus ("Best Codelab / Tutorial") | § 5.8b / 4_8b | 1 176 | 1 200 | OK |
| Liens/URL ("Try it Out links") | § 4.3 + § 5.8 / 3_3 + 4_8 | 139 | 4 000 | OK |

Two blocks are not fields of the form: block 4.1b (the complete story,
12 656 characters, kept as documentation) and block 4.7 (evidence of QNX use,
2 959 characters, a required attachment of the QNX contest, not a Devpost
text field). No block exceeds the declared limit: the closest to its limit is
the Project story block (1 187 of 1 200 characters, 99 %).

---

## 2. Step 1 - Manage your team

No questions in this step (Devpost help, article 126). The entry is made by a
single person: see block 4.1.

---

## 3. Step 2 - Project Overview

### 3.1 Project name

- Devpost field: **Titre** ("Submission name", step 2)

<!-- BLOC:2_1 -->

```text
QX PORTMAP
```

- Length (measured): 10 characters
- Field limit: no limit published (Devpost help, article 145, read 15/11/2026)

### 3.2 Project tagline

- Devpost field: **Tagline** ("Submission tagline", step 2)

<!-- BLOC:2_2 -->

```text
QX PORTMAP tells you, for every QNX symbol your code calls, whether QNX 8.0 still documents it - with the page, the quote and the SHA-256.
```

- Length (measured): 138 characters
- Field limit: **140 characters** (Devpost help, article 145: "Submission tagline (140 characters)*", page dated "Last updated on November 12, 2026", read 15/11/2026)

### 3.3 Thumbnail image for the Project Gallery

Not a text field. Format JPG, PNG or GIF, 5 MB max, 3:2 ratio (Devpost help,
article 126, read 15/11/2026). **The thumbnail is committed to the repository
and is publicly readable**; this is the file to upload:

```text
https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/qx-portmap-demo-thumbnail.png
```

- Measured on 17/11/2026: PNG, 172 092 bytes, 1280 x 720 (16:9), which is
  under the 5 MB limit. Devpost asks for a 3:2 ratio "for best results"
  (article 126) and accepts PNG, JPG and GIF: the ratio of this one is 16:9,
  the format and the size are accepted.
- The image is the thumbnail of the demonstration video (section 4.5): the
  terminal output of the tool, never retyped.
- The URL was checked from outside the build environment on 17/11/2026:
  HTTP 200, `image/png`, 172 092 bytes.
- **A 3:2 thumbnail is committed too**, for the field that asks for the 3:2
  ratio "for best results" (article 126). It is the same screen, rendered in
  3:2, and it is the alternative to upload in this field:

```text
https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/galerie-miniature-3x2.png
```

- Measured on 17/11/2026: PNG, 161 276 bytes, 1500 x 1000, **exactly 3:2**,
  under the 5 MB limit. The URL was checked from outside the build
  environment on 17/11/2026: HTTP 200, `image/png`, 161 276 bytes.
- The choice between the two files (16:9 thumbnail of the video, 3:2
  thumbnail of the gallery) is the owner's; both are public and both show
  the real output of the tool.

---

## 4. Step 3 - Project Details

### 4.1a Description courte - the block to paste in "Text Description" / "About the project"

- Devpost field: **Description** ("Text Description", step 3)

<!-- BLOC:3_1a -->

```markdown
QX PORTMAP - a documentation map for the QNX 8.0 symbols your code calls

## How this differs from our other entry

The rules allow one entrant to submit several projects, but "each Submission must be unique and substantially different from each of the Entrant's other Submissions". Our other entry, QX-PROBE, is a source checker: it reads the C source of a QNX 8.0 resource manager and reports the access gates and dispatch tables the QNX 8.0 documentation requires. QX PORTMAP is a documentation mapper: it reads the QNX symbols a source tree calls and answers, for each one, whether it is still documented in QNX 8.0, with the official page and the exact quotation. Different inputs, different outputs, no shared code and no shared document.

## What the tool does

For each symbol it resolves, QX PORTMAP prints the official page, the exact quotation and the SHA-256 of the page, then a work list of the symbols to fix, sorted by priority. A symbol it cannot decide stays `unknown`: the tool never guesses.

## Measured

On 100 QNX symbols really called by five public QNX repositories: 95 resolved and quoted. 246 tests, no failure. Pure Python 3, no SDK, no board.
```

- Length (measured): 1170 characters
- Field limit: **1 200 characters** (tableau 1.1, the reference table measured
  on another form and relayed by the owner on 14/11/2026 22:20). Devpost
  publishes **no** limit for this field: the "Text Description*" question of
  the help article 145 carries no number, and 119 public project descriptions
  measured on 15/11/2026 go from 637 to 48 663 characters (median 3 659).
  This block is the one that fits
  the declared limit; block 4.1b is the same story with every section, for
  the judge who has the room for it.
- The paragraph "How this differs from our other entry" is kept in this short
  version on purpose: the rules ask for it ("each Submission must be unique
  and substantially different from each of the Entrant's other Submissions",
  `https://qnx.devpost.com/rules`, read 18/11/2026).

### 4.1b The complete story (12 656 characters) - kept in the kit, not a block to paste

- Devpost field: **documentation** (not a field of the form: this text is the complete story, kept for the codelab and the repository)

<!-- BLOC:3_1b -->

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

For every symbol it resolves, QX PORTMAP prints the official page and the exact
quotation taken from that page. The SHA-256 of every page of the snapshot is
recorded in the corpus index and checked by `qnx-portmap --verify-corpus`, so a
reviewer can check the answer without trusting the tool. It then prints a work
list of the symbols to fix, sorted by priority.

## What it does not do

- It does not analyse a binary and it does not run on the target: it analyses
  the documentation.
- It does not redistribute the QNX documentation. The corpus (about 4,000 pages,
  QNX 7.1 and 8.0) is rebuilt on demand from the official QNX site with one
  command and one download log. **The first download takes about two hours**
  at one request per second (about 2 s per page: 1.7 to 2.0 s measured on 15 and
  16 November 2026, and 1.87 s per page measured over a complete judge replay on
  18 November 2026: 3,973 pages in 2 h 03, 0 failure -- 547 more pages than the
  frozen snapshot of 14 November, all of them in the 7.1 C Library Reference);
  after that the tool works offline. A **quick mode** (`--quick`,
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
minutes (76 pages downloaded in 127 s in the build environment, in 144 s in an
independent replay from a clean virtual environment, both measured on
16 November 2026, and in 151.2 s on the filming machine the same day, from a
fresh clone, shown on screen in the video, at one request per second). It
reads only the A-Z indexes of
the QNX 8.0 and 7.1 C Library Reference, the official migration guide to 8.0
and the own page of each documented symbol. It answers `documented` and
`described elsewhere` like the full mode, and it says `absent` **only** for a
symbol that the official migration guide (read in full) says was removed,
quoting the sentence of the guide; any other symbol that only the full corpus
can decide is reported `unknown`, with a note that says why.
The exit code of that run is **1**, and that is the expected code: `0` when
every analysed symbol is documented in 8.0, `1` when at least one symbol is
absent or unknown, `2` on error. The quick mode answers `unknown` for the two
symbols it cannot decide, so `1` is the right code here.
Real output of that run (one status line and one note line per symbol; the page,
citation and detail lines are elided here, like in the full-mode output below):

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
complete corpus once: **about 4,000 pages** of the official QNX
documentation, one request per second. **Budget about two hours**
(about 2 s per page: 1.7 to 2.0 s measured on 15 and 16 November 2026, and
1.87 s per page measured over a complete judge replay on 18 November 2026:
3,973 pages in 2 h 03, 0 failure). The
tool then runs offline:

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m qnx_portmap abort accept bzero
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
commits) are classified by the tool: **95 of them are resolved and quoted**
(95 %), 5 are not, and the 5 are honest: four had a page in the 7.1 C Library
Reference and have none in the 8.0 corpus, so the tool reports them as
`absent` with their 7.1 page rather than dropping them; and the fifth,
`InterruptAttach`, is reported as **removed in 8.0 according to the official
migration guide** - quoted by the tool: "The following functions have been
removed: InterruptAttach() InterruptAttachArray() InterruptHookIdle2()
InterruptHookTrace()". The list of the 100
symbols, the citation of each one and the SHA-256 of the cited page are in
`docs/mesure-J5.md` and `docs/mesure-J5/`. The figure was reproduced on
19 November 2026 with `tools/mesure_j5.py`.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

246 tests, no third-party dependency, no network access. Measured on
23 November 2026 in the three possible configurations: with the corpus in
`corpus/` next to the package, 246 tests and 0 skipped; with the corpus
pointed to by the environment variable `QX_PORTMAP_CORPUS`, 246 tests and 1
skipped; without any corpus, 246 tests and 33 skipped (the skipped ones are
the ones that need the corpus). The suite also contains
a RED -> GREEN proof: `tools/contre_epreuve.py` breaks one rule of the code
at a time and checks that the matching test turns red, then restores the
repository. The 12 rules and their output are in `docs/contre-epreuve-rouge.txt`.

## Honest limits

- The tool itself is a host tool: it needs no QNX 8.0 target to run, and it
  does not run on the target.
- The project has **not** been compiled or executed on a QNX 8.0 target yet:
  that requires the QNX SDP 8.0 licence, which is not available in this
  environment. The code is Python 3 standard library only and POSIX-compatible,
  but this has not been demonstrated on a QNX 8.0 machine.
- The 95 % figure is a measurement on one sample of 100 symbols; it is not a
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
  `NOTICES-DOCS-QNX.md` and `CORPUS-NON-PUBLIE.txt`.
- Codelab / tutorial, published in this repository: https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/CODELAB-COMMUNITY-QNX.md

## AI-assisted development

This project was written with the help of an AI coding assistant. The
assistant wrote the code, the tests and the documentation. Nothing about QNX
is taken on trust: every statement about a QNX symbol is backed by an exact
quotation of an official page (URL, date, SHA-256), and the behaviour of the
tool is checked by the test suite and by the RED -> GREEN proof described
above.
```

- Length (measured): 12656 characters
- **This block is not pasted in the form.** It is the complete story: every
  section, with the details the two short versions leave out. The two fields
  of the form get block 4.1a (1 170 characters) and block 4.1c (1 187
  characters), both under the 1 200 characters of the reference table. This
  text is kept here because it is the source of the codelab and of the
  repository documentation, and because the verifier checks its announced
  length (the line above is exact).
- Devpost publishes **no** character limit for the description field (help
  articles 145 and 126, read 15/11/2026). Observation on the same platform:
  120 public project pages measured on 15/11/2026, published descriptions from
  637 to 48 663 characters, median 3 659; no truncation observed at any lower
  bound. So the platform would accept this text too: pasting it is the
  owner's decision, not a technical necessity.

### 4.1c Description etendue - the block to paste in the "Project story" field, if the form shows one

- Devpost field: **Description etendue** ("Project story", step 3)

<!-- BLOC:3_1c -->

```markdown
QX PORTMAP - a documentation map for the QNX 8.0 symbols your code calls

## How this differs from our other entry

The rules ask for entries that are "unique and substantially different". QX PORTMAP is not a version of our QX-PROBE entry: QX-PROBE reads the C source of a QNX 8.0 resource manager and reports the access gates and dispatch tables the documentation requires; QX PORTMAP reads the QNX symbols a source tree calls and answers, for each, whether it is still documented in QNX 8.0, with the official page and the quotation. Different inputs, different outputs, no shared code.

## What the tool does

For each symbol, QX PORTMAP prints the official page, the exact quotation and the SHA-256 of the page, then a work list of the symbols to fix, by priority. A symbol it cannot decide stays `unknown`: it never guesses.

## Run it in three commands

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap
python3 -m qnx_portmap --quick abort accept bzero
```

Pure Python 3, standard library only: no SDK, no board.

## Measured

On 100 QNX symbols really called by five public QNX repositories: 95 resolved and quoted. 246 tests, no failure.
```

- Length (measured): 1187 characters
- Field limit: **1 200 characters** (tableau 1.1, the reference table measured
  on another form and relayed by the owner on 14/11/2026 22:20). Devpost
  publishes **no** limit for this field: the "Project story*" question of the
  help article 126 carries no number, and 119 public project descriptions
  measured on 15/11/2026 go from 637 to 48 663 characters (median 3 659).
- **Which one to paste**: the form of the contest is behind a session, so the
  two names of the official help ("Text Description", article 145, and
  "Project story", article 126) cannot be told apart before Sunday. If the
  form shows ONE description field, paste block 4.1a (1 170 characters). If it
  shows TWO, paste 4.1a in the "Text Description" field and this block (1 187
  characters) in the "Project story" field. Both are under the 1 200
  characters of the reference table, so no paste can overflow it.

### 4.1d Testing instructions - the block to paste in the "testing instructions" part of the description

- Devpost field: **Instructions d'installation**

<!-- BLOC:3_1d -->

```markdown
## Run it in three commands

```bash
git clone https://github.com/tgg49099-dotcom/qnx-qx-portmap.git
cd qnx-qx-portmap && pip install .   # optional: the tool needs only the standard library
python3 -m qnx_portmap --quick abort accept bzero zzz_fonction_inexistante
```

The install is optional and can fail on a locked-down Python (a system Python
protected by PEP 668 refuses it, measured on 16 November 2026): the tool is
pure standard library, the third command works with or without it, and
`python3 -m qnx_portmap` is the same program as the `qnx-portmap` command an
install gives.

The third command is the **quick mode**: a first answer in about two to three
minutes (76 pages in 127 s in the build environment, in 144 s in an
independent replay, both measured on 16 November 2026, and in 151.2 s on the
filming machine that same day, from a fresh clone, one request per second).
It reads only the A-Z indexes of the QNX 8.0 and 7.1 C Library Reference, the
official migration guide to 8.0 and the own page of each documented symbol.
It says `absent` only for a symbol that the official migration guide (read in
full) says was removed, quoting the sentence of the guide; any other symbol
that only the full corpus can decide is reported `unknown`. Exit code **1** is
expected here: `0` when every analysed symbol is documented in 8.0, `1` when
at least one is absent or unknown, `2` on error.

Real output of that run (one status line per symbol; the note, page, citation
and detail lines are elided here; the complete session is in the repository
README):

```text
  abort                        documented
  accept                       described elsewhere
  bzero                        unknown
  zzz_fonction_inexistante     unknown
```

For the full answer (quotations, SHA-256, and `absent`), download the complete
corpus once: **about 4,000 pages** of the official QNX documentation, one
request per second, **budget about two hours** (1.7 to 2.0 s per page measured
on 15 and 16 November 2026, and 1.87 s per page over a complete judge replay
on 18 November 2026: 3,973 pages in 2 h 03, 0 failure). The tool then runs
offline:

```bash
bash scripts/bootstrap_corpus.sh --out corpus-downloaded
QX_PORTMAP_CORPUS=$PWD/corpus-downloaded python3 -m qnx_portmap abort accept bzero
```

Real output, executed on 15 November 2026 against the 3,426-page corpus
(status lines only; the complete session is in the repository README):

```text
  abort                        documented
  accept                       described elsewhere
  bzero                        absent
```

Without a corpus the tool prints `corpus not found` and exits with code 2: it
never invents an answer.
```

- Length (measured): 2687 characters
- Field limit: **3 000 characters** (tableau 1.1). Devpost publishes no
  separate limit for this field: the help article 126 lists the testing
  instructions with the project story, and the form is behind a session.
- This block is the testing-instructions part of the complete story (block
  4.1b, unchanged), shortened to fit the declared limit: same commands, same
  measured numbers, shorter prose. If the form has no separate field for
  testing instructions, paste it at the end of the "Project story" field
  (4.1a + 4.1d = 3 857 characters, far under the 48 663 characters observed
  on public pages).

### 4.2 Built with tags

- Devpost field: **Mots-cles** ("Built with tags", step 3)

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

- Devpost field: **Liens/URL** ("Try it Out links", step 3)

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
15/11/2026). **The four images are committed to the repository and are
publicly readable.** Each one is a real recording of a real command: every
line drawn in them is the verbatim output of the tool, never retyped. The
only texts that are not the output of the tool are the title bars and the
footers of the two 3:2 images, and each of them repeats a fact that the
capture it belongs to already prints.

| file | public URL | bytes | size | md5 | Devpost field |
|---|---|---:|---|---|---|
| `media/galerie-miniature-3x2.png` | `https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/galerie-miniature-3x2.png` | 161 276 | 1500 x 1000 (3:2) | `a95afc6864ab55327f3e62fe6f1645f3` | Thumbnail image for the Project Gallery |
| `media/galerie-1-statuts.png` | `https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/galerie-1-statuts.png` | 154 689 | 1300 x 949 | `eb705e77ed1acb942f305a66f8746431` | Image Gallery |
| `media/galerie-2-json.png` | `https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/galerie-2-json.png` | 87 887 | 1300 x 1033 | `0ec556c674ddd603a5b341f8da07295e` | Image Gallery |
| `media/galerie-3-tests.png` | `https://raw.githubusercontent.com/tgg49099-dotcom/qnx-qx-portmap/main/media/galerie-3-tests.png` | 44 175 | 1500 x 1000 (3:2) | `7a1adf2c24c855f035050f5b619d93f7` | Image Gallery |

- The three gallery screenshots are the three screenshots of the table
  below, taken on 17/11/2026 (screenshot 3 was put back on a 3:2 canvas on
  18/11/2026, from the same recorded session, and re-made on 24/11/2026
  from a new recording of the same command on the 246-test tree), in this
  order:

| screenshot | file | command | what it shows |
|---|---|---|---|
| 1 | `media/galerie-1-statuts.png` | `python3 -m qnx_portmap abort accept bzero` | the three statuses (documented / described elsewhere / absent), the official page, the exact quotation and the upgrade work list |
| 2 | `media/galerie-2-json.png` | `python3 -m qnx_portmap --format json abort` | the same answer in JSON, with English field names |
| 3 | `media/galerie-3-tests.png` | `python3 -m unittest discover -s tests -t .` | the test suite result: `Ran 246 tests`, `OK (skipped=33)` |

- The 3:2 thumbnail is the same screen as screenshot 1, with a title bar
  and a footer; it is the file to upload in the field of section 3.3.
- Screenshot 3 is in the exact 3:2 ratio too (1500 x 1000), like the
  thumbnail: Devpost shows the gallery images in a fixed frame, and a 3:2
  image is not cropped. It was re-rendered on a 3:2 canvas from the
  recording of 24/11/2026: the lines drawn are the verbatim lines of that
  recording, and its title bar and its footer only repeat what the capture
  already prints (`Ran 246 tests`, `OK (skipped=33)`).
- All four files are PNG, under the 5 MB limit of Devpost (the biggest one
  is 161 276 bytes). The URLs were checked from outside the build
  environment on 17/11/2026 and again on 18/11/2026, and the URL of
  screenshot 3 was checked again on 24/11/2026 after its update: HTTP 200,
  `image/png`, the size and the md5 announced above.
- What the images do **not** show: the tool running on a QNX 8.0 target.
  It is a host tool, and the SDP 8.0 licence is not available in the build
  environment (section "Honest limits" of block 4.1 says so too). No QNX
  screen is simulated in them.

### 4.5 Video demo link

- Devpost field: **Video** ("Video demo link", step 3)

<!-- BLOC:3_5 -->

```text
https://youtu.be/UMmxNlxkEi0
```

- Length (measured): 28 characters
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
- The video **is published and public** on YouTube since 17/11/2026: identifier
  `UMmxNlxkEi0`, title "QX PORTMAP - is every QNX symbol your code calls still
  documented in QNX 8.0?", channel "Tgg Labs", duration **1 min 51 s**
  (111.04 s, measured on the file by the Studio on 17/11/2026), so it is under
  the three minutes the rules ask for. The URL above was checked from outside
  the build environment on 17/11/2026: HTTP 200 on the YouTube oEmbed of
  `https://youtu.be/UMmxNlxkEi0`, with that title and that channel.
- **The figures stated in the video are the figures of its day**: it says
  96 %, which was the published rate on 17 November 2026, the day it was
  published. The tool was changed on 19 November 2026 and the published rate
  is now 95 % (change C8 above): the video shows the tool as it was on
  17/11, the documents of this repository show the tool as it is.
- It is not a title card: the video shows the tool running in a real
  terminal, filmed from a fresh clone of this public repository - the quick
  mode against the official QNX documentation (the A-Z indexes of the QNX 7.1
  and 8.0 C Library Reference and of the 8.0 migration guide, 76 pages at one
  request per second, the wait shortened in the video), the status of each symbol
  with the official page and
  the exact quotation, the JSON output, the upgrade work list and the test
  suite. The video states its own limit: QX PORTMAP is a host tool, so it is
  not filmed running on a QNX 8.0 target (that would need the SDP 8.0
  licence).
- The video file itself is downloadable from this repository:
  `media/qx-portmap-demo-final.mp4` (1 832 957 bytes), with its thumbnail
  `media/qx-portmap-demo-thumbnail.png`. The plan of the video and the
  YouTube fields are in `VIDEO-YOUTUBE-QNX-PORTMAP.md`.

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
  Cuba, Iran, and North Korea and any other country which is comprehensively
  sanctioned by the U.S. Treasury's Office of Foreign Assets Control", and
  Switzerland is not among them (`https://qnx.devpost.com/rules`, section
  "Eligibility", re-read on 18/11/2026; the page does not contain the word
  "Switzerland": `grep -ci Switzerland` returns 0).

### 5.3 Category

- Devpost field: **Categorie** ("Category", step 4)

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

- Devpost field: **Lien d'installation** ("URL to your code repository", step 4)

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

- Devpost field: **Preuve QNX** ("Evidence of QNX use", step 4; not one of the 10 fields of tableau 1.1)

<!-- BLOC:4_7 -->

```text
QX PORTMAP is a host tool whose output exists to analyse software written for
QNX 8.0: it tells a QNX 8.0 developer whether each symbol their code calls is
still documented in the official QNX SDP 8.0 documentation, and where.

The relevant files, in the public repository
https://github.com/tgg49099-dotcom/qnx-qx-portmap:

- `qnx_portmap/extract.py` parses the index page of the QNX 8.0 C Library
  Reference (`parse_index_page`) and the topic pages (`parse_topic_page`), and
  extracts the "Description" section of a symbol page.
- `qnx_portmap/classify.py` (`Classifier`) decides the four states of a symbol
  in QNX 8.0: documented, described elsewhere, absent, unknown. The
  "described elsewhere" case links a symbol to the page of the QNX 8.0
  io-sock User's Guide or of the QNX SDP 8.0 migration guide that describes
  it.
- `qnx_portmap/corpus.py` reads the corpus snapshot: it is not redistributed
  with this repository (licence). It is rebuilt by
  `bash scripts/bootstrap_corpus.sh --out corpus-downloaded`, which writes
  `corpus-downloaded/index/pages.jsonl` (the index) and
  `corpus-downloaded/SHA256SUMS` (the fingerprints of the files).
  `qnx-portmap --verify-corpus` compares the SHA-256 of every page with the
  index, so the quotation comes from the page it names.
- `qnx_portmap/cli.py` and `qnx_portmap/report.py` produce the output.

The output to look at: for each symbol, the official QNX 8.0 page and the exact
quotation taken from that page; its SHA-256 is in the snapshot index,
`corpus-downloaded/index/pages.jsonl`. Example, executed on 15 November 2026:

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
description block; the console labels are in the repository README.

The measurement on real QNX code is in `docs/mesure-J5.md`: 100 QNX symbols
really called by five public QNX repositories, pinned commits, classified by
the tool, 95 resolved and quoted with the URL and the SHA-256 of the cited
page; `InterruptAttach` is reported removed in 8.0 according to the official
migration guide, sentence quoted. The cited pages are in
`docs/mesure-J5/citations-*.txt`.

What is not claimed: the project has not been compiled or executed on a QNX
8.0 target, because the QNX SDP 8.0 licence is not available in this
environment. The tool itself needs no QNX target to run: it is pure Python 3,
standard library only.
```

- Length (measured): 2959 characters
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

- Devpost field: **Liens/URL** ("Codelab URL", step 4)

<!-- BLOC:4_8 -->

```text
https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/CODELAB-COMMUNITY-QNX.md
```

- Length (measured): 89 characters
- Field limit: no limit published. The requirement comes from the rules: "If
  you are entering the Best Codelab/Tutorial bonus prize: Provide the URL of
  your codelab or tutorial in the designated field on the submission form."
  (`https://qnx.devpost.com/rules`, section "Submission Requirements", read
  15/11/2026).
- **The tutorial is published in the public repository**, at the URL of the
  block above: `docs/CODELAB-COMMUNITY-QNX.md` is a codelab / tutorial
  written during the submission period (first committed on 15/11/2026,
  published version of 17/11/2026), in English, with the commands and the
  expected output of every step. It teaches a task **for QNX 8.0**: find
  out which of the QNX calls your project makes are still documented in
  QNX 8.0 - first by hand on the official documentation, then with the tool
  of this project. The rules accept a tutorial that does not have to be
  related to the project ("The codelab is not required to relate to the
  Entrant's Project"), and this URL is a public URL of the repository the
  rules already ask for in the field of block 5.4.
- The URL was checked from outside the build environment on 17/11/2026:
  HTTP 200, and the file it points to is the tutorial itself.
- The proposal of a post on community.qnx.com is kept in the repository
  (`docs/CODELAB-FORUM-PROPOSITION.md`). The owner may post it there; the
  tutorial does not depend on it.
- The bonus is 3,500 USD, 1 winner
  (`https://qnx.devpost.com/`, section "Prizes", read 15/11/2026).

### 5.8b Description du bonus (the text of the "Best Codelab / Tutorial" field)

- Devpost field: **Description du bonus** ("Best Codelab / Tutorial", step 4)

<!-- BLOC:4_8b -->

```text
This tutorial is a codelab for QNX 8.0: find out which of the QNX calls your project makes are still documented in QNX 8.0.

You maintain C code that calls the QNX C Library and you have to move it to QNX 8.0. The call itself is not the hard part; knowing which of the calls your code makes still exist in the QNX 8.0 documentation, which ones moved to another book, and which ones disappeared - each case needs a different decision in your port.

In about 30 minutes you do that job twice: by hand on the official QNX 8.0 documentation (about 10 minutes, the method that works with no tool at all), then with QX PORTMAP, the tool of this repository (about 5 minutes): the same work, automated, reproducible and quotable. Every answer comes with the official page, the exact quotation taken from it and the SHA-256 of the page, so a reader can check the answer without trusting the tool.

The tutorial is in English, published in the public repository during the submission period, and needs nothing but Python 3: no QNX SDP, no board, no licence, no account. It ends with the work list of the calls that need a decision, which is exactly the deliverable of a port to QNX 8.0.
```

- Length (measured): 1176 characters
- Field limit: 1 200 characters (tableau 1.1, the reference table relayed by
  the owner on 14/11/2026 22:20). Devpost publishes no limit for this field.
- The URL of the codelab is the block above (5.8); this block is the text
  that goes with it. The kit of 15/11/2026 prepared only the URL.
- Every fact of this text is measured: the codelab is published in the public
  repository (`docs/CODELAB-COMMUNITY-QNX.md`, HTTP 200 on 17/11/2026), it is
  in English, it needs nothing but Python 3, and it ends with the work list
  of the calls that need a decision.

### 5.9 File upload (optional field, not used)

No file is uploaded. The field is optional ("File upload (if any)", 35 MB max,
zip, pdf, word or apk - Devpost help, article 126, section "Step 4:
Additional Details", read 15/11/2026). The rules ask for "a URL to your
public code repository for judging and testing on either GitHub, GitLab, or
Bitbucket" (`https://qnx.devpost.com/rules`, section "Submission
Requirements", read 15/11/2026), and that URL is the one of block 4.4. The
repository is public and can be cloned without an account, so nothing has to
be uploaded.

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
| Video demo link | the public YouTube URL of block 4.5 (`https://youtu.be/UMmxNlxkEi0`) |
| Category | `Developer Tooling & Host Tools` |
| Repository URL | the public repository URL of block 5.4 |
| Licence | the MIT file is visible at the top of the repository page |
| Thumbnail and gallery | the thumbnail file of section 3.3 (`media/galerie-miniature-3x2.png`, 3:2), and the three screenshots of block 4.4 (`media/galerie-1-statuts.png`, `media/galerie-2-json.png`, `media/galerie-3-tests.png`) |
| Codelab URL (bonus) | the URL of block 5.8, and the page it points to is the tutorial |
| No secret in the text | no token, no account identifier, no private URL |

## 8. Deadlines

| what | when | source |
|---|---|---|
| Submission closes | 15 December 2026, 14:00 EST | `https://qnx.devpost.com/rules`, section "Dates and Timing", read 15/11/2026 |
| Judging | 15 January to 29 January 2027 | same |
| Winners announced | around 4 February 2027 | same |
