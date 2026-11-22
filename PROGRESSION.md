# PROGRESSION - QX PORTMAP

One line per function of the tool: **name**, what it does, its state, the test that proves it.
State = `done` (implemented and tested) / `partial` (done but incomplete) / `planned` (not done).

This file is the map of the tool. It is updated at every cycle, before the report.
The French version is in `PROGRESSION-FR.md`; it follows the same sections, cycle
by cycle, and the two files now carry the same sections in the same order.

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
  "Tgg Labs", **1 min 51 s** (111.04 s, measured on the file by the Studio on
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

## Progress of this cycle (18/11/2026, the kit was replayed as a judge, and the legend of the README is corrected)
- **The kit was replayed, not read.** A fresh clone (`/tmp/juge`), a fresh
  virtual environment, `pip install .`, then **every command of the kit, in the
  order of the kit**: for each claim, the real output, the real duration and
  the real exit code. **63 claims checked, 1 false**: the legend of the quick
  mode said "one line per symbol", while the program prints six lines per
  symbol (status, page, citation, detail, note) and the published block only
  shows two because the three in between are elided. The legend of the kit now
  says what is elided: "one status line and one note line per symbol; the
  page, citation and detail lines are elided here, like in the full-mode
  output below". Two figures were added on the same measurement: the quick
  mode took **149,1 s** in that replay, and the full corpus runs at **2,03 s
  per page** over its first 160 pages, which projects to about 1 h 56 for the
  3 426 pages. The whole table of the 63 claims is in
  `/work/NOTES-KIT-JUGE-20261118.md`.
- **The same false sentence was in `README.md`, line 77.** It is now corrected
  and published: the legend of the README is the one of the kit, **word for
  word**, with the same line break. A program compares the two parentheses
  and answers `True`; "one line per symbol" and "header elided" are gone from
  the README. **No other line of the README was touched.**
- **The published manifest hashes the README.** The first `verify-all.sh`
  after the correction answered **RC 1** with two rows that are not bugs:
  `published manifest FAILED` ("MANIFESTE-PUBLIE.txt est obsolete :
  regenerez-le.") and `RED counter-proof NOT CHECKED` ("the working copy is
  not clean"). The manifest had to be regenerated
  (`python3 -B scripts/manifeste_publie.py`, **126 files**) and the commit had
  to come **before** the verification. The order that works is now: edit,
  regenerate the manifest, commit, verify, push.
- **Checks of this cycle**: `python3 -B tools/controle_placeholders.py` -> OK,
  70 documents, no placeholder; `bash scripts/verify-all.sh` -> **RC 0**,
  **6/8 OK and 2 NOT CHECKED** (the anti-leak control and the parity of the
  README block, which need the corpus), the unit test suite **202 tests, 33
  skipped**, the RED counter-proof **10/10**, the lengths of the kit
  conform. The two NOT CHECKED rows are not re-run before the corpus replay
  ends: they are never reported as OK when they did not run.
- **Published**: `0172402` -> **`1716cca`**, fast-forward, no force, no amend
  after a push, no secret in the tree; checked **through the GitHub API
  without a token** (`commits/main` -> sha `1716cca3c2415bff112c82d5c84b739516a67453`,
  `contents/README.md` -> blob `b5ede5e9377011925af2fea34a7946045bd62b9d`,
  whose decoded content holds the corrected legend and no longer holds the
  false one).
- **The corpus replay is still running**: 1 927 pages and 0 error at 01:48,
  1,705 s per page since 00:54, which projects to about **1 h 37** for the
  3 426 pages -- faster than the "about 1 h 56" of the kit, which is a
  projection measured on the first 160 pages. **The exact number of pages is
  not known yet, so nothing was written in the kit or in the README.**
- **Two tasks are left for Jules**: re-read the README and the kit as a judge
  of the contest and list every claim that does not match the real output;
  check that every figure of the README, of the kit and of
  `VIDEO-YOUTUBE-QNX-PORTMAP.md` is the same in the three files.

## Progress of this cycle (18/11/2026, 02:00, the legend of the README and the legend of the kit can no longer drift apart)
- **The false legend is now guarded by a published test.** The README and the
  submission kit must describe the elided lines in the same words; the
  published test `test_readme_and_kit_show_the_same_quick_output` now
  compares the two legends character by character, and fails when they
  differ. The counter-proof was played on a copy of the tree: a README whose
  legend says "one line per symbol" again makes the test fail, with the two
  texts side by side. **No published figure moves**: the assertion was added
  to an existing test, so the suite still answers **202 tests, 33 skipped**.
- **The two legends are identical, and it is now proved on every run.** The
  legend of the README (line 77) and the legend of the kit (line 270) are the
  same text, with the same line break: "(one status line and one note line per
  symbol; the page, / citation and detail lines are elided here, like in the
  full-mode output below):". The only difference is the lead-in of the
  sentence, and it is on another line ("Real output of the quick mode", line
  76), which no order allows to touch.
- **The two tasks for Jules pointed at a folder that does not exist.** The
  first field of a task is the working folder: it must exist in `/work` and
  hold a `LISEZMOI.md`. The tasks written this morning pointed at
  `qnx-qx-portmap`, the name of the repository on GitHub, which is not a
  folder here: the pump would have counted them as "dossier absent", like it
  did on 14 November. They now point at `qnx-portmap`, the real folder, which
  holds a `LISEZMOI.md`.
- **Checks of this cycle**: `python3 -B tools/controle_placeholders.py` -> OK,
  70 documents, no placeholder; `bash scripts/verify-all.sh` -> **RC 0**,
  **6/8 OK and 2 NOT CHECKED** (the anti-leak control and the parity of the
  README block, which need the corpus: the replay is still running), the unit
  test suite **202 tests, 33 skipped**, the RED counter-proof **10/10**, the
  lengths of the kit conform, the manifest **126 files**.
- **The corpus replay is still running**: **2 292 pages and 0 error** at
  02:00:38, **1,740 s per page** since 00:54:09, which projects to about
  **1 h 40** for the 3 426 pages -- the rate of the README, and faster than
  the "about 1 h 56" of the kit, which is a projection measured on the first
  160 pages. **The exact number of pages is not known yet, so nothing was
  written in the kit or in the README.**

## Progress of this cycle (18/11/2026, 02:12, the coherence check replayed on a clean tree, the corpus replay still running)
- **The coherence check was replayed from a clean tree**: `python3 -B tools/controle_placeholders.py` -> OK, 70 documents, no placeholder; `bash scripts/verify-all.sh` -> **RC 0**, **6/8 OK and 2 NOT CHECKED**, the unit test suite **202 tests, 33 skipped**, the published manifest **126 files**, the RED counter-proof **10/10**, the lengths of the kit conform. The two NOT CHECKED rows are the anti-leak control and the parity of the README block: both need the frozen corpus, and the judge replay that rebuilds it is still running. A check that did not run is never reported as OK.
- **The published block of the README is still the real output**: the fenced block that follows "Real output, on a fresh clone without the corpus:" is byte-identical to the output of `bash scripts/verify-all.sh` on this machine. The comparison was made without touching the file, so the fixed point was not disturbed.
- **The corpus replay is still running**: **2,609 pages and 0 error** at 02:11:09, **1,771 ms per page** since 00:54:09, which projects to about **1 h 41** for the 3,426 pages -- the rate of the README, and faster than the "about 1 h 56" of the kit, which is a projection measured on the first 160 pages. **The exact number of pages is not known yet, so nothing was written in the kit or in the README.**

## Progress of this cycle (18/11/2026, 02:16, every figure of the three documents compared one by one)
- **The task given to Jules was done by the slot, because Jules has not answered yet.** Every figure quoted in README.md, in KIT-SOUMISSION-QNX.md and in VIDEO-YOUTUBE-QNX-PORTMAP.md was compared one by one. The three documents agree on the figures that matter: 202 tests and 33 skipped, 3,426 pages of corpus, 76 pages for the quick mode, the URL of the video and its duration (111.04 s, 1 min 51 s), the manifest of 126 files, the RED counter-proof 10/10, the rate of 96 % on a sample of 100 symbols.
- **Two figures of the video file were not dated, and are now.** That file is the plan of 15 November (160 s, 170 tests), then the filming of 16 November (111.04 s, 194 tests), then the publication of 17 November; the published suite answers 202 tests today. The plan is kept as it was written, but a status paragraph at the top of the file now says which figure belongs to which day, and the two rows of the filming table that quote a figure (the test suite, and the duration of the quick-mode run, 151.2 s on the filming machine) now name the day and the machine they come from. **No figure was changed**: the documents did not contradict each other, they were measuring three different days without saying so.

## Progress of this cycle (18/11/2026, 03:05, the complete judge replay is over: the exact number of pages is known)
- **The complete judge replay of the corpus ended at 02:57:42.** Exact figures, read from the download log of the replay: **3,973 pages, 0 failure**, from 00:54:09 to 02:57:42, so **7,413 s (2 h 03)**, **1.87 s per page** at one request per second, 399 Mo downloaded. The 8.0 books are the same as in the frozen snapshot (2,226 pages); the 7.1 C Library Reference now serves **1,747** pages against 1,200 in the snapshot of 14 November, and the 547 extra pages come from there.
- **The published budget was false, and is corrected.** The README, the kit and the codelab said "about 1 h 40 to 2 h"; the real download took 2 h 03. They now say **about two hours** and quote the measurement: 3,973 pages in 2 h 03, 1.87 s per page, 0 failure. The frozen snapshot used for the proofs still holds 3,426 pages, and the two figures now stand next to each other, with the reason (the live documentation serves more pages than the snapshot).
- **The rebuilt corpus was checked with the tool**: `qnx-portmap --verify-corpus` answers **pages checked: 3973, page SHA-256: OK, SHA256SUMS: OK (7948 files)**, exit code 0, and the three published answers (abort documented, accept described elsewhere, bzero absent) are the same with the 3,973-page corpus as with the frozen one. The replay directory was not modified (checked with `find -newer`).
- **A date the tool printed was false, and is fixed.** `tools/build_corpus.py` wrote the hardcoded date "2026-11-14" in the manifest of every corpus it built: the corpus rebuilt by the replay of 18 November said "consulted on 2026-11-14" although its pages were downloaded on 18 November. The date now comes from the download log of the build (the last page downloaded), and from the day of the build when there is no log. The frozen snapshot of the project is not touched: its own manifest keeps the date of 14 November, which is the date of its pages.
- **The two verifications that needed the corpus were relaunched.** The parity of the README block now runs against the frozen corpus: `tests.test_readme` answers OK (the block of the README is the real output of the tool). The anti-leak control was relaunched on the corpus of 14 November, in the background (it takes more than 25 minutes).
- **The same false budget was in two more published documents.** `docs/README-FR.md` (the French README) and `CORPUS-NON-PUBLIE.txt` (the notice that tells a reader how to rebuild the corpus) said the same "about 1 h 40 to 2 h"; they now say "about two hours" and quote the same measurement (3,973 pages in 2 h 03, 1.87 s per page, 0 failure). The only occurrences left in the public repository are in the dated log of the progression, where they are the historical record of what was believed at the time -- and where the entry of this cycle says they were false.

## Progress of this cycle (19/11/2026, 06:16, the removals announced by the official guide are in the tool)
- **The patch of the mother was applied cleanly** with `git am 0001-retraits-v2.patch` (21 415 o, md5 `a755171c2989494dea022facef0b6ad4`): no `git am` failure, no force/reset/rebase. New HEAD = `3413482` ("A function that the official migration guide says was removed is reported absent, priority 1, with the removal sentence quoted (itoa, _smalloc were 'described elsewhere', priority 3)"). 1 commit, 9 files: `classify.py`, `cli.py`, `quick.py`, `report.py`, `tests/test_fixtures.py`, `tests/test_frozen_corpus.py`, `tests/test_lang_en.py`, `tests/test_quick.py` and `MANIFESTE-PUBLIE.txt`. The patch file itself is kept outside the published tree (in `/work/preparation/patches/`), so that the public repository holds only the code.
- **The measurement was redone (J5, dated 19/11/2026)**: the expected result is there, exactly. `InterruptAttach` is now "non resolu : retire selon le guide" — status `absent`, priority 1, with the sentence of the guide quoted ("The following functions have been removed: InterruptAttach() InterruptAttachArray() InterruptHookIdle2() InterruptHookTrace()", page `kernel.html` of `com.qnx.doc.qnxsdp.migration`). The rate drops from 96 % to **95 %** (95 resolved and quoted, 5 not resolved: the four historical absents + InterruptAttach). `if_freenameindex` and `setsockopt` stay converted ("described elsewhere" in the io-sock guide). The sample is still **strictly identical to J4** ("identique a J4 : OUI"). J4 stays a dated measurement, not rewritten.
- **202 tests, all green** with and without the corpus: `python3 -B -m unittest discover -s tests -t .` -> `Ran 202 tests`, `OK (skipped=33)` without corpus, `OK (skipped=1)` with it. The 3 red tests the mother expected after the patch (test_mesure_j4 published statuses, test_mesure_j5 rate 95 instead of 96 + statuses) went green by moving the **published figures** (95 %, 2 conversions, InterruptAttach as a removal), never by weakening a test: `test_mesure_j4` now asserts exactly the one expected difference, `test_mesure_j5` asserts the removal, `test_quick` asserts `absent` is said only for the guide-announced removals.
- **The quick mode now says `absent` only when the guide announces the removal.** Real run, frozen corpus serving the pages, `python3 -m qnx_portmap --quick InterruptAttach itoa abort bzero`: InterruptAttach and itoa -> `absent` with the guide sentence quoted (kernel.html / c_apps.html), abort -> `documented`, bzero -> `unknown`. Log `/work/quick-retrait-demo-20261119.log`.
- **The documents were updated**: `README.md`, `docs/README-FR.md`, `docs/UTILISATION.md`, `docs/CODELAB-COMMUNITY-QNX.md`, `docs/CODELAB-FORUM-PROPOSITION.md`, `VIDEO-YOUTUBE-QNX-PORTMAP.md`, `scripts/video/record_demo.sh`, `qnx_portmap/quick.py` (docstring), `scripts/install-sdp8.sh` (message). The point highlighted everywhere: "in a real public repository, the tool finds a call to InterruptAttach(), removed in 8.0 according to the official guide". The demo captures stay valid (they show no rate figure and no quick-mode header).
- **A V3 kit was written** (`KIT-SOUMISSION-QNX-V3-20261119.md`, a NEW versioned file; the frozen V2 kit and the 15/11 kit are untouched) with the up-to-date figures (95 %, InterruptAttach "retiré selon le guide", the new point, the field lengths). It was passed through `verif-kit-devpost.py`: verdict **OK**, RC 0.
- **The proof (l) of the English report was regenerated**: it still said "96 % becomes 97 %" while the published figure is 95 %. It was redone by a script (`/work/preparation/regen_preuve_l.py`, outside the published tree) that really breaks `docs/mesure-J4.md` (93 % -> 94 %) and then `docs/mesure-J5.md` (95 % -> 96 %) in a copy, requires the tests to fail (RC 1 and RC 1), restores the files byte for byte (SHA-256 identical) and requires the green again (RC 0). The outputs in the file are the ones of that run.

## Progress of this cycle (19/11/2026, 08:30, the published kit is the version of 19 November 2026, corrected twice in prose)
- **The published kit is the version of 19 November 2026 that replaces the one of commit `2b0704f`.** It carries three corrections, all of them in the prose around the blocks to paste, never inside a block: the header now says the file was revised on 19 November 2026, the figures quoted by the demonstration video are dated (the video says 96 %, which was the published rate on 17 November 2026, the day it was published), and the two references to a path of the build environment are gone. The sentence that gives the source of the 1 200-character reference table is kept, because it is true and it is the only useful trace.
- **The 18 blocks to paste are byte-identical, character for character, to the ones of the version at `2b0704f`.** The script that builds the file refuses to write it if one of them moved, if one of the measured lengths changed, or if the reference to the internal path is still in it. The lengths measured by the repository (`python3 tools/mesure_kit.py --check`) are the same as before: 1 170 and 1 187 characters for the two description fields, 2 673 for the testing instructions, 1 176 for the bonus field, 2 959 for the QNX proof.
- **The header does not carry a version number any more.** It carried "Version 4", the number of the version published at `2b0704f`: that number would have been false in the file that replaces it. The header now names the publication date and the commit of the version it replaces (`2b0704f`), which stays in the history of the repository, next to the kit of 15 November 2026 (`1b46b69`).
- **The verifier of the kits is green on the published file**: 13 fields checked, 0 over the limit, 0 field not covered, 0 placeholder, 0 discrepancy, exit code 0. The counter-proof still bites: on a copy, with 40 characters added to the block of the "Description" field, the same verifier answers NON CONFORME (over the limit) and names the field, exit code 1.
- **Nothing else changed**: no line of the tool, no test, no corpus, no image. The published manifest is regenerated, as after every change of the published tree.

## Progress of this cycle (19/11/2026, 09:45, the published kit tells the truth about the corpus)
- **The two corpus paths that the published kit cited are not in the public repository.** The kit said that the corpus is read in `corpus/index/pages.jsonl` and checked against `corpus/SHA256SUMS`. The repository holds no `corpus/` directory at all: the QNX documentation is not redistributed with the repository (licence). The kit now says exactly that in the block of the QNX proof, gives the one command that rebuilds the corpus (`bash scripts/bootstrap_corpus.sh --out corpus-downloaded`, the command of the README, line 115) and the two exact paths of the built snapshot: `corpus-downloaded/index/pages.jsonl` (the index) and `corpus-downloaded/SHA256SUMS` (the fingerprints of the files). Both paths were checked on the local copy of the corpus, not assumed. The sentence about the verification is kept and made exact: `qnx-portmap --verify-corpus` compares the SHA-256 of every page with the index, so the quotation comes from the page it names.
- **The 18 blocks to paste keep their published lengths.** Seventeen of them are byte-identical, character for character, to the ones of the version at `2b0704f`. The block of the QNX proof (4_7) is the only one that changed, because the two false paths were inside it, and it keeps exactly its published length: 2 959 characters, the number the kit announces and the number the verifier re-measures. The script that builds the file refuses to write it if a block moves, if one of the six published lengths changes, or if a false path is still in it.
- **The verifier of the kits is green on the new file**: 13 fields checked, 0 over the limit, 0 field not covered, 0 placeholder, 0 discrepancy, exit code 0. The counter-proof still bites: on a copy, with 40 characters added to the block of the "Description" field, the same verifier answers NON CONFORME (over the limit) and names the field, exit code 1. The lengths measured by the repository (`python3 tools/mesure_kit.py --check`) are unchanged.
- **The audit of the paths cited by the kit**: 33 cited paths, 4 of them absent from the public tree, and none of them a false path of the repository any more. `image/png` is a MIME type, not a file. `verif-kit-devpost.py` is the verifier of the owner, which is not published. `corpus-downloaded/index/pages.jsonl` and `corpus-downloaded/SHA256SUMS` are the two files of the snapshot that the command of the kit builds, in a directory that is not in the repository by design.
- **Nothing else changed**: no line of the tool, no test, no corpus, no image. The published manifest is regenerated, as after every change of the published tree.

## Progress of this cycle (19/11/2026, 23:35, the codelab of the submission is published)
- **The codelab is written, checked and published.** `docs/codelab/QX-PORTMAP-CODELAB.md` (23 874 bytes, md5 `9749480b9c340e27833d1c89e7c02e20`) is in `main` since commit `a8ffb53`, followed by `79fa0f3`, `241f2e2` and `33acb70` (fast-forward, never an amend). The public URL is https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/codelab/QX-PORTMAP-CODELAB.md (measured from outside on 19/11 at 23:05: HTTP 200, the same bytes as the local file). The published manifest was regenerated (126 -> 127 files) and the README links the codelab.
- **The shape of the codelab**: nine steps (clone, `--help`, quick mode, a short download test, the complete snapshot, the full offline answer with the quotations, `--verify-corpus`, the extraction of the reader's own calls, the JSON of those calls), then "How to verify", "The traps" (four of them) and a one-sentence "Next step". Every step gives one command and one expected result.
- **The four traps are the ones a reader really meets**: the corpus is not redistributed (licence), `unknown` is not `absent`, the exit code 1 is an answer and not a failure, and the test suite needs 145 MB in `TMPDIR`.
- **The checker of the codelab is green** (86 controls, exit code 0) and two red counter-proofs bite (an invented path, a broken structure). The kit, the blocks to paste, the four gallery images and the verification script were not touched.

## Progress of this cycle (20/11/2026, 00:50, the codelab is replayed by a reader, and three of its measured outputs were wrong)
- **The codelab is now replayed end to end by a script that plays the reader** (`/work/candidat-028-codelab/rejouer-codelab.py`, outside the published tree): it clones the public repository, runs the nine commands of the codelab as they are written, compares every output with the announced block, then runs the three commands of the "How to verify" section. **13 controls**. The first replay found four real defects, all of them corrected in this cycle.
- **A published test only passed on the day it was written.** `tests/test_mesure_j5.py` compared the published English measurement report with the output of the tool, byte for byte, but the tool stamps the day of the run in the report: the suite was green on 19/11 and **red in a fresh clone on 20/11** (1 failure, 33 skipped) and `verify-all.sh` then answered `FAILED AND NOT CHECKED - 2 check(s) FAILED`. The test now pins the date of the published report before regenerating it (commit `82b26a6`): the suite is green again (202 tests, 33 skipped) and the verdict is `6/8 OK, 2 NOT CHECKED` on any day. **The published report was not rewritten.**
- **Three expected outputs of the codelab were not the measured ones.** (a) The JSON of step 9 was an older output: it was missing `citation_kind`, `see_urls`, `mentioned_in_migration_guide`, `migration_urls`, `detail` and `note`, and it gave the kind `function` for `bzero` and `f`, which the tool answers with an empty kind. The block is now the output measured on 20/11. (b) Step 7 announced `SHA256SUMS: OK (<N>+1 files)`, a placeholder that was never substituted: it now says `<M>` and explains that `<M>` is 3 427 for the frozen snapshot and 7 948 for a snapshot rebuilt in step 5 (the two measured values). (c) The "How to verify" section did not say what the reader sees after the steps: the tree is then dirty and the measured verdict is `VERDICT: FAILED AND NOT CHECKED - 1 check(s) FAILED and 4 check(s) could not run out of 8 (RC 1)`, the failing row being the published manifest. The section now says it, and says that the command is meant to be run on a fresh clone.
- **A trap was half-written**: the script never overwrites a frozen corpus, and the first replay hit the refusal (`bootstrap_corpus: refus : /tmp/essai contient deja un corpus fige`). The first trap now says it, with the exact message.
- **A number of the README was wrong**: the published transcript of `verify-all.sh` said `nothing left in the 70 published documents`, the real count is **71** (the codelab added one). The README is corrected; the published transcript is now byte-identical to the real output.
- **Nothing else changed**: no line of the tool, no corpus, no image, and the kit, the blocks to paste and the verification script were not touched. The published manifest is regenerated, as after every change of the published tree.

## Progress of this cycle (22/11/2026, 06:45, the hostile audit of the PORTMAP half found 6 false lines, they are corrected, and the licence is now detected as MIT)
- **A hostile audit checked the 149 assertions of the PORTMAP half of the submission kit one by one**: 138 were measured true, **6 were false**, and 5 are dated measurements that cannot be replayed. The 6 false lines had 5 distinct causes: two stale numbers (`3 722` -> `3 843` characters, `1 min 52 s` -> `1 min 51 s`), one number the repository does not carry (`149.1 s` -> `151.2 s`, the duration the repository documents for that replay), two wrong date attributions (the kit of 15 November is not the one of 12 263 characters: that one is the kit of 18 November, at commit `1b46b69`), and one licence answer.
- **The licence sentence was false for a reason that was measured, not guessed.** The kit says the repository "contains an MIT licence file (LICENSE) at the top of the repository page", and the rules of the contest ask for a licence "detectable and visible at the top of the repository page". The file `LICENSE` did start with the MIT text, but the API answered `license.spdx_id = NOASSERTION` and `name = "Other"`: 9 French lines had been added after the MIT text, and a second unknown licence file (`LICENCE-DOCS-QNX.md`) sat at the root of the repository. The file is now the MIT text alone (21 lines), the second file is renamed `NOTICES-DOCS-QNX.md` (same name length, the 36 mentions updated), and the published manifest is regenerated (127 files).
- **The proof after the push**: `GET https://api.github.com/repos/tgg49099-dotcom/qnx-qx-portmap` answers `license.spdx_id = "MIT"` and `license.name = "MIT License"`. The sentence of the kit was not rewritten: it became true because the repository was corrected, and that is what the judge reads.
- **Two commits, nothing else**: `4a4ebcc` ("licence MIT detectable + 5 corrections audit hostile") and `7af8943` ("la duree de la video est 1 min 51 s dans tous les documents"). The 5 wrong texts now have 0 occurrence in the public tree (128 files) and `NOTICES-DOCS-QNX.md` appears 36 times.

## Progress of this cycle (22/11/2026, 10:30, the published tree is verified end to end with the frozen corpus (8/8), and the codelab is replayed by a judge)
- **The verdict of the previous cycle was provisional, and it is now complete.** The cycle of 06:45 concluded that the QNX corpus was not on the machine and published `6/8 OK, 2 NOT CHECKED`. The corpus **is** on the machine (`/work/qnx-portmap-corpus-local/corpus`, 3 430 files, 50 Mo, SHA-256 fingerprints intact), but `scripts/verify-all.sh` only looks for it in `$ROOT/corpus` or through `QX_PORTMAP_CORPUS`. Pointed at it, the 2 checks that could not run do run: on a fresh public clone (`main = 7af8943`), 22/11 07:56-08:30, `VERDICT: EVERY CHECK PASSED - 8/8 OK (RC 0)`: unit test suite OK (202 tests), anti-leak control of the corpus OK (0 match with the QNX documentation), published manifest OK (127 files), published numbers of the README OK, parity of the README output block OK (the README shows the real output), RED counter-proof OK, lengths of the submission kit OK, placeholders and draft banners OK (71 published documents).
- **The three configurations published by the kit are all re-measured**: corpus next to the package -> `Ran 202 tests in 32.903s` / `OK` (0 skipped); corpus through `QX_PORTMAP_CORPUS` -> `OK (skipped=1)`; no corpus -> `Ran 202 tests in 1.004s` / `OK (skipped=33)`. The red counter-proof gives 11 / 11 with the corpus. The "0.98 s" of the Devpost field P1 replays to 1.004 s here.
- **A trap worth publishing**: the corpus must never be copied **into** the tree. The anti-leak control scans the whole tree and then answers `FAILED` on a repository that contains no QNX page at all. The reference corpus stays outside the tree.
- **The codelab is replayed by a reader on the public tree, after the corrections**: the nine commands of the tutorial are executed as they are written and every announced output is compared with the measured one, then the three commands of the "How to verify" section are run. **13 controls, 13 OK** (the steps 1 to 9, the fresh-clone verdict `NO CHECK FAILED - 6/8 OK, 2 NOT CHECKED`, the suite `Ran 202 tests ... OK (skipped=33)`, the red counter-proof 10 / 10, and the verdict after the steps, which is the `FAILED AND NOT CHECKED - 1 check(s) FAILED` that the codelab announces for a dirty tree).
- **The figures the kit publishes about the media are still the figures of the published files**: the md5 of each of the four gallery images announced in the kit is the md5 of the file in the repository, and the video still lasts 111.04 s (1 min 51 s) and shows on screen `Ran 194 tests in 0.607s` / `OK (skipped=33)` - the two figures the video document dates to the filming day.
- **One stale promise is corrected in the codelab**: it announced a demonstration on a real QNX 8.0 target "to be confirmed on QNX 8.0 on 20 November 2026". That date has passed and the SDP 8.0 licence is still missing, so the codelab now says what is true: **not done as of 22 November 2026**. Nothing else of the codelab was touched, and the "Next step" is still one sentence.
- **The French log now carries the same sections as the English one.** The four English sections of 15/11 and 16/11 - the public repository in English, English as the default language of the console, the quick mode and the judge's first command, the run on a QNX 8.0 target prepared - had never been translated; they are now, and the two files carry the same sections in the same order. The check is mechanical: the sections are paired by date, then the figures, the identifiers and the file names of each pair are compared: 0 difference of facts on the 8 dates, the only differences being the French decimal comma.

## Progress of this cycle (22/11/2026, 19:05, the two dates of the table of the three configurations are corrected)
- **Two published sentences dated a measurement that does not match the figures they point to.** The README says "The three lines of the table above were re-measured on 15/11/2026" and the French README says the same with "le 16/11/2026". The table above them holds the figures of the current suite - 202 tests, and 0, 1 and 33 skipped - which were measured on 17 November 2026, the day the suite reached 202 tests, and re-measured on 22 November 2026, from 15:44 to 15:46 UTC, on three fresh clones of the published repository (`main = cbfe5e4`). On 15/11 the suite had 124 tests and 25 skipped, on 16/11 it had 184 tests and 32 skipped: neither sentence could describe the three lines it points to. Both say 22 November 2026 now, the date of the last measurement.
- **How the two false sentences appeared.** The English sentence was added in `7af8943` (22/11) carrying the date of the French one, which the same commit had just moved from 15/11 to 16/11, at the moment when the table was updated to the 202-test figures. The check that would have seen it compares the figures of a published sentence with the date it carries: `git log -S` on the sentence gives the date of every version of it, and the number of tests of the suite on that date is in the history.
- **Nothing else changed**: no line of the tool, no test, no corpus, no image. The kit, the blocks to paste and the verification script were not touched, and the 18 published lengths are unchanged. The published manifest is regenerated, as after every change of the published tree.

## Progress of this cycle (22/11/2026, 22:15, the two false claims of the published codelab are corrected)
- **Two sentences of the published codelab were false, and both are now corrected.** The first one said that a regenerated manifest lists "132 files instead of the 127 published ones": it is impossible, because `scripts/manifeste_publie.py` counts files and never a directory (it walks the tree with `os.walk` and reads `filenames`). Measured on 22 November 2026 in a fresh clone of the published commit `cbfe5e4`: **127 files** in the clean clone, **130** after the steps that leave `calls.txt`, `my_code.c` and `state.json` in the tree, **285** with the quick snapshot of step 3 (`corpus-quick/`, 155 files) and **8 235** with the complete snapshot of step 5 (`corpus-downloaded/`, 7 950 files). The codelab now gives these four numbers and says that a directory is never counted.
- **The second one dated a measurement with the wrong day.** The codelab dated the "27 pages in 51 seconds" of step 4 to 19 November 2026; the same measurement is dated 15 November 2026 by the README (`README.md:169` and `README.md:754`). The date is now 15 November 2026, in both places where the codelab gives it.
- **The other dates of the codelab were checked and left alone.** Six other occurrences of "19 November 2026" are in the codelab; `git log -S` shows that they were written on 19 November 2026 (`79fa0f3`, `241f2e2`) and they date other measurements (the quick mode, the full mode, the three lines of `calls.txt`, the test suite, the temporary directory). They are true and they still say the day they were measured.
- **A third false date was found in the README and in the French README.** They dated the table of the three configurations to 15/11/2026 and to 16/11/2026, but the table holds the figures of the current suite (202 tests, and 0, 1 and 33 skipped), measured on 22 November 2026 from 15:44 to 15:46 UTC on three fresh clones of the published repository. On 15 November the suite had 124 test methods and on 16 November 195: neither date could describe those three lines. Both sentences now say 22 November 2026.
- **Nothing else changed**: no line of the tool, no test, no corpus, no image, and the published kit (`KIT-SOUMISSION-QNX.md`) is not touched. The published manifest is regenerated, as after every change of the published tree.
