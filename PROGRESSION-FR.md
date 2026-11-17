# PROGRESSION — QX PORTMAP

Une ligne par fonction de l'outil : **nom**, ce qu'elle fait, son etat, le test qui le prouve.
Etat = `fait` (implemente et teste) / `partiel` (fait mais incomplet) / `prevu` (non fait).

Ce fichier est la carte de l'outil. Il est mis a jour a chaque cycle, avant le rapport.

---

## 1. Coeur de l'outil (`qnx_portmap/`)

| Fonction | Ce qu'elle fait | Etat | Test qui le prouve |
|---|---|---|---|
| `extract.strip_tags` | Retire le balisage HTML et decode les entites | fait | `tests/test_extract.py::TestStripTags::test_removes_markup_and_decodes_entities` |
| `extract.article_of` | Isole le `<article>` d'une page Oxygen (ignore la navigation) | fait | `tests/test_extract.py::TestArticle::test_keeps_only_article` |
| `extract.parse_index_page` | Lit l'index A-Z d'un livre : entrees de fonctions, variables et renvois "decrit ailleurs" | fait | `tests/test_extract.py::TestParseIndexPage::test_finds_function_entry` |
| `extract.parse_topic_page` | Lit une page de fonction : titre, `shortdesc`, section Description | fait | `tests/test_extract.py::TestParseTopicPage::test_description_is_the_description_section_not_the_library_one` |
| `extract.bold_identifiers` | Repere les identifiants cites en gras (renvois croises) | fait | `tests/test_extract.py::TestParseTopicPage::test_bold_text_is_kept` |
| `extract.sentences_with` | Trouve les phrases contenant un symbole, frontiere de mot respectee | fait | `tests/test_extract.py::TestSentencesWith::test_respects_word_boundaries` |
| `corpus.default_corpus_dir` | Trouve le corpus fige (variable d'environnement, puis depot) | fait | `tests/test_corpus.py::TestCorpusLocation::test_env_var_has_priority` |
| `corpus.Corpus.load` | Charge le manifeste et la liste des pages | fait | `tests/test_corpus.py::TestMiniCorpus::test_loads_pages_and_manifest` |
| `corpus.Corpus.find_url` | Retrouve une page a partir de son URL | fait | `tests/test_frozen_corpus.py::TestFrozenCorpus::test_documented_symbol` |
| `corpus.Corpus.html` / `.text` | Rend le HTML brut / le texte d'une page | fait | `tests/test_corpus.py::TestMiniCorpus::test_page_content_is_readable` |
| `corpus.Corpus.verify` | Verifie le SHA-256 de chaque page du corpus | fait | `tests/test_corpus.py::TestMiniCorpus::test_detects_a_corrupted_page` |
| `corpus.Corpus.verify_sha256sums` | Verifie le fichier `SHA256SUMS` du corpus | fait | `tests/test_corpus.py::TestMiniCorpus::test_detects_a_corrupted_sha256sums_file` |
| `corpus.read_symbols` | Lit une liste de symboles (lignes, virgules, commentaires) et deduplique | fait | `tests/test_corpus.py::TestReadSymbols::test_removes_duplicates` |
| `classify.Classifier.classify` | Classe une liste de symboles : `documented` / `described_elsewhere` / `absent` / `unknown`, avec page et citation | fait | `tests/test_classify.py::TestClassification::test_documented_symbol` |
| `classify.Classifier.worklist` | Liste de travail de mise a niveau, absences d'abord | fait | `tests/test_classify.py::TestClassification::test_worklist_lists_absent_before_described_elsewhere` |
| `classify.SymbolResult.to_dict` | Serialise un resultat (utilise par la sortie JSON) | fait | `tests/test_cli.py::TestCli::test_json_output` |
| `report.render_text` | Rendu texte pour le terminal | fait | `tests/test_cli.py::TestCli::test_text_output` |
| `report.render_json` | Rendu JSON (machine) | fait | `tests/test_cli.py::TestCli::test_json_output` |
| `report.render_markdown` | Rendu Markdown (collable dans une soumission) | fait | `tests/test_cli.py::TestCli::test_markdown_output` |
| `refresh.Downloader.fetch` | Telecharge une page QNX avec cache, delai et reprises | fait | `tests/test_fixtures.py::TestFixtureCorpus::test_integrity_is_ok` (chemin de construction du corpus) |
| `refresh.crawl_book` / `build_corpus_from_cache` | Reconstruit un corpus depuis qnx.com (reseau, jamais par defaut) | fait | `tests/test_cli.py::TestCli::test_verify_corpus_ok` (mode `--fresh` hors ligne par defaut) |
| `cli.main` | Point d'entree : symboles en arguments, `--file`, `--stdin`, `--format`, `--worklist`, `--verify-corpus`, `--stats`, `--fresh` | fait | `tests/test_cli.py::TestCli::test_input_from_file` |

## 2. Harnais de mesure (`tools/`)

| Fonction | Ce qu'elle fait | Etat | Test qui le prouve |
|---|---|---|---|
| `mesure_j4.scan_repo` | Extrait les symboles reellement appeles dans les `.c`/`.h` d'un depot clone | fait | `tests/test_mesure_j4.py::TestEchantillon::test_vingt_symboles_par_depot_et_cinq_depots` |
| `mesure_j4.select_sample` | Choisit 20 symboles par depot (100 distincts), famille QNX d'abord | fait | `tests/test_mesure_j4.py::TestEchantillon::test_cent_symbols_distincts` |
| `mesure_j4.etat` | Traduit un resultat de l'outil en l'un des 3 etats exclusifs | fait | `tests/test_mesure_j4.py::TestTauxCompteALaMain::test_les_etats_publies_des_dix_symboles_sont_bien_ceux_du_test` |
| `mesure_j4.taux` | Calcule le taux J4 (division par zero refusee) | fait | `tests/test_mesure_j4.py::TestTauxCompteALaMain::test_un_taux_sur_zero_leve_une_erreur` |
| `mesure_j4.measure` | Rejoue l'outil sur l'echantillon et collecte page, citation et SHA-256 | fait | `tests/test_mesure_j4.py::TestMesureReproductible::test_les_statuts_publies_sont_reproduits` |
| `mesure_j4.write_markdown` | Ecrit `docs/mesure-J4.md` (100 lignes, une par symbole) | fait | `tests/test_mesure_j4.py::TestTauxPublie::test_le_taux_du_markdown_vaut_le_taux_calcule` |
| `mesure_j4.write_citations` | Ecrit les 5 fichiers de citations (1 par depot, < 4 000 o de texte QNX) | fait | `tests/test_mesure_j4.py::TestTauxPublie::test_les_pages_de_citations_contenent_chaque_symbole_resolu` |
| `mesure_j4.write_public_json` | Ecrit le JSON public (sans le texte des citations, avec leur SHA-256) | fait | `tests/test_mesure_j4.py::TestEchantillon::test_chaque_symbole_resolu_a_une_page_et_une_citation` |
| `contre_epreuve.main` | Casse 11 regles une par une et exige que le test charge echoue | fait | `docs/preuves/c-contre-epreuve-rouge-sans-corpus.txt` (10/10) et `docs/preuves/b-tests-avec-corpus.txt` (11/11) |
| `controle_fuite_corpus.py` | Controle anti-fuite : aucune page QNX dans l'arbre publiable (7 controles) | fait | `docs/preuves/d-controle-fuite-corpus.txt` |
| `manifeste_publie.py` | Regenere `MANIFESTE-PUBLIE.txt` (fichiers et octets publies) | fait | `docs/preuves/f-manifeste-publie.txt` |
| `make_fixtures.py` | Fabrique les 12 extraits de test depuis le corpus | fait | `tests/test_fixtures.py::TestFixtureInvariants::test_every_excerpt_is_verbatim_and_not_empty` |
| `mesure_j5.resoudre_page` | Cherche la page exacte du livre QNX 8.0 qui decrit un symbole « decrit ailleurs » (verifiee dans le corpus fige) | fait | `tests/test_mesure_j5.py::TestMesureReproductible::test_les_pages_citees_sont_dans_le_corpus_fige_avec_le_bon_sha256` |
| `mesure_j5.etat_j5` | Etat J5 : « resolu et cite » des que la page QNX 8.0 qui decrit le symbole est verifiee | fait | `tests/test_mesure_j5.py::TestEchantillonJ5::test_le_taux_publie_est_96_pour_cent` |
| `mesure_j5.measure` / `.taux` / `.resume` | Rejoue la mesure J5 sur le meme echantillon que J4 et calcule le taux | fait | `tests/test_mesure_j5.py::TestMesureReproductible::test_le_taux_recalcule_vaut_le_taux_publie` |
| `mesure_j5.comparer_echantillons` | Verifie que l'echantillon rederive des 5 depots epingles est **strictement** celui de la mesure J4 | fait | `tests/test_mesure_j5.py::TestEchantillonJ5::test_echantillon_identique_a_j4` |
| `mesure_kit.py` | Recalcule la longueur de chaque bloc de `KIT-SOUMISSION-QNX.md`, la reecrit, et `--check` echoue si un chiffre publie est faux | fait | contre-epreuve : "138" -> "999" sur le bloc tagline = RC 1 ("2_2: file says 999, measured 138"), apres restauration RC 0 |
| `mesure_champs_devpost.py` | Mesure les longueurs reellement acceptees par Devpost, sur 120 pages de projets publiees (nom, description, tags, URL) | fait | `docs/preuves/j-mesure-champs-devpost.txt` (120 pages, resume + detail) |
| `table_mesure_devpost.py` | Transforme la mesure brute en une table de preuves ASCII, sans extrait de page | fait | `docs/preuves/j-mesure-champs-devpost.txt` (sortie ASCII verifiee par le script) |

## 3. Ce qui reste a faire (vu par la fiche, pas par moi)

| Fonction | Etat | Test qui le prouvera |
|---|---|---|
| J5 : etendre aux appels systeme (`user_guide`) | prevu | a ecrire |
| J6 : `verify-portmap.sh` de bout en bout sur une machine neuve | prevu | a ecrire |
| J7 : codelab de 30 minutes | prevu | a ecrire |

---

## Avance de ce cycle (14/11/2026)

**La mesure J4 (le critere d'arret chiffre de la fiche) est faite et verifiee : 93 % (93/100).**

Ce qui a ete construit et teste :

- `tools/mesure_j4.py` — le harnais de mesure : clone superficiel de 5 depots QNX publics, extraction
  des symboles reellement appeles, purge des definitions locales, filtre sur l'index QNX
  (8.0 ∪ 7.1), echantillon de 100 symboles distincts, classification, 3 etats, calcul du taux ;
- `tools/posix-base.txt` — 732 noms POSIX/C standard, ecrits a la main, **independants du corpus** :
  ils servent a separer la famille "standard" de la famille "QNX" et a ne pas favoriser l'outil ;
- `tests/test_mesure_j4.py` — 16 tests, dont le **contre-epreuve ROUGE** : le taux calcule par le
  script doit egaler le taux compte a la main sur 10 symboles donnes dans le test (70 % a la main) ;
- `docs/mesure-J4.md` + `docs/mesure-J4/` — les 100 symboles (nom, depot, etat, page, source,
  SHA-256), les 5 fichiers de citations, le JSON public ;
- `tools/contre_epreuve.py` — 11e contre-epreuve ajoutee : "le taux J4 ne compte que les symboles
  resolus et cites" ;
- `README.md` / `LISEZMOI.md` — chiffres remis a jour (106 tests, 11/11 contre-epreuves, J4 93 %) ;
- `/rapports/FICHE-QNX-2E-OUTIL.md` — section **2.8 ETAT REEL MESURE LE 14/11/2026** (taux, 5 URL +
  commits + dates, methode, decision).

Resultat : **J4 = 93 %**, seuil de 80 % franchi -> le critere d'arret de la section 2.6 de la fiche
n'est **pas** declenche, le plan B de 2.7 n'est pas declenche non plus. La decision de la suite
appartient a la mere ; **aucune fonction nouvelle n'a ete ajoutee ce cycle**.

## Suite

1. **Relecture hostile par Jules** (3 a 6 taches deposees dans `/work/jules-a-faire.txt`) : relecture
   du code, verification des chiffres du README contre le code, robustesse du script de mesure
   (division par zero, symbole vide, depot vide, doublon).
2. **J5** (dans la fiche) : etendre la classification aux appels systeme du `user_guide` — uniquement
   si la mere le demande ; le critere J5 de la fiche dit de reporter si le gain est faible.
3. Ne rien publier ni pousser sans validation : ni depot public, ni video, ni compte, ni soumission.

---

## Avance de ce cycle (14/11/2026, tranche J5 de la mere)

**Le taux de resolution passe de 93/100 a 96/100 sur le MEME echantillon**, et le
changement est prouve par un test ROUGE puis VERT.

Ce qui a ete construit et teste (rien dans `qnx_portmap/` n'a ete modifie) :

- `tools/mesure_j5.py` — le harnais de la mesure J5 : lit l'echantillon publie par la mesure J4,
  rejoue la classification sur le corpus fige, et pour un symbole « decrit ailleurs » cherche la
  **page exacte du livre QNX 8.0 qui le decrit** (candidates : les renvois de l'index 8.0, la page
  trouvee dans le corpus, les pages du guide de migration), la verifie dans le corpus fige et cite
  son empreinte SHA-256 ;
- `tests/test_mesure_j5.py` — 18 tests : l'echantillon J5 est **strictement** celui de J4 (memes
  100 symboles, meme ordre), le taux compte a la main sur 10 symboles vaut 90 %, seuls les 3
  symboles convertis ont change d'etat, chaque page citee est dans le corpus fige avec la bonne
  empreinte, et la citation publiee est bien extraite de la page citee ;
- `docs/mesure-J5.md` + `docs/mesure-J5/` — les 100 symboles, les 5 fichiers de citations, le
  JSON public ;
- `docs/preuves/h-mesure-j5-rouge.txt` — la preuve ROUGE -> VERT (sur l'etat d'avant : 10 echecs,
  RC 1 ; donnee publiee cassee : 9 echecs, RC 1 ; restauration : `Ran 18 tests ... OK`, RC 0) ;
- `scripts/controle_fuite_corpus.py` — les fichiers de citations de J5 sont desormais analyses
  fragment par fragment comme ceux de J4 ;
- `README.md` — chiffres remis a jour (124 tests, J5 = 96 %, J4 = 93 % date).

Resultat : **J5 = 96 % (96/100)** sur le meme echantillon que J4 (93 %). Les 3 conversions :

| symbole | avant (J4) | apres (J5) | livre QNX 8.0 cite |
|---|---|---|---|
| `InterruptAttach` | decrit ailleurs | resolu et cite | guide de migration, `kernel.html` |
| `if_freenameindex` | decrit ailleurs | resolu et cite | guide io-sock, `socket_api.html` |
| `setsockopt` | decrit ailleurs | resolu et cite | guide io-sock, `socket_api.html` |

Les 4 symboles absents de la 8.0 (`ND_NODE_CMP`, `pthread_sleepon_lock`,
`pthread_sleepon_unlock`, `fcfgopen`) **restent absents** : le plafond honnete du taux sur cet
echantillon est **96/100**. Aucune fonction nouvelle n'a ete ajoutee a l'outil ; le J5 de la fiche
(extension aux appels systeme) reste `prevu`, c'est une autre chose.

---

## Avance de ce cycle (15/11/2026, preparation de la soumission QNX)

**Le dossier de soumission existe** : le kit de formulaire Devpost, le plan de la video, et le
README public en anglais. **Aucune fonction nouvelle n'a ete ajoutee a `qnx_portmap/`** (moteur
gele, commit `395ffc2` inchange).

Ce qui a ete construit et verifie :

- `KIT-SOUMISSION-QNX.md` (30 060 octets) - le texte a coller dans le formulaire Devpost, bloc par
  bloc, dans l'ordre du formulaire, avec pour chaque bloc sa **longueur mesuree** et la limite du
  champ, avec sa source et sa date ; **aucune limite inventee** : ce que le formulaire QNX
  n'affiche pas (il est derriere une session : HTTP 302 / 401) est dit comme "non lu" ;
- `VIDEO-YOUTUBE-QNX-PORTMAP.md` (18 817 octets) - le plan minute par minute de la video (2 min 40),
  avec les commandes a l'ecran, le **voice-over en anglais**, et le **segment unique qui manque**
  (l'execution sur QNX 8.0 lui-meme), avec ce qu'il faut pour le produire ;
- `tools/mesure_kit.py` - le controleur : il recalcule chaque longueur du kit et **echoue** si un
  chiffre publie est faux (contre-epreuve faite : RC 1 quand on force "138" en "999") ;
- `tools/mesure_champs_devpost.py` + `tools/table_mesure_devpost.py` + `docs/preuves/j-mesure-champs-devpost.txt` -
  la mesure des longueurs reellement acceptees par la plateforme (120 pages de projets Devpost
  publies), qui donne la **borne inferieure** des limites non publiees ;
- `README.md` - section "Build and test (English)" (build, test, les 3 configurations de corpus),
  section "Honest limits (English)", liens vers le kit, le plan video et le codelab, chiffres
  corriges (l'option `--fresh --fresh-max-pages` n'existait pas ; les 27 pages du mode court sont
  mesurees en **51 s** le 15/11/2026) ;
- `docs/UTILISATION.md` et `docs/CODELAB-COMMUNITY-QNX.md` - meme correction de commande.

Resultat : **le dossier est soumettable**, sauf le segment video qui exige la licence SDP 8.0
(action du proprietaire). Le **controle anti-fuite** rejoue sur l'arbre complet (kit et plan video
compris) : **0 correspondance**, 6 037 octets de texte QNX verbatim, 0 fichier au-dessus du budget
de 4 000 octets (`docs/preuves/d-controle-fuite-corpus.txt`).

Points d'honnetete traites cette fois :

- la sortie console de l'outil est en **francais** alors que la regle l. 320 impose l'anglais :
  le kit et le plan video donnent la **table de traduction** des libelles ;
- le projet **n'a pas ete execute sur QNX 8.0** (licence SDP absente) : ni le kit, ni le README, ni
  la video ne pretendent le contraire ; la phrase qui le disait ("it also runs on QNX 8.0 itself")
  a ete corrigee en "designed to run on QNX 8.0 as well - this has not been demonstrated yet".

## Suite

1. Gestes du proprietaire : licence SDP 8.0 + execution reelle (segment video), video YouTube
   publique (08/12), codelab community.qnx.com (10/12), formulaire Devpost (13/12), miniature 3:2
   et 3 captures pour la galerie, depot public jusqu'au 29/01/2027.
2. Question a la mere : faut-il un mode de sortie **anglais** dans l'outil (changement du moteur,
   donc soumis au gel) ? Faut-il un README **integralement** en anglais ?
