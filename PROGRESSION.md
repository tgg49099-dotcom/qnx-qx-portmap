# PROGRESSION - QX PORTMAP

One line per function of the tool: **name**, what it does, its state, the test that proves it.
State = `done` (implemented and tested) / `partial` (done but incomplete) / `planned` (not done).

This file is the map of the tool. It is updated at every cycle, before the report.
The French version is in `PROGRESSION-FR.md`; it follows the same sections, cycle
by cycle, and the English one is currently ahead by four sections (the four
English sections of 15/11 and 16/11 have not been translated yet).

---

## 1. Core of the tool (`qnx_portmap/`)

| Function | What it does | State | Test that proves it |
|---|---|---|---|
| `extract.strip_tags` | Removes the HTML markup and decodes the entities | done | `tests/test_extract.py::TestStripTags::test_removes_markup_and_decodes_entities` |
| `extract.article_of` | Isolates the `<article>` of an Oxygen page (ignores the navigation) | done | `tests/test_extract.py::TestArticle::test_keeps_only_article` |
| `extract.parse_index_page` | Reads the A-Z index of a book: function entries, variables and "described elsewhere" cross-references | done | `tests/test_extract.py::TestParseIndexPage::test_finds_function_entry` |
| `extract.parse_topic_page` | Reads a function page: title, `shortdesc`, Description section | done | `tests/test_extract.py::TestParseTopicPage::test_description_is_the_description_section_not_the_library_one` |
| `extract.bold_identifiers` | Spots the identifiers quoted in bold (cross-references) | done | `tests/test_extract.py::TestParseTopicPage::test_bold_text_is_kept` |
| `extract.sentences_with` | Finds the sentences containing a symbol, word boundary respected | done | `tests/test_extract.py::TestSentencesWith::test_respects_word_boundaries` |
| `corpus.default_corpus_dir` | Finds the frozen corpus (environment variable, then repository) | done | `tests/test_corpus.py::TestCorpusLocation::test_env_var_has_priority` |
| `corpus.Corpus.load` | Loads the manifest and the list of pages | done | `tests/test_corpus.py::TestMiniCorpus::test_loads_pages_and_manifest` |
| `corpus.Corpus.find_url` | Finds a page from its URL | done | `tests/test_frozen_corpus.py::TestFrozenCorpus::test_documented_symbol` |
| `corpus.Corpus.html` / `.text` | Renders the raw HTML / the text of a page | done | `tests/test_corpus.py::TestMiniCorpus::test_page_content_is_readable` |
| `corpus.Corpus.verify` | Verifies the SHA-256 of every page of the corpus | done | `tests/test_corpus.py::TestMiniCorpus::test_detects_a_corrupted_page` |
| `corpus.Corpus.verify_sha256sums` | Verifies the `SHA256SUMS` file of the corpus | done | `tests/test_corpus.py::TestMiniCorpus::test_detects_a_corrupted_sha256sums_file` |
| `corpus.read_symbols` | Reads a list of symbols (lines, commas, comments) and deduplicates it | done | `tests/test_corpus.py::TestReadSymbols::test_removes_duplicates` |
| `classify.Classifier.classify` | Classifies a list of symbols: `documented` / `described_elsewhere` / `absent` / `unknown`, with page and citation | done | `tests/test_classify.py::TestClassification::test_documented_symbol` |
| `classify.Classifier.worklist` | Upgrade work list, absences first | done | `tests/test_classify.py::TestClassification::test_worklist_lists_absent_before_described_elsewhere` |
| `classify.SymbolResult.to_dict` | Serialises a result (used by the JSON output) | done | `tests/test_cli.py::TestCli::test_json_output` |
| `report.render_text` | Text rendering for the terminal | done | `tests/test_cli.py::TestCli::test_text_output` |
| `report.render_json` | JSON rendering (machine) | done | `tests/test_cli.py::TestCli::test_json_output` |
| `report.render_markdown` | Markdown rendering (can be pasted into a submission) | done | `tests/test_cli.py::TestCli::test_markdown_output` |
| `refresh.Downloader.fetch` | Downloads a QNX page with cache, delay and retries | done | `tests/test_fixtures.py::TestFixtureCorpus::test_integrity_is_ok` (path used to build the corpus) |
| `refresh.crawl_book` / `build_corpus_from_cache` | Rebuilds a corpus from qnx.com (network, never by default) | done | `tests/test_cli.py::TestCli::test_verify_corpus_ok` (`--fresh` mode, offline by default) |
| `cli.main` | Entry point: symbols as arguments, `--file`, `--stdin`, `--format`, `--worklist`, `--verify-corpus`, `--stats`, `--fresh` | done | `tests/test_cli.py::TestCli::test_input_from_file` |

## 2. Measurement harness (`tools/`)

| Function | What it does | State | Test that proves it |
|---|---|---|---|
| `mesure_j4.scan_repo` | Extracts the symbols really called in the `.c`/`.h` files of a cloned repository | done | `tests/test_mesure_j4.py::TestEchantillon::test_vingt_symboles_par_depot_et_cinq_depots` |
| `mesure_j4.select_sample` | Chooses 20 symbols per repository (100 distinct ones), QNX family first | done | `tests/test_mesure_j4.py::TestEchantillon::test_cent_symbols_distincts` |
| `mesure_j4.etat` | Turns a result of the tool into one of the 3 exclusive states | done | `tests/test_mesure_j4.py::TestTauxCompteALaMain::test_les_etats_publies_des_dix_symboles_sont_bien_ceux_du_test` |
| `mesure_j4.taux` | Computes the J4 rate (division by zero refused) | done | `tests/test_mesure_j4.py::TestTauxCompteALaMain::test_un_taux_sur_zero_leve_une_erreur` |
| `mesure_j4.measure` | Replays the tool on the sample and collects page, citation and SHA-256 | done | `tests/test_mesure_j4.py::TestMesureReproductible::test_les_statuts_publies_sont_reproduits` |
| `mesure_j4.write_markdown` | Writes `docs/mesure-J4.md` (100 rows, one per symbol), in French (`--lang fr`) or in English (`--lang en`) | done | `tests/test_mesure_j4.py::TestTauxPublie::test_le_taux_du_markdown_vaut_le_taux_calcule` |
| `mesure_j4.write_citations` | Writes the 5 citation files (1 per repository, < 4 000 bytes of QNX text) | done | `tests/test_mesure_j4.py::TestTauxPublie::test_les_pages_de_citations_contenent_chaque_symbole_resolu` |
| `mesure_j4.write_public_json` | Writes the public JSON (without the text of the citations, with their SHA-256) | done | `tests/test_mesure_j4.py::TestEchantillon::test_chaque_symbole_resolu_a_une_page_et_une_citation` |
| `contre_epreuve.main` | Breaks 11 rules one by one and requires that the loaded test fails | done | `docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt` (10/10) and `docs/preuves/b-tests-avec-corpus.txt` (11/11) |
| `controle_fuite_corpus.py` | Anti-leak control: no QNX page in the publishable tree (7 controls) | done | `docs/preuves/d-controle-fuite-corpus.txt` |
| `manifeste_publie.py` | Regenerates `MANIFESTE-PUBLIE.txt` (published files and bytes) | done | `docs/preuves/f-manifeste-publie.txt` |
| `make_fixtures.py` | Builds the 12 test excerpts from the corpus | done | `tests/test_fixtures.py::TestFixtureInvariants::test_every_excerpt_is_verbatim_and_not_empty` |
| `mesure_j5.resoudre_page` | Looks for the exact page of the QNX 8.0 book that describes a "described elsewhere" symbol (verified in the frozen corpus) | done | `tests/test_mesure_j5.py::TestMesureReproductible::test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256` |
| `mesure_j5.etat_j5` | J5 state: "resolved and cited" as soon as the QNX 8.0 page that describes the symbol is verified | done | `tests/test_mesure_j5.py::TestEchantillonJ5::test_le_taux_publie_est_96_pour_cent` |
| `mesure_j5.measure` / `.taux` / `.resume` | Replays the J5 measurement on the same sample as J4 and computes the rate | done | `tests/test_mesure_j5.py::TestMesureReproductible::test_le_taux_recalcule_vaut_le_taux_publie` |
| `mesure_j5.comparer_echantillons` | Verifies that the sample re-derived from the 5 pinned repositories is **strictly** the one of the J4 measurement | done | `tests/test_mesure_j5.py::TestEchantillonJ5::test_echantillon_identique_a_j4` |
| `mesure_kit.py` | Recomputes the length of each block of `KIT-SOUMISSION-QNX.md`, rewrites it, and `--check` fails if a published figure is wrong | done | counter-proof: "138" -> "999" on the tagline block = RC 1 ("2_2: file says 999, measured 138"), RC 0 after restoration |
| `mesure_champs_devpost.py` | Measures the lengths really accepted by Devpost, on 120 published project pages (name, description, tags, URL) | done | `docs/preuves/j-mesure-champs-devpost.txt` (120 pages, summary + detail) |
| `table_mesure_devpost.py` | Turns the raw measurement into an ASCII proof table, without any page extract | done | `docs/preuves/j-mesure-champs-devpost.txt` (ASCII output verified by the script) |