3. Ne rien faire sans instruction : nouvelle fonction du moteur, publication Devpost, video,
   compte, message a Tgg.

## Avance de ce cycle (16/11/2026, le controle cible mesure l'interpreteur, les images de la galerie sont pretes)

- **`scripts/qnx8_target_check.sh` mesure maintenant l'interpreteur** : une
  nouvelle ligne `compat` apparait juste apres la version de Python, et un
  troisieme code de sortie apparait dans le verdict (`compat exit code`).
  Elle repond a une question qui ne pouvait pas etre repondue avant la cible :
  *cet interpreteur est-il assez recent pour le paquet ?* Le seuil n'est pas
  suppose, il est mesure (voir le point suivant). Le controle passe toujours
  a la repetition, avec `/bin/sh` (dash) et avec `bash`, depuis la racine du
  depot et depuis un autre repertoire, et `--help` affiche maintenant tout
  l'en-tete du script.
- **La compatibilite du code cote cible est mesuree, pas supposee**
  (16/11/2026) : `vermin --no-parse-comments --target=3.13- --violations
  qnx_portmap/` donne "Minimum required versions: **3.4**" pour les 9 fichiers
  du paquet, donc le **Python 3.13.7** que le SDP 8.0.3 installe sur une
  cible lui suffit ; les modules importes par le paquet (`argparse`,
  `collections`, `gzip`, `hashlib`, `html`, `json`, `os`, `re`, `string`,
  `sys`, `time`, `urllib`) ne sont **aucun des modules supprimes en Python
  3.13** (PEP 594) et il n'y a aucune dependance tierce ; les deux scripts
  shell n'ont aucun bashisme. Sortie :
  `/work/preuves-qnx13/PROMESSE-PYTHON-CIBLE.txt`, et la sortie complete de
  la repetition dans `/work/preuves-qnx13/rehearsal-cible-16-11-2026.txt`
  (64 lignes).