## 3. What remains to be done (seen by the project sheet, not by me)

| Function | State | Test that will prove it |
|---|---|---|
| J5: extend to the system calls (`user_guide`) | planned | to be written |
| J6: `verify-portmap.sh` end to end on a clean machine | planned | to be written |
| J7: 30-minute codelab | planned | to be written |

---

## Progress of this cycle (14/11/2026)

**The J4 measurement (the numerical stop criterion of the project sheet) is done and verified: 93 % (93/100).**

What was built and tested:

- `tools/mesure_j4.py` - the measurement harness: shallow clone of 5 public QNX repositories, extraction
  of the symbols really called, purge of the local definitions, filter on the QNX index
  (8.0 union 7.1), sample of 100 distinct symbols, classification, 3 states, computation of the rate;
- `tools/posix-base.txt` - 732 standard POSIX/C names, written by hand, **independent of the corpus**:
  they serve to separate the "standard" family from the "QNX" family and not to favour the tool;
- `tests/test_mesure_j4.py` - 16 tests, among them the **RED counter-proof**: the rate computed by the
  script must equal the rate counted by hand on 10 symbols given in the test (70 % by hand);
- `docs/mesure-J4.md` + `docs/mesure-J4/` - the 100 symbols (name, repository, state, page, source,
  SHA-256), the 5 citation files, the public JSON;
- `tools/contre_epreuve.py` - 11th counter-proof added: "the J4 rate only counts the symbols
  resolved and cited";