- **`docs/QNX-8.0-CIBLE.md`** dit desormais cette mesure en section 1, cite
  le nouveau verdict en section 3, et montre la nouvelle ligne `compat` dans
  la sortie reelle de la section 5.
- **Les images de la galerie Devpost sont produites et verifiees**
  (16/11/2026) : une vignette 3:2 (1500x1000) et trois captures, toutes
  rendues a partir de sessions reellement enregistrees (`script -T`, rejouees
  par pyte), jamais retranscrites. La verification est independante du
  generateur : chaque ligne dessinee doit etre verbatim dans l'enregistrement,
  le PNG livre doit etre identique pixel par pixel a un re-rendu tire de
  l'enregistrement, PNG et moins de 5 Mo, la vignette exactement 3:2 ->
  `verify_galerie.py` sort avec 0 sur les quatre images.
- **Elles sont livrees, pas commitees** : les quatre PNG, les enregistrements,
  le generateur et le verificateur sont dans
  `/work/A_ENVOYER/DEVPOST-GALERIE/` avec un `LISEZ-MOI.txt` (quoi televerser
  ou, et ce que les images ne montrent pas). Elles ne sont **pas** dans le
  depot, parce que le kit de soumission dit qu'aucune miniature et aucune
  capture n'est encore commitee, et que le kit ne doit pas etre touche : les
  images sont televersees sur Devpost par le proprietaire.