- `README.md` / `LISEZMOI.md` - figures updated (106 tests, 11/11 counter-proofs, J4 93 %);
- `/rapports/FICHE-QNX-2E-OUTIL.md` - section **2.8** ("real state of the measurement of
  14/11/2026": rate, 5 URLs + commits + dates, method, decision).

Result: **J4 = 93 %**, the 80 % threshold is cleared -> the stop criterion of section 2.6 of the project
sheet is **not** triggered, and the plan B of 2.7 is not triggered either. The decision on what
follows belongs to the mother; **no new function was added this cycle**.

## Next steps

1. **Hostile review by Jules** (3 to 6 tasks deposited in `/work/jules-a-faire.txt`): review of
   the code, verification of the figures of the README against the code, robustness of the
   measurement script (division by zero, empty symbol, empty repository, duplicate).
2. **J5** (in the project sheet): extend the classification to the system calls of the
   `user_guide` - only if the mother asks for it; the J5 criterion of the project sheet says to
   postpone it if the gain is low.
3. Publish or push nothing without validation: no public repository, no video, no account, no
   submission.

---

## Progress of this cycle (14/11/2026, mother's J5 slice)

**The resolution rate goes from 93/100 to 96/100 on the SAME sample**, and the
change is proven by a RED then GREEN test.

What was built and tested (nothing in `qnx_portmap/` was modified):

- `tools/mesure_j5.py` - the J5 measurement harness: reads the sample published by the J4
  measurement, replays the classification on the frozen corpus, and for a "described elsewhere"
  symbol looks for the **exact page of the QNX 8.0 book that describes it** (candidates: the
  cross-references of the 8.0 index, the page found in the corpus, the pages of the migration
  guide), verifies it in the frozen corpus and cites its SHA-256 fingerprint;
- `tests/test_mesure_j5.py` - 18 tests: the J5 sample is **strictly** the one of J4 (same
  100 symbols, same order), the rate counted by hand on 10 symbols is 90 %, only the 3
  converted symbols changed state, every cited page is in the frozen corpus with the right
  fingerprint, and the published citation is really extracted from the cited page;
- `docs/mesure-J5.md` + `docs/mesure-J5/` - the 100 symbols, the 5 citation files, the
  public JSON;
- `docs/preuves/h-mesure-j5-rouge.txt` - the RED -> GREEN proof (on the state before: 10 failures,
  RC 1; published data broken: 9 failures, RC 1; restoration: `Ran 18 tests ... OK`, RC 0);
- `scripts/controle_fuite_corpus.py` - the J5 citation files are now analysed fragment by
  fragment like the J4 ones;
- `README.md` - figures updated (124 tests, J5 = 96 %, J4 = 93 % dated).

Result: **J5 = 96 % (96/100)** on the same sample as J4 (93 %). The 3 conversions:

| symbol | before (J4) | after (J5) | cited QNX 8.0 book |
|---|---|---|---|
| `InterruptAttach` | described elsewhere | resolved and cited | migration guide, `kernel.html` |
| `if_freenameindex` | described elsewhere | resolved and cited | io-sock guide, `socket_api.html` |
| `setsockopt` | described elsewhere | resolved and cited | io-sock guide, `socket_api.html` |

The 4 symbols absent from 8.0 (`ND_NODE_CMP`, `pthread_sleepon_lock`,
`pthread_sleepon_unlock`, `fcfgopen`) **stay absent**: the honest ceiling of the rate on this
sample is **96/100**. No new function was added to the tool; the J5 of the project sheet
(extension to the system calls) stays `planned`, that is another thing.

---

## Progress of this cycle (15/11/2026, preparation of the QNX submission)

**The submission folder exists**: the Devpost form kit, the plan of the video, and the
public README in English. **No new function was added to `qnx_portmap/`** (frozen engine,
commit `395ffc2` unchanged).

What was built and verified:

- `KIT-SOUMISSION-QNX.md` (30 060 bytes) - the text to paste into the Devpost form, block by
  block, in the order of the form, with for each block its **measured length** and the limit of
  the field, with its source and its date; **no invented limit**: what the QNX form does not
  display (it is behind a session: HTTP 302 / 401) is said as "not read";
- `VIDEO-YOUTUBE-QNX-PORTMAP.md` (18 817 bytes) - the minute by minute plan of the video
  (2 min 40), with the commands on screen, the **voice-over in English**, and the **single
  segment that is missing** (the execution on QNX 8.0 itself), with what is needed to produce it;
- `tools/mesure_kit.py` - the controller: it recomputes each length of the kit and **fails** if
  a published figure is wrong (counter-proof done: RC 1 when "138" is forced to "999");
- `tools/mesure_champs_devpost.py` + `tools/table_mesure_devpost.py` + `docs/preuves/j-mesure-champs-devpost.txt` -
  the measurement of the lengths really accepted by the platform (120 published Devpost
  projects), which gives the **lower bound** of the unpublished limits;
- `README.md` - section "Build and test (English)" (build, test, the 3 corpus configurations),
  section "Honest limits (English)", links to the kit, the video plan and the codelab, figures
  corrected (the `--fresh --fresh-max-pages` option did not exist; the 27 pages of the short mode
  are measured in **51 s** on 15/11/2026);
- `docs/UTILISATION.md` and `docs/CODELAB-COMMUNITY-QNX.md` - same command correction.

Result: **the folder is submittable**, except the video segment that requires the SDP 8.0
licence (owner's action). The **anti-leak control** replayed on the complete tree (kit and
video plan included): **0 match**, 6 037 bytes of verbatim QNX text, 0 file above the budget of
4 000 bytes (`docs/preuves/d-controle-fuite-corpus.txt`).

Honesty points handled this time:

- the console output of the tool is in **French** while rule l. 320 requires English:
  the kit and the video plan give the **translation table** of the labels;
- the project **has not been run on QNX 8.0** (SDP licence absent): neither the kit, nor the
  README, nor the video claim the opposite; the sentence that said so ("it also runs on
  QNX 8.0 itself") was corrected to "designed to run on QNX 8.0 as well - this has not been
  demonstrated yet".

## Next steps

1. Owner's actions: SDP 8.0 licence + real execution (video segment), public YouTube video
   (08/12), codelab on community.qnx.com (10/12), Devpost form (13/12), 3:2 thumbnail
   and 3 screenshots for the gallery, public repository until 29/01/2027.
2. Question to the mother: is an **English output mode** needed in the tool (change of the
   engine, therefore subject to the freeze)? Is a README **entirely** in English needed?
3. Do nothing without instruction: new function of the engine, Devpost publication, video,
   account, message to Tgg.

---

## Progress of this cycle (15/11/2026, the public repository in English)

**A judge opening the public repository reads no French any more**, except what is
deliberate: the French counterparts kept byte-identical, the raw console output and the
two VERBATIM blocks of the README.

What was done, without touching the frozen engine (`qnx_portmap/` is unchanged since
`395ffc2`):

- `PROGRESSION.md`, `qnx_portmap/LISEZMOI.md`, `docs/mesure-J4.md`, `docs/mesure-J5.md`
  and the **10 citation pages** of the two measurements are now in English; their French
  originals are kept byte-identical in `PROGRESSION-FR.md`,
  `qnx_portmap/LISEZMOI-FR.md`, `docs/mesure-J4-FR.md`, `docs/mesure-J5-FR.md` and
  `docs/mesure-J4/citations-*-FR.txt`, `docs/mesure-J5/citations-*-FR.txt`;
- `tools/mesure_j4.py` and `tools/mesure_j5.py` gained a `--lang` option: the reports
  **and** the citation pages are **produced by the tool itself** in English
  (`--lang en`) and still in French (`--lang fr`, byte-identical to the historical
  files). Re-running the tool with `--lang fr` on the same corpus and the same 5 pinned
  clones reproduces the 10 French citation pages **byte for byte** (proof: `cmp` on the
  10 files), and the English pages carry **exactly the same numbers and exactly the same
  QNX quotations** as the French ones;
- the tests `tests/test_mesure_j4.py` / `tests/test_mesure_j5.py` check that **every
  figure of the English report is the figure of the published JSON** (the tool's own
  output), that both versions contain the same numbers, and that the citation pages
  English and French have the same numbers and the same quotations;
- the RED counter-proof of the English reports is published in
  `docs/preuves/l-rapport-anglais-rouge.txt`: change one figure in
  `docs/mesure-J4.md` (93 % -> 94 %) and the tests fail (4 failures), restore the file
  byte for byte and they pass again;
- `MANIFESTE-PUBLIE.txt` is written in English (`scripts/manifeste_publie.py`), it lists
  the new files and `scripts/manifeste_publie.py --check` returns 0.

Result: **0 French line** in the published tree outside the deliberate whitelist (the
French counterparts, the raw console output kept in the two VERBATIM blocks of the README
and their translation table). The figures are unchanged: **J4 = 93 %**, **J5 = 96 %**,
**170 tests**.

## Progress of this cycle (15/11/2026, English becomes the default language of the console)

Direction of 15/11 21:26: **one single objective for two cycles** - the default
language of the console of QX PORTMAP becomes **English**.

- the CLI default is now English (`qnx_portmap/cli.py`): `--lang` defaults to
  `en`, and the two help texts state the real default ("output language
  (default: en)" and "langue de sortie (defaut : en)");
- **the bytes of the console did not change**: the default output is the English
  output of the day before (`md5 3a4b722c9fd149c7a17abc88b81ab2fb`, 2 901
  bytes, exit code 1) and `--lang fr` still prints the French output of the day
  before (`md5 6e0efa2ee1f4b8f920e51f8d6bbf8436`, 2 964 bytes, exit code 1) -
  both measured on 15/11/2026 with the frozen corpus, the corpus path replaced
  by `<CORPUS>`;
- the comments and the docstrings of `qnx_portmap/`, `tools/` and `scripts/`
  are in English (no behaviour change, no figure written by hand);
- the README, the submission kit, the video plan, `docs/UTILISATION.md` and the
  two LISEZMOI files describe the English default; the quick start is the command
  **without** `--lang`;
- `tests/test_readme_en.py` now checks the **default** output (its marker
  changed) and a new test proves that `--lang fr` still returns the French
  bytes;
- `docs/mesure-J4.md` and `docs/mesure-J5.md` were regenerated by
  `tools/mesure_j4.py` and `tools/mesure_j5.py` (English); the French versions
  and the 20 citation pages did not move (byte for byte);
- the French files stay French and unchanged (`docs/README-FR.md`,
  `docs/mesure-J4-FR.md`, `docs/mesure-J5-FR.md`, `qnx_portmap/LISEZMOI-FR.md`,
  `PROGRESSION-FR.md`), and the archived proofs of `docs/preuves/` are not
  rewritten.

Result: the default console output is the English output of the day before, byte
for byte, and `--lang fr` is the French output of the day before, byte for byte.
The published figures are unchanged: **J4 = 93 %**, **J5 = 96 %**, **170 tests**
(170 tests, 27 of them skipped without the corpus, 1 skipped with the corpus).


## Progress of this cycle (16/11/2026, quick mode and the judge's first command)

- `--quick` (A-Z indexes of the 8.0 and 7.1 C Library Reference, migration guide to 8.0, own page of each documented symbol): **76 pages in 127 s** for `abort accept bzero zzz_fonction_inexistante`, measured on 16/11/2026 at one request per second; it never says `absent`; `tests/test_quick.py` checks on the frozen corpus that it never contradicts the full mode. It is now the first command of the submission kit (section 4.1), and `tools/published_counts.py` also checks the French README and the kit, where stale test counts (124 instead of 183) had been left unchecked.
- 16/11/2026 (mere): the judge's path replayed in a clean virtual environment (venv, `pip install .`, then the quick mode): **76 pages in 144.2 s**, exit code **1** (the expected code: the quick mode answers `unknown` for the two symbols it cannot decide), output identical to the one published in the kit. `pip install .` fails inside a venv when `PIP_USER` is set, so the kit now offers the no-install path (`python3 -m qnx_portmap`).
- 16/11/2026 (Studio): the README quick start, the first thing a judge reads on GitHub, still began with `pip install .` then `qnx-portmap abort ...`: on a PEP 668 Python the install fails and the command does not exist, and without the corpus the full mode can only say `corpus not found`. It now gives the same three commands as the kit (quick mode through `python3 -m`, install optional), the real quick-mode output and the meaning of exit code 1; the full corpus comes after. `tests/test_quick.py` guards it: the quick-start command, the optional install, the same output block in the README and the kit, and (with the frozen corpus) the published block replayed through the real command line.

## Progress of this cycle (16/11/2026, the run on a QNX 8.0 target is prepared)

The one segment that the demonstration video does not contain is the run of
the tool **on a QNX 8.0 target**. It is blocked by the SDP 8.0 licence
(owner's action), but everything that can be done without the SDP was done
this cycle: the procedure, the one-command check, and the sources.

- **What was checked in the official QNX documentation** (all read on
  16/11/2026, the URLs are in `docs/QNX-8.0-CIBLE.md`): the SDP 8.0.3 ships
  a **Python 3.13 for QNX OS targets** (package `com.qnx.qnx800.target.utils.python3`,
  internal version `3.13.7.00013T202603200501L`), so the same command fits a
  QNX 8.0 target; the QNX Everywhere licence is free for non-commercial use
  (myQNX account) and the **Quick Start Target Image for Raspberry Pi 4B**
  already has **PIP installed by default** (release of 11 September 2025), so
  a target with Python is reachable without buying anything; the x86_64 QEMU
  image is built by `mkqnximage --type=qemu --arch=x86_64 --run`.
- **`scripts/qnx8_target_check.sh`** (new): one POSIX-shell command, run from
  the root of the repository, that proves on the target itself that the
  system is a QNX system, that a Python 3 is there, that every page of the
  corpus matches its SHA-256, and that the tool answers. It ends with an
  explicit verdict (`RESULT      : PASS`). It installs nothing, writes
  nothing in the repository, and never touches the network. Two variables
  replace the arguments when needed: `QX_PORTMAP_CORPUS` and
  `QX_PORTMAP_PYTHON` (the release notes do not publish the path of the
  interpreter on the target).
- **Rehearsed, not guessed**: the script was run on 16/11/2026 with `/bin/sh`
  (dash) and with `bash`, from the root of the repository and from another
  directory, with the frozen corpus (3 426 pages verified, `page SHA-256:
  OK`, `SHA256SUMS: OK (3 427 files)`), with the corpus absent (explicit
  failure with the procedure to rebuild it), and with `QX_PORTMAP_PYTHON`.
  The real output is in `docs/QNX-8.0-CIBLE.md`, section 5.
- **`docs/QNX-8.0-CIBLE.md`** (new): what the tool needs on the target, the
  two ways to get a QNX 8.0 target, the exact command to film, how to get
  the corpus onto the target (the QNX documentation is not redistributed),
  the rehearsal and its real output, and the sources with their dates.
- **The honest limit does not move**: the project **has still not been run on
  a QNX 8.0 machine**. The README, the video plan and the new document all
  say so; the check script says `NOT a QNX system - this run is a rehearsal`
  when it is not on a target. The date of the run on a target is the day the
  licence arrives.
- The video plan (`VIDEO-YOUTUBE-QNX-PORTMAP.md`, section 4) now lists the
  two needs that were missing from the table - a Python 3 on the target and
  the corpus on the target - and gives the exact command to film. The
  published figures are unchanged: **194 tests** (33 skipped without the
  corpus), **117 files** in the published manifest.

## Progress of this cycle (16/11/2026, the target check measures the interpreter, the gallery images are ready)

- **`scripts/qnx8_target_check.sh` now measures the interpreter too**: a new
  `compat` line appears right after the version of Python, and a third exit
  code appears in the verdict (`compat exit code`). It answers a question that
  could not be answered before without the target: *is that interpreter new
  enough for the package?* The threshold is not a guess, it is measured (see
  the next point). The check still passes on the rehearsal, with `/bin/sh`
  (dash) and with `bash`, from the root of the repository and from another
  directory, and `--help` now prints the whole header of the script.
- **The compatibility of the target-side code is measured, not assumed**
  (16/11/2026): `vermin --no-parse-comments --target=3.13- --violations
  qnx_portmap/` gives "Minimum required versions: **3.4**" for the 9 files of
  the package, so the **Python 3.13.7** that the SDP 8.0.3 installs on a
  target is new enough for it; the modules the package imports (`argparse`,
  `collections`, `gzip`, `hashlib`, `html`, `json`, `os`, `re`, `string`,
  `sys`, `time`, `urllib`) are **none of the modules that Python 3.13
  removed** (PEP 594) and there is no third-party dependency; the two shell
  scripts have no bashism. Output:
  `/work/preuves-qnx13/PROMESSE-PYTHON-CIBLE.txt`, and the complete output of
  the rehearsal in `/work/preuves-qnx13/rehearsal-cible-16-11-2026.txt` (64
  lines).
- **`docs/QNX-8.0-CIBLE.md`** now states this measurement in section 1,
  quotes the new verdict in section 3, and shows the new `compat` line in the
  real output of section 5.
- **The images of the Devpost gallery are produced and verified** (16/11/2026):
  a 3:2 thumbnail (1500x1000) and three screenshots, all rendered from real
  recorded sessions (`script -T`, replayed through pyte), never retyped. The
  verification is independent of the builder: every drawn line must be
  verbatim in the recording, the PNG on disk must be pixel by pixel identical
  to a re-render from the recording, PNG and under 5 MB, the thumbnail exactly
  3:2 -> `verify_galerie.py` exits 0 on the four images.
- **They are delivered, not committed**: the four PNG, the recordings, the
  builder and the verifier are in `/work/A_ENVOYER/DEVPOST-GALERIE/` with a
  `LISEZ-MOI.txt` (what to upload where, and what the images do not show).
  They are **not** in the repository, because the submission kit states that
  no thumbnail and no screenshot is committed yet, and the kit is not to be
  touched: the images are uploaded to Devpost by the owner.
- **The honest limits do not move**: the project **has still not been run on a
  QNX 8.0 machine**, and the gallery images show the output of the tool on
  the host, not on a target. The published figures are unchanged: **194
  tests** (33 skipped without the corpus), **117 files** in the published
  manifest.


## Progress of this cycle (17/11/2026, the submission text now says how this project differs from our other entry)

- **The Multiple Submissions rule is now answered in the submission text itself.** The
  rules of the QNX Global Hackathon (`https://qnx.devpost.com/rules`, read on
  17 November 2026) say that an entrant may submit several projects, but that each
  submission must be unique and substantially different from each of the entrant's
  other submissions. The project story of `KIT-SOUMISSION-QNX.md` now says, in the
  text the entrant pastes into Devpost, how QX PORTMAP differs from QX-PROBE:
  different input (the QNX symbols a source tree calls vs the C source of a
  resource manager), different output (the state of the documentation vs the access
  gates and dispatch tables), different user, and no shared code, rule or document.
- **The published figures are now 200 tests** (33 skipped without the corpus, exit
  code 0, measured on 17 November 2026) and **118 files** in the published manifest.
  The figures of the previous entry (194 tests, 117 files) are the ones of
  16 November 2026 and are left as they are: this file is a dated log.
- **Checks of this cycle**: `python3 -m unittest discover -s tests -t .` -> 200 tests,
  OK, 33 skipped; `python3 -I tools/mesure_kit.py --check` -> OK, 14 blocks, tagline
  138/140, tags 11/25; `bash scripts/verify-all.sh` -> no check failed (4/7 OK,
  3 not checked on this machine because the frozen corpus is absent).

## Progress of this cycle (17/11/2026, the video is published and its URL is in the kit)

- **The demonstration video is published and public** on YouTube since 17/11/2026:
  `https://youtu.be/UMmxNlxkEi0` - identifier `UMmxNlxkEi0`, title "QX PORTMAP -
  is every QNX symbol your code calls still documented in QNX 8.0?", channel
  "Tgg Labs", **1 min 52 s** (111.04 s, measured on the file by the Studio on
  17/11/2026), so it is under the three minutes the rules ask for. Checked from
  outside the build environment on 17/11/2026: HTTP 200 on the YouTube oEmbed
  of that URL, with that title and that channel.
- **The URL is in the submission kit**: block 4.5 of `KIT-SOUMISSION-QNX.md`
  now carries `https://youtu.be/UMmxNlxkEi0` and its real measured length (28
  characters). The paragraph that said "the placeholder is deliberate: no video
  is published yet" is replaced by the facts above and by what the video shows:
  the tool running in a real terminal (the quick mode against the official QNX
  documentation, the status of each symbol with the official page and the exact
  quotation, the JSON output, the upgrade work list, the test suite).
- **No placeholder is left in the published documents** (new control, check 8
  of `scripts/verify-all.sh`): `tools/controle_placeholders.py` looks for the
  three placeholder markers of this project (the marker of a field to fill, the
  marker of a text to complete, and the length marker of the kit) in the 69
  published documents, and checks that the demonstration video URL is the same
  in the README and in the kit. It **fails on the state before this cycle** (the
  three placeholders of the tree of 17/11, exit code 1) and **passes after**
  (exit code 0). The codelab field (block 4.8 of the kit) is now **empty**: the
  codelab is not published on community.qnx.com, so there is no URL to give,
  and the note says what to do if it goes online before the deadline.
- **The thumbnail of the gallery is now committed and public**: section 3.3 of
  the kit gives the public URL of `media/qx-portmap-demo-thumbnail.png` (PNG,
  172 092 bytes, 1280 x 720), checked HTTP 200 from outside the build
  environment on 17/11/2026. The section said before that no thumbnail was
  committed: that was true when it was written and is false now.
- **The published figures are now 200 tests** (33 skipped without the corpus,
  exit code 0, measured on 17 November 2026) and **119 files** in the published
  manifest (the control of the placeholders is the 119th file). The figure of
  the previous entry (118 files) is the one of the previous cycle: this file is
  a dated log.
- **Checks of this cycle**: `python3 -m unittest discover -s tests -t .` -> 200
  tests, OK, 33 skipped; `python3 -I tools/mesure_kit.py --check` -> OK, 14
  blocks, tagline 138/140, tags 11/25, video URL 28 characters, codelab 0
  character; `python3 -I tools/controle_placeholders.py` -> OK, 69 documents,
  no placeholder; `bash scripts/verify-all.sh` -> no check failed (6/8 OK, 2
  not checked on this machine because the frozen corpus is absent).

## Progress of this cycle (17/11/2026, a quick path in the codelab, a download that survives a cut page, and the numbers of the tutorial are the measured ones)

- **A page cut off by the network no longer stops the corpus download.**
  `qnx_portmap/refresh.py` now catches `http.client.HTTPException`
  (`IncompleteRead`) and retries it like a network error; before, one page
  cut in the middle stopped the whole download with a traceback (measured on
  17/11/2026, page 1545 of 3426). Two tests were added
  (`tests/test_download_retry.py`), and the **RED counter-proof was checked
  by hand** on a temporary copy: with the old `refresh.py` the two tests end
  in `ERROR` (uncaught `IncompleteRead`), with the new one they pass.
- **The codelab has a "2-minute path"**: the quick mode downloads the 26 A-Z
  indexes of 8.0 and 7.1, the migration guide and the page of each documented
  symbol (76 pages) and answers at once. Its real output and its real
  duration are in the tutorial, and the exit code (`1`, because two symbols
  stay `unknown`) is explained: a judge who runs the command must not read
  `1` as a failure.
- **The numbers of the tutorial are the measured ones.** The quick mode was
  run for real on 17/11/2026: 76 pages in **143,7 s**, a duration the tool
  itself writes in `corpus-quick/MANIFEST.json` (`quick.seconds`). The four
  archived measurements are 127 s and 144 s (16/11), 94 s and 151 s (17/11):
  the tutorial now says "about two to three minutes" and gives them, like
  the README and the kit. The full download keeps the published budget
  ("about 1 h 40 to 2 h", 1.7 to 2 s per page).
- **Step 6 keeps only the calls.** The extraction of the symbols of your own
  code now keeps the words followed by `(` and drops the C keywords; the
  tutorial shows the two-line file it counts (8 "symbols" and 6 `unknown`
  without the filter, 3 calls with it) and the answer the tool really gives
  (`abort` documented, `bzero` absent, `f` unknown).
- **The gallery screenshot of the test suite was re-recorded**: it still
  showed "Ran 200 tests" while every published document said 202. It is a
  real recording (`script -T`, replayed through pyte), so it was re-filmed,
  not edited: the new capture shows "Ran 202 tests in 1.130s" and
  "OK (skipped=33)", and `verify_galerie.py` checks that the published PNG
  is the pixel-for-pixel re-render of the recording. The three other images
  are byte-identical. Two figures of the kit follow the image (its size and
  the caption of section 4.4); nothing else of the kit was touched.
- **The published figures are now 202 tests** (33 skipped without the
  corpus, exit code 0, measured on 17 November 2026) and **125 files** in the
  published manifest. The figure of the previous entry (200 tests, 124
  files) is the one of the previous cycle: this file is a dated log.
- **Checks of this cycle**: `python3 -m unittest discover -s tests -t .` ->
  202 tests, OK, 33 skipped (and OK, 1 skipped, with the frozen corpus
  pointed to by `QX_PORTMAP_CORPUS`); `bash scripts/verify-all.sh` -> no
  check failed (6/8 OK, 2 not checked on this machine because the frozen
  corpus is absent from the tree, RC 0), the RED counter-proof of the
  repository is 10/10; `python3 -I tools/mesure_kit.py --check` -> OK;
  `python3 -I tools/controle_placeholders.py` -> OK, 70 documents, no
  placeholder.