- **Les limites honnete ne bougent pas** : le projet **n'a toujours pas ete
  execute sur une machine QNX 8.0**, et les images de la galerie montrent la
  sortie de l'outil sur l'hote, pas sur une cible. Les chiffres publies sont
  inchanges : **194 tests** (33 ignores sans le corpus), **117 fichiers** dans
  le manifeste publie.


## Progression de ce cycle (17/11/2026, le texte de soumission dit comment ce projet differe de notre autre entree)

- **La regle "Multiple Submissions" est desormais repondue dans le texte de soumission
  lui-meme.** Les regles du QNX Global Hackathon (`https://qnx.devpost.com/rules`, lues
  le 17 novembre 2026) disent qu'un entrant peut soumettre plusieurs projets, mais que
  chaque soumission doit etre unique et substantiellement differente des autres
  soumissions du meme entrant. Le recit de projet de `KIT-SOUMISSION-QNX.md` dit
  maintenant, dans le texte que l'entrant colle dans Devpost, en quoi QX PORTMAP
  differe de QX-PROBE : entree differente (les symboles QNX appeles par un arbre de
  sources contre le code C d'un resource manager), sortie differente (l'etat de la
  documentation contre les portes d'acces et les tables de dispatch), utilisateur
  different, et aucun code, aucune regle et aucun document partage.
- **Les chiffres publies sont maintenant 200 tests** (33 ignores sans le corpus, code
  de sortie 0, mesures le 17 novembre 2026) et **118 fichiers** dans le manifeste
  publie. Les chiffres de l'entree precedente (194 tests, 117 fichiers) sont ceux du
  16 novembre 2026 : ce fichier est un journal date, ils ne sont donc pas reecrits.
- **Controles de ce cycle** : `python3 -m unittest discover -s tests -t .` -> 200
  tests, OK, 33 ignores ; `python3 -I tools/mesure_kit.py --check` -> OK, 14 blocs,
  tagline 138/140, tags 11/25 ; `bash scripts/verify-all.sh` -> aucun controle en
  echec (4/7 OK, 3 non verifiables sur cette machine, le corpus fige est absent).
