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

## Progression de ce cycle (17/11/2026, la video est publiee et son URL est dans le kit)

- **La video de demonstration est publiee et publique** sur YouTube depuis le
  17/11/2026 : `https://youtu.be/UMmxNlxkEi0` - identifiant `UMmxNlxkEi0`,
  titre "QX PORTMAP - is every QNX symbol your code calls still documented in
  QNX 8.0 ?", chaine "Tgg Labs", **1 min 51 s** (111,04 s, mesure sur le
  fichier par le Studio le 17/11/2026), donc sous les trois minutes demandees
  par le reglement. Verifie depuis l'exterieur de l'environnement de build le
  17/11/2026 : HTTP 200 sur l'oEmbed YouTube de cette URL, avec ce titre et
  cette chaine.
- **L'URL est dans le kit de soumission** : le bloc 4.5 de
  `KIT-SOUMISSION-QNX.md` porte maintenant `https://youtu.be/UMmxNlxkEi0` et sa
  longueur reelle mesuree (28 caracteres). Le paragraphe qui disait "the
  placeholder is deliberate: no video is published yet" est remplace par les
  faits ci-dessus et par ce que la video montre : l'outil en fonctionnement dans
  un vrai terminal (le mode rapide contre la documentation QNX officielle, l'etat
  de chaque symbole avec la page officielle et la citation exacte, la sortie
  JSON, la liste de travail, la suite de tests).
- **Plus aucun placeholder dans les documents publies** (nouveau controle,
  verification 8 de `scripts/verify-all.sh`) :
  `tools/controle_placeholders.py` cherche les trois marqueurs de placeholder
  de ce projet (le marqueur d'un champ a remplir, le marqueur d'un texte a
  completer, et le marqueur de longueur du kit) dans les 69 documents
  publies, et verifie que l'URL de la video de demonstration est la meme dans
  le README et dans le kit.
  Il **echoue sur l'etat d'avant ce cycle** (les trois placeholders de l'arbre
  du 17/11, code de sortie 1) et **passe apres** (code de sortie 0). Le champ
  codelab (bloc 4.8 du kit) est maintenant **vide** : le codelab n'est pas
  publie sur community.qnx.com, il n'y a donc aucune URL a donner, et la note
  dit quoi faire s'il passe en ligne avant la date limite.
- **La vignette de la galerie est desormais committee et publique** : la
  section 3.3 du kit donne l'URL publique de
  `media/qx-portmap-demo-thumbnail.png` (PNG, 172 092 octets, 1280 x 720),
  verifiee HTTP 200 depuis l'exterieur de l'environnement de build le
  17/11/2026. La section disait avant qu'aucune miniature n'etait committee :
  c'etait vrai quand elle a ete ecrite et c'est faux maintenant.
- **Les chiffres publies sont toujours 200 tests** (33 ignores sans le corpus,
  code de sortie 0, mesures le 17 novembre 2026) et **119 fichiers** dans le
  manifeste publie (le controle des placeholders est le 119e fichier). Le
  chiffre de l'entree precedente (118 fichiers) est celui du cycle precedent :
  ce fichier est un journal date, il n'est donc pas reecrit.
- **Controles de ce cycle** : `python3 -m unittest discover -s tests -t .` -> 200
  tests, OK, 33 ignores ; `python3 -I tools/mesure_kit.py --check` -> OK, 14
  blocs, tagline 138/140, tags 11/25, URL de la video 28 caracteres, codelab 0
  caractere ; `python3 -I tools/controle_placeholders.py` -> OK, 69 documents,
  aucun placeholder ; `bash scripts/verify-all.sh` -> aucun controle en echec
  (6/8 OK, 2 non verifiables sur cette machine, le corpus fige est absent).

## Progression de ce cycle (17/11/2026, un chemin rapide dans le codelab, un telechargement qui survit a une page coupee, et les chiffres du tutoriel sont ceux mesures)

- **Une page coupee par le reseau n'arrete plus le telechargement du
  corpus.** `qnx_portmap/refresh.py` attrape maintenant
  `http.client.HTTPException` (`IncompleteRead`) et la retente comme une
  erreur reseau ; avant, une seule page coupee au milieu arretait tout le
  telechargement avec une trace (mesure le 17/11/2026, page 1545 sur 3426).
  Deux tests ont ete ajoutes (`tests/test_download_retry.py`), et la
  **contre-epreuve ROUGE a ete verifiee a la main** sur une copie
  temporaire : avec l'ancien `refresh.py` les deux tests finissent en
  `ERROR` (`IncompleteRead` non rattrapee), avec le nouveau ils passent.
- **Le codelab a un « chemin de 2 minutes »** : le mode rapide telecharge
  les 26 index A-Z de 8.0 et de 7.1, le guide de migration et la page de
  chaque symbole documente (76 pages) et repond tout de suite. Sa sortie
  reelle et sa duree reelle sont dans le tutoriel, et son code de sortie
  (`1`, parce que deux symboles restent `unknown`) est explique : un juge
  qui lance la commande ne doit pas lire `1` comme un echec.
- **Les chiffres du tutoriel sont ceux qu'on a mesures.** Le mode rapide a
  ete lance pour de vrai le 17/11/2026 : 76 pages en **143,7 s**, duree que
  l'ecrit lui-meme dans `corpus-quick/MANIFEST.json` (`quick.seconds`). Les
  quatre mesures archivees sont 127 s et 144 s (16/11), 94 s et 151 s
  (17/11) : le tutoriel dit desormais « about two to three minutes » et les
  donne, comme le README et le kit. Le telechargement complet garde le
  budget publie (« about 1 h 40 to 2 h », 1,7 a 2 s par page).
- **L'etape 6 ne garde que les appels.** L'extraction des symboles de votre
  propre code ne garde plus que les mots suivis de `(` et retire les mots
  cles du C ; le tutoriel montre le fichier de 2 lignes qu'il compte
  (8 « symboles » et 6 `unknown` sans le filtre, 3 appels avec) et la
  reponse que l'outil donne vraiment (`abort` documented, `bzero` absent,
  `f` unknown).
- **La capture de la galerie qui montre la suite de tests a ete refilmee** :
  elle affichait encore « Ran 200 tests » alors que tous les documents
  publies disaient 202. C'est un vrai enregistrement (`script -T`, rejeu par
  pyte) : elle a ete refilmee, pas retouchee ; la nouvelle capture montre
  « Ran 202 tests in 1.130s » et « OK (skipped=33) », et `verify_galerie.py`
  controle que le PNG publie est le re-rendu pixel par pixel de
  l'enregistrement. Les trois autres images sont identiques octet pour
  octet. Deux chiffres du kit suivent l'image (sa taille et la legende de la
  section 4.4) ; rien d'autre du kit n'a ete touche.
- **Les chiffres publies sont maintenant 202 tests** (33 ignores sans le
  corpus, code de sortie 0, mesures le 17 novembre 2026) et **125 fichiers**
  dans le manifeste publie. Le chiffre de l'entree precedente (200 tests,
  124 fichiers) est celui du cycle precedent : ce fichier est un journal
  date, il n'est donc pas reecrit.
- **Controles de ce cycle** : `python3 -m unittest discover -s tests -t .` ->
  202 tests, OK, 33 ignores (et OK, 1 ignore, avec le corpus fige pointe par
  `QX_PORTMAP_CORPUS`) ; `bash scripts/verify-all.sh` -> aucun controle en
  echec (6/8 OK, 2 non verifiables sur cette machine, le corpus fige est
  absent de l'arbre, RC 0), la contre-epreuve ROUGE du depot est 10/10 ;
  `python3 -I tools/mesure_kit.py --check` -> OK ;
  `python3 -I tools/controle_placeholders.py` -> OK, 70 documents, aucun
  placeholder.

## Progression de ce cycle (18/11/2026, le kit rejoue en juge, et la legende du README corrigee)
- **Le kit a ete rejoue, pas relu.** Clone neuf (`/tmp/juge`), environnement
  virtuel neuf, `pip install .`, puis **toutes les commandes du kit, dans
  l'ordre du kit** : pour chaque affirmation, la sortie reelle, la duree
  reelle et le code de sortie reel. **63 affirmations verifiees, 1 fausse** :
  la legende du mode rapide annoncait « one line per symbol », alors que le
  programme affiche six lignes par symbole (statut, page, citation, detail,
  note) et que le bloc publie n'en montre que deux, les trois du milieu etant
  elidees. La legende du kit dit maintenant ce qui est elide : « one status
  line and one note line per symbol; the page, citation and detail lines are
  elided here, like in the full-mode output below ». Deux chiffres ont ete
  ajoutes sur la meme mesure : le mode rapide a pris **149,1 s** dans ce
  replay, et le corpus complet tourne a **2,03 s par page** sur ses 160
  premieres pages, ce qui projette environ 1 h 56 pour les 3 426 pages. Le
  tableau complet des 63 affirmations est dans
  `/work/NOTES-KIT-JUGE-20261118.md`.
- **La meme phrase fausse etait dans `README.md` ligne 77.** Elle est
  corrigee et publiee : la legende du README est celle du kit, **mot pour
  mot**, avec la meme coupure de ligne. Un programme compare les deux
  parenthèses et repond `True` ; « one line per symbol » et « header elided »
  ont disparu du README. **Aucune autre ligne du README n'a ete touchee.**
- **Le manifeste publie hache le README.** Le premier `verify-all.sh` apres
  la correction a repondu **RC 1**, sur deux lignes qui ne sont pas des bugs :
  `published manifest FAILED` (« MANIFESTE-PUBLIE.txt est obsolete :
  regenerez-le. ») et `RED counter-proof NOT CHECKED` (« the working copy is
  not clean »). Il fallait regenerer le manifeste
  (`python3 -B scripts/manifeste_publie.py`, **126 fichiers**) et commiter
  **avant** la verification. L'ordre qui marche est desormais : editer,
  regenerer le manifeste, commiter, verifier, pousser.
- **Controles de ce cycle** : `python3 -B tools/controle_placeholders.py` ->
  OK, 70 documents, aucun placeholder ; `bash scripts/verify-all.sh` ->
  **RC 0**, **6/8 OK et 2 NOT CHECKED** (le controle anti-fuite et la parite
  du bloc README, qui ont besoin du corpus), la suite **202 tests, 33
  ignores**, la contre-epreuve ROUGE **10/10**, les longueurs du kit
  conformes. Les deux lignes NOT CHECKED ne sont pas relancees avant la fin
  du rejeu du corpus : un controle qui n'a pas tourne n'est jamais compte
  comme OK.
- **Publie** : `0172402` -> **`1716cca`**, fast-forward, 0 --force, 0 amend
  apres un push, 0 secret dans l'arbre ; verifie **par l'API GitHub sans
  jeton** (`commits/main` -> sha
  `1716cca3c2415bff112c82d5c84b739516a67453`, `contents/README.md` -> blob
  `b5ede5e9377011925af2fea34a7946045bd62b9d`, dont le contenu decode contient
  la legende corrigee et ne contient plus la phrase fausse).
- **Le rejeu du corpus tourne encore** : 1 927 pages et 0 erreur a 01:48,
  1,705 s par page depuis 00:54, soit une projection d'environ **1 h 37**
  pour les 3 426 pages, plus rapide que le « about 1 h 56 » du kit, qui est
  une projection mesuree sur les 160 premieres pages. **Le nombre exact de
  pages n'est pas encore connu : rien n'a ete ecrit dans le kit ni dans le
  README.**
- **Deux taches restent pour Jules** : relire le README et le kit comme un
  juge de concours et lister chaque affirmation qui ne correspond pas a la
  sortie reelle du programme ; verifier que chaque chiffre du README, du kit
  et de `VIDEO-YOUTUBE-QNX-PORTMAP.md` est identique dans les trois fichiers.

## Progression de ce cycle (18/11/2026, 02:00, la legende du README et celle du kit ne peuvent plus diverger)
- **La legende fausse est desormais gardee par un test publie.** Le README et
  le kit de soumission doivent decrire les lignes elidees avec les memes
  mots ; le test publie `test_readme_and_kit_show_the_same_quick_output`
  compare maintenant les deux legendes caractere par caractere, et echoue
  des qu'elles different. La contre-epreuve a ete jouee sur une copie de
  l'arbre : un README dont la legende dit a nouveau "one line per symbol"
  fait echouer le test, avec les deux textes l'un a cote de l'autre.
  **Aucun chiffre publie ne bouge** : l'assertion a ete ajoutee a un test
  existant, la suite repond donc toujours **202 tests, 33 ignores**.
- **Les deux legendes sont identiques, et c'est desormais prouve a chaque
  run.** La legende du README (ligne 77) et celle du kit (ligne 270) sont le
  meme texte, avec la meme coupure de ligne : "(one status line and one note
  line per symbol; the page, / citation and detail lines are elided here,
  like in the full-mode output below):". La seule difference est le debut de
  la phrase, qui est sur une autre ligne ("Real output of the quick mode",
  ligne 76), qu'aucune consigne n'autorise a toucher.
- **Les deux taches pour Jules pointaient vers un dossier qui n'existe
  pas.** Le premier champ d'une tache est le dossier de travail : il doit
  exister dans `/work` et contenir un `LISEZMOI.md`. Les taches ecrites ce
  matin pointaient vers `qnx-qx-portmap`, le nom du depot sur GitHub, qui
  n'est pas un dossier ici : la pompe les aurait comptees "dossier absent",
  comme le 14 novembre. Elles pointent maintenant vers `qnx-portmap`, le
  vrai dossier, qui contient un `LISEZMOI.md`.
- **Controles de ce cycle** : `python3 -B tools/controle_placeholders.py` ->
  OK, 70 documents, aucun placeholder ; `bash scripts/verify-all.sh` ->
  **RC 0**, **6/8 OK et 2 NOT CHECKED** (le controle anti-fuite et la parite
  du bloc README, qui ont besoin du corpus : le rejeu tourne encore), la
  suite **202 tests, 33 ignores**, la contre-epreuve ROUGE **10/10**, les
  longueurs du kit conformes, le manifeste **126 fichiers**.
- **Le rejeu du corpus tourne encore** : **2 292 pages et 0 erreur** a
  02:00:38, **1,740 s par page** depuis 00:54:09, soit une projection
  d'environ **1 h 40** pour les 3 426 pages -- le rythme du README, et plus
  rapide que le « about 1 h 56 » du kit, qui est une projection mesuree sur
  les 160 premieres pages. **Le nombre exact de pages n'est pas encore
  connu : rien n'a ete ecrit dans le kit ni dans le README.**

## Progression de ce cycle (18/11/2026, 02:12, le controle de coherence rejoue sur un arbre propre, le rejeu du corpus tourne encore)
- **Le controle de coherence a ete rejoue sur un arbre propre** : `python3 -B tools/controle_placeholders.py` -> OK, 70 documents, aucun placeholder ; `bash scripts/verify-all.sh` -> **RC 0**, **6/8 OK et 2 NOT CHECKED**, la suite **202 tests, 33 ignores**, le manifeste **126 fichiers**, la contre-epreuve ROUGE **10/10**, les longueurs du kit conformes. Les deux lignes NOT CHECKED sont le controle anti-fuite et la parite du bloc README : les deux ont besoin du corpus fige, et le rejeu de juge qui le reconstruit tourne encore. Un controle qui n'a pas tourne n'est jamais rapporte comme OK.
- **Le bloc publie du README est toujours la sortie reelle** : le bloc delimite qui suit "Real output, on a fresh clone without the corpus:" est identique octet pour octet a la sortie de `bash scripts/verify-all.sh` sur cette machine. La comparaison a ete faite sans toucher au fichier, donc le point fixe n'a pas ete derange.
- **Le rejeu du corpus tourne encore** : **2 609 pages et 0 erreur** a 02:11:09, **1 771 ms par page** depuis 00:54:09, soit une projection d'environ **1 h 41** pour les 3 426 pages -- le rythme du README, et plus rapide que le « about 1 h 56 » du kit, qui est une projection mesuree sur les 160 premieres pages. **Le nombre exact de pages n'est pas encore connu : rien n'a ete ecrit dans le kit ni dans le README.**

## Progression de ce cycle (18/11/2026, 02:16, chaque chiffre des trois documents compare un par un)
- **La tache donnee a Jules a ete faite par le slot, Jules n'ayant pas encore repondu.** Chaque chiffre cite dans README.md, dans KIT-SOUMISSION-QNX.md et dans VIDEO-YOUTUBE-QNX-PORTMAP.md a ete compare un par un. Les trois documents concordent sur les chiffres qui comptent : 202 tests et 33 ignores, 3 426 pages de corpus, 76 pages pour le mode rapide, l'URL de la video et sa duree (111,04 s, 1 min 51 s), le manifeste de 126 fichiers, la contre-epreuve ROUGE 10/10, le taux de 96 % sur un echantillon de 100 symboles.
- **Deux chiffres du fichier video n'etaient pas dates, ils le sont maintenant.** Ce fichier est le plan du 15 novembre (160 s, 170 tests), puis le tournage du 16 novembre (111,04 s, 194 tests), puis la publication du 17 novembre ; la suite publiee repond aujourd'hui 202 tests. Le plan est garde tel qu'il a ete ecrit, mais un paragraphe d'etat, en tete du fichier, dit desormais a quel jour chaque chiffre appartient, et les deux lignes du tableau du tournage qui citent un chiffre (la suite de tests, et la duree du mode rapide, 151,2 s sur la machine de tournage) nomment maintenant le jour et la machine dont ils viennent. **Aucun chiffre n'a ete change** : les documents ne se contredisaient pas, ils mesuraient trois jours differents sans le dire.

## Progression de ce cycle (18/11/2026, 03:05, le rejeu complet du corpus est fini : le nombre exact de pages est connu)
- **Le rejeu complet du corpus s'est termine a 02:57:42.** Chiffres exacts, lus dans le journal du rejeu : **3 973 pages, 0 echec**, de 00:54:09 a 02:57:42, soit **7 413 s (2 h 03)**, **1,87 s par page** a une requete par seconde, 399 Mo telecharges. Les livres 8.0 sont les memes que dans le corpus fige (2 226 pages) ; la C Library Reference 7.1 sert maintenant **1 747** pages contre 1 200 dans l'instantane du 14 novembre : les 547 pages de plus viennent de la.
- **Le budget publie etait faux, il est corrige.** Le README, le kit et le codelab disaient « about 1 h 40 to 2 h » ; le telechargement reel a pris 2 h 03. Ils disent maintenant **about two hours** et citent la mesure : 3 973 pages en 2 h 03, 1,87 s par page, 0 echec. Le corpus fige utilise pour les preuves contient toujours 3 426 pages, et les deux chiffres sont desormais cote a cote, avec la raison (la documentation en ligne sert plus de pages que l'instantane).
- **Le corpus reconstruit a ete verifie par l'outil** : `qnx-portmap --verify-corpus` repond **pages checked: 3973, page SHA-256: OK, SHA256SUMS: OK (7948 files)**, code de sortie 0, et les trois reponses publiees (abort documented, accept described elsewhere, bzero absent) sont les memes avec le corpus de 3 973 pages qu'avec le corpus fige. Le dossier du rejeu n'a pas ete modifie (verifie avec `find -newer`).
- **Une date affichee par l'outil etait fausse, elle est corrigee.** `tools/build_corpus.py` ecrivait la date codee en dur « 2026-11-14 » dans le manifeste de tout corpus qu'il construisait : le corpus reconstruit par le rejeu du 18 novembre disait « consulted on 2026-11-14 » alors que ses pages ont ete telechargees le 18 novembre. La date vient maintenant du journal de telechargement de la construction (la derniere page telechargee), et du jour de la construction quand il n'y a pas de journal. Le corpus fige du projet n'est pas touche : son propre manifeste garde la date du 14 novembre, qui est la date de ses pages.
- **Les deux verifications qui avaient besoin du corpus ont ete relancees.** La parite du bloc README tourne desormais contre le corpus fige : `tests.test_readme` repond OK (le bloc du README est la sortie reelle de l'outil). Le controle anti-fuite a ete relance sur le corpus du 14 novembre, en arriere-plan (il demande plus de 25 minutes).
- **Le meme budget faux etait dans deux autres documents publies.** `docs/README-FR.md` (le README en francais) et `CORPUS-NON-PUBLIE.txt` (la notice qui explique a un lecteur comment reconstruire le corpus) disaient la meme chose (« environ 1 h 40 a 2 h ») ; ils disent maintenant « environ deux heures » et citent la meme mesure (3 973 pages en 2 h 03, 1,87 s par page, 0 echec). Les seules occurrences qui restent dans le depot public sont dans le journal date de la progression, ou elles sont l'historique de ce qui etait cru a l'epoque -- et ou l'entree de ce cycle dit qu'elles etaient fausses.

## Progression de ce cycle (19/11/2026, 06:16, les suppressions annoncees par le guide officiel sont dans l'outil)
- **Le patch de la mere a ete applique proprement** avec `git am 0001-retraits-v2.patch` (21 415 o, md5 `a755171c2989494dea022facef0b6ad4`) : aucun echec de `git am`, aucun force/reset/rebase. Nouveau HEAD = `3413482` ("A function that the official migration guide says was removed is reported absent, priority 1, with the removal sentence quoted (itoa, _smalloc were 'described elsewhere', priority 3)"). 1 commit, 9 fichiers : `classify.py`, `cli.py`, `quick.py`, `report.py`, `tests/test_fixtures.py`, `tests/test_frozen_corpus.py`, `tests/test_lang_en.py`, `tests/test_quick.py` et `MANIFESTE-PUBLIE.txt`. Le fichier du patch lui-meme est garde hors de l'arbre publie (dans `/work/preparation/patches/`), pour que le depot public ne contienne que le code.
- **La mesure a ete refaite (J5, datee 19/11/2026)** : le resultat attendu est la, exactement. `InterruptAttach` est maintenant « non resolu : retire selon le guide » -- statut `absent`, priorite 1, avec la phrase du guide citee (« The following functions have been removed: InterruptAttach() InterruptAttachArray() InterruptHookIdle2() InterruptHookTrace() », page `kernel.html` de `com.qnx.doc.qnxsdp.migration`). Le taux passe de 96 % a **95 %** (95 resolus et cites, 5 non resolus : les quatre absents historiques + InterruptAttach). `if_freenameindex` et `setsockopt` restent convertis (« decrit ailleurs » dans le guide io-sock). L'echantillon est toujours **strictement identique a J4** (« identique a J4 : OUI »). J4 reste une mesure datee, non reecrite.
- **202 tests, tous verts** avec et sans le corpus : `python3 -B -m unittest discover -s tests -t .` -> `Ran 202 tests`, `OK (skipped=33)` sans corpus, `OK (skipped=1)` avec lui. Les 3 tests rouges que la mere attendait apres le patch (etats publies de `test_mesure_j4`, taux 95 au lieu de 96 + etats de `test_mesure_j5`) sont devenus verts en deplacant les **chiffres publies** (95 %, 2 conversions, InterruptAttach comme suppression), jamais en affaiblissant un test : `test_mesure_j4` verifie maintenant exactement la seule difference attendue, `test_mesure_j5` verifie la suppression, `test_quick` verifie que `absent` n'est dit que pour les suppressions annoncees par le guide.
- **Le mode rapide ne dit `absent` que quand le guide annonce la suppression.** Execution reelle, corpus fige qui sert les pages, `python3 -m qnx_portmap --quick InterruptAttach itoa abort bzero` : InterruptAttach et itoa -> `absent` avec la phrase du guide citee (kernel.html / c_apps.html), abort -> `documented`, bzero -> `unknown`. Journal `/work/quick-retrait-demo-20261119.log`.
- **Les documents ont ete mis a jour** : `README.md`, `docs/README-FR.md`, `docs/UTILISATION.md`, `docs/CODELAB-COMMUNITY-QNX.md`, `docs/CODELAB-FORUM-PROPOSITION.md`, `VIDEO-YOUTUBE-QNX-PORTMAP.md`, `scripts/video/record_demo.sh`, `qnx_portmap/quick.py` (docstring), `scripts/install-sdp8.sh` (message). Le point souligne partout : « dans un vrai depot public, l'outil trouve un appel a InterruptAttach(), retire en 8.0 selon le guide officiel ». Les captures de demonstration restent valides (elles ne montrent ni chiffre de taux ni entete du mode rapide).
- **Un kit V3 a ete ecrit** (`KIT-SOUMISSION-QNX-V3-20261119.md`, un NOUVEAU fichier versionne ; le kit V2 fige et celui du 15/11 ne sont pas touches) avec les chiffres a jour (95 %, InterruptAttach « retire selon le guide », le nouveau point, les longueurs des champs). Il est passe dans `verif-kit-devpost.py` : verdict **OK**, RC 0.
- **La preuve (l) du rapport anglais a ete regeneree** : elle annoncait encore « 96 % devient 97 % » alors que le chiffre publie est 95 %. Elle a ete refaite par un script (`/work/preparation/regen_preuve_l.py`, hors de l'arbre publie) qui casse reellement `docs/mesure-J4.md` (93 % -> 94 %) puis `docs/mesure-J5.md` (95 % -> 96 %) dans une copie, exige l'echec des tests (RC 1 et RC 1), restaure les fichiers octet pour octet (SHA-256 identique) et exige le retour au vert (RC 0). Les sorties du fichier sont celles de cette execution.

## Progression de ce cycle (19/11/2026, 08:30, le kit publie est la version du 19 novembre 2026, corrigee deux fois en prose)
- **Le kit publie est la version du 19 novembre 2026 qui remplace celle du commit `2b0704f`.** Elle porte trois corrections, toutes dans la prose autour des blocs a coller, jamais dans un bloc : l'en-tete dit desormais que le fichier a ete revise le 19 novembre 2026, les chiffres cites par la video de demonstration sont dates (la video dit 96 %, le taux publie le 17 novembre 2026, le jour de sa publication), et les deux references a un chemin de l'environnement de compilation ont disparu. La phrase qui donne la source du tableau de reference de 1 200 caracteres est conservee : elle est vraie, et c'est la seule trace utile.
- **Les 18 blocs a coller sont identiques octet pour octet, caractere pour caractere, a ceux de la version de `2b0704f`.** Le script qui ecrit le fichier refuse de l'ecrire si l'un d'eux a bouge, si une longueur mesuree a change, ou si la reference au chemin interne y est encore. Les longueurs mesurees par le depot (`python3 tools/mesure_kit.py --check`) sont les memes qu'avant : 1 170 et 1 187 caracteres pour les deux champs de description, 2 673 pour les instructions de test, 1 176 pour le champ bonus, 2 959 pour la preuve QNX.
- **L'en-tete ne porte plus de numero de version.** Il portait « Version 4 », le numero de la version publiee a `2b0704f` : ce numero aurait ete faux dans le fichier qui le remplace. L'en-tete nomme desormais la date de publication et le commit de la version qu'il remplace (`2b0704f`), qui reste dans l'historique du depot, a cote du kit du 15 novembre 2026 (`1b46b69`).
- **Le verificateur des kits est vert sur le fichier publie** : 13 champs verifies, 0 au-dessus de la limite, 0 champ non couvert, 0 placeholder, 0 divergence, code de sortie 0. La contre-epreuve mord toujours : sur une copie, avec 40 caracteres ajoutes dans le bloc du champ « Description », le meme verificateur repond NON CONFORME (au-dessus de la limite) et nomme le champ, code de sortie 1.
- **Rien d'autre n'a change** : aucune ligne de l'outil, aucun test, aucun corpus, aucune image. Le manifeste publie est regenere, comme apres chaque changement de l'arbre publie.

## Progression de ce cycle (19/11/2026, 09:45, le kit publie dit la verite sur le corpus)
- **Les deux chemins de corpus que citait le kit publie ne sont pas dans le depot public.** Le kit disait que le corpus se lit dans `corpus/index/pages.jsonl` et se verifie contre `corpus/SHA256SUMS`. Le depot ne contient aucun repertoire `corpus/` : la documentation QNX n'est pas redistribuee avec le depot (licence). Le kit dit desormais exactement cela dans le bloc de la preuve QNX, donne la seule commande qui reconstruit le corpus (`bash scripts/bootstrap_corpus.sh --out corpus-downloaded`, la commande du README, ligne 115) et les deux chemins exacts de l'instantane construit : `corpus-downloaded/index/pages.jsonl` (l'index) et `corpus-downloaded/SHA256SUMS` (les empreintes des fichiers). Les deux chemins ont ete verifies sur la copie locale du corpus, pas supposes. La phrase sur la verification est conservee et rendue exacte : `qnx-portmap --verify-corpus` compare le SHA-256 de chaque page avec l'index, donc la citation vient bien de la page qu'elle nomme.
- **Les 18 blocs a coller gardent leurs longueurs publiees.** Dix-sept sont identiques octet pour octet a ceux de la version de `2b0704f`. Seul le bloc de la preuve QNX (4_7) a change, parce que les deux faux chemins y etaient, et il garde exactement sa longueur publiee : 2 959 caracteres, le nombre que le kit annonce et que le verificateur remesure. Le script qui ecrit le fichier refuse de l'ecrire si un bloc bouge, si l'une des six longueurs publiees change, ou si un faux chemin y est encore.
- **Le verificateur des kits est vert sur le nouveau fichier** : 13 champs verifies, 0 au-dessus de la limite, 0 champ non couvert, 0 placeholder, 0 divergence, code de sortie 0. La contre-epreuve mord toujours : sur une copie, avec 40 caracteres ajoutes dans le bloc du champ « Description », le meme verificateur repond NON CONFORME (au-dessus de la limite) et nomme le champ, code de sortie 1. Les longueurs mesurees par le depot (`python3 tools/mesure_kit.py --check`) n'ont pas change.
- **L'audit des chemins cites par le kit** : 33 chemins cites, 4 absents de l'arbre public, et aucun n'est un faux chemin du depot. `image/png` est un type MIME, pas un fichier. `verif-kit-devpost.py` est le verificateur du proprietaire, qui n'est pas publie. `corpus-downloaded/index/pages.jsonl` et `corpus-downloaded/SHA256SUMS` sont les deux fichiers de l'instantane que construit la commande du kit, dans un repertoire qui n'est pas dans le depot par construction.
- **Rien d'autre n'a change** : aucune ligne de l'outil, aucun test, aucun corpus, aucune image. Le manifeste publie est regenere, comme apres chaque changement de l'arbre publie.

## Progression de ce cycle (19/11/2026, 23:35, le codelab de la soumission est publie)
- **Le codelab est ecrit, verifie et publie.** `docs/codelab/QX-PORTMAP-CODELAB.md` (23 874 octets, md5 `9749480b9c340e27833d1c89e7c02e20`) est dans `main` depuis le commit `a8ffb53`, suivi de `79fa0f3`, `241f2e2` et `33acb70` (fast-forward, jamais un amend). L'URL publique est https://github.com/tgg49099-dotcom/qnx-qx-portmap/blob/main/docs/codelab/QX-PORTMAP-CODELAB.md (mesure depuis l'exterieur le 19/11 a 23:05 : HTTP 200, les memes octets que le fichier local). Le manifeste publie a ete regenere (126 -> 127 fichiers) et le README renvoie au codelab.
- **La forme du codelab** : neuf etapes (clone, `--help`, mode rapide, un court test de telechargement, l'instantane complet, la reponse hors ligne complete avec les citations, `--verify-corpus`, l'extraction des appels du lecteur, le JSON de ces appels), puis « How to verify », « The traps » (quatre) et une « Next step » d'une phrase. Chaque etape donne une commande et un resultat attendu.
- **Les quatre pieges sont ceux que le lecteur rencontre vraiment** : le corpus n'est pas redistribue (licence), `unknown` n'est pas `absent`, le code de sortie 1 est une reponse et pas un echec, et la suite de tests a besoin de 145 Mo dans `TMPDIR`.
- **Le verificateur du codelab est vert** (86 controles, code de sortie 0) et deux contre-epreuves rouges mordent (un chemin invente, une structure cassee). Le kit, les blocs a coller, les quatre images de la galerie et le script de verification n'ont pas ete touches.

## Progression de ce cycle (20/11/2026, 00:50, le codelab est rejoue par un lecteur, et trois de ses sorties mesurees etaient fausses)
- **Le codelab est desormais rejoue de bout en bout par un script qui joue le lecteur** (`/work/candidat-028-codelab/rejouer-codelab.py`, hors de l'arbre publie) : il clone le depot public, execute les neuf commandes du codelab telles qu'elles sont ecrites, compare chaque sortie avec le bloc annonce, puis execute les trois commandes de la section « How to verify ». **13 controles**. Le premier rejeu a trouve quatre defauts reels, tous corriges dans ce cycle.
- **Un test publie ne passait que le jour ou il a ete ecrit.** `tests/test_mesure_j5.py` comparait le rapport de mesure anglais publie avec la sortie de l'outil, octet pour octet, mais l'outil estampille le jour de l'execution dans le rapport : la suite etait verte le 19/11 et **rouge dans un clone neuf le 20/11** (1 echec, 33 ignores) et `verify-all.sh` repondait alors `FAILED AND NOT CHECKED - 2 check(s) FAILED`. Le test epingle desormais la date du rapport publie avant de le regenerer (commit `82b26a6`) : la suite est verte de nouveau (202 tests, 33 ignores) et le verdict est `6/8 OK, 2 NOT CHECKED` tous les jours. **Le rapport publie n'a pas ete reecrit.**
- **Trois sorties attendues du codelab n'etaient pas les sorties mesurees.** (a) Le JSON de l'etape 9 etait une sortie plus ancienne : il ne portait pas `citation_kind`, `see_urls`, `mentioned_in_migration_guide`, `migration_urls`, `detail` et `note`, et il donnait le genre `function` pour `bzero` et `f`, que l'outil repond avec un genre vide. Le bloc est desormais la sortie mesuree le 20/11. (b) L'etape 7 annoncait `SHA256SUMS: OK (<N>+1 files)`, un placeholder jamais remplace : elle dit desormais `<M>` et explique que `<M>` vaut 3 427 pour l'instantane fige et 7 948 pour un instantane reconstruit a l'etape 5 (les deux valeurs mesurees). (c) La section « How to verify » ne disait pas ce que le lecteur voit apres les etapes : l'arbre est alors sale et le verdict mesure est `VERDICT: FAILED AND NOT CHECKED - 1 check(s) FAILED and 4 check(s) could not run out of 8 (RC 1)`, la ligne en echec etant le manifeste publie. La section le dit desormais, et dit que la commande est faite pour etre lancee sur un clone neuf.
- **Un piege etait ecrit a moitie** : le script n'ecrase jamais un corpus fige, et le premier rejeu a heurte le refus (`bootstrap_corpus: refus : /tmp/essai contient deja un corpus fige`). Le premier piege le dit desormais, avec le message exact.
- **Un nombre du README etait faux** : la transcription publiee de `verify-all.sh` disait `nothing left in the 70 published documents`, le compte reel est **71** (le codelab en a ajoute un). Le README est corrige ; la transcription publiee est desormais identique octet pour octet a la sortie reelle.
- **Rien d'autre n'a change** : aucune ligne de l'outil, aucun corpus, aucune image, et le kit, les blocs a coller et le script de verification n'ont pas ete touches. Le manifeste publie est regenere, comme apres chaque changement de l'arbre publie.

## Progression de ce cycle (22/11/2026, 06:45, l'audit hostile de la moitie PORTMAP a trouve 6 lignes fausses, elles sont corrigees, et la licence est desormais detectee comme MIT)
- **Un audit hostile a verifie une a une les 149 affirmations de la moitie PORTMAP du kit de soumission** : 138 mesurees vraies, **6 fausses**, et 5 sont des mesures datees qui ne peuvent pas etre rejouees. Les 6 lignes fausses avaient 5 causes distinctes : deux chiffres perimes (`3 722` -> `3 843` caracteres, `1 min 52 s` -> `1 min 51 s`), un chiffre que le depot ne porte pas (`149.1 s` -> `151.2 s`, la duree que le depot documente pour ce rejeu), deux attributions de date fausses (le kit du 15 novembre n'est pas celui de 12 263 caracteres : c'est celui du 18 novembre, au commit `1b46b69`), et une reponse de licence.
- **La phrase sur la licence etait fausse pour une raison mesuree, pas devinee.** Le kit dit que le depot « contains an MIT licence file (LICENSE) at the top of the repository page », et le reglement du concours demande une licence « detectable and visible at the top of the repository page ». Le fichier `LICENSE` commencait bien par le texte MIT, mais l'API repondait `license.spdx_id = NOASSERTION` et `name = "Other"` : 9 lignes en francais avaient ete ajoutees apres le texte MIT, et un second fichier de licence inconnu (`LICENCE-DOCS-QNX.md`) se trouvait a la racine du depot. Le fichier est desormais le seul texte MIT (21 lignes), le second fichier est renomme `NOTICES-DOCS-QNX.md` (meme longueur de nom, les 36 mentions mises a jour), et le manifeste publie est regenere (127 fichiers).
- **La preuve apres le push** : `GET https://api.github.com/repos/tgg49099-dotcom/qnx-qx-portmap` repond `license.spdx_id = "MIT"` et `license.name = "MIT License"`. La phrase du kit n'a pas ete reecrite : elle est devenue vraie parce que le depot a ete corrige, et c'est cela que le juge lit.
- **Deux commits, rien d'autre** : `4a4ebcc` (« licence MIT detectable + 5 corrections audit hostile ») et `7af8943` (« la duree de la video est 1 min 51 s dans tous les documents »). Les 5 textes fautifs ont maintenant 0 occurrence dans l'arbre public (128 fichiers) et `NOTICES-DOCS-QNX.md` y apparait 36 fois.

## Progression de ce cycle (22/11/2026, 10:30, l'arbre public est verifie de bout en bout avec le corpus fige (8/8), et le codelab est rejoue par un juge)
- **Le verdict du cycle precedent etait provisoire, il est desormais complet.** Le cycle de 06:45 a conclu que le corpus QNX n'etait pas sur la machine et a publie `6/8 OK, 2 NOT CHECKED`. Le corpus **est** sur la machine (`/work/qnx-portmap-corpus-local/corpus`, 3 430 fichiers, 50 Mo, empreintes SHA-256 intactes), mais `scripts/verify-all.sh` ne le cherche que dans `$ROOT/corpus` ou par `QX_PORTMAP_CORPUS`. En le pointant, les 2 controles qui ne pouvaient pas tourner tournent : sur un clone public neuf (`main = 7af8943`), le 22/11 07:56-08:30, `VERDICT: EVERY CHECK PASSED - 8/8 OK (RC 0)` : suite de tests OK (202 tests), controle anti-fuite du corpus OK (0 correspondance avec la documentation QNX), manifeste publie OK (127 fichiers), chiffres publies du README OK, parite du bloc de sortie du README OK (le README montre la sortie reelle), contre-epreuve ROUGE OK, longueurs du kit de soumission OK, placeholders et bannieres de brouillon OK (71 documents publies).
- **Les trois configurations publiees par le kit sont toutes remesurees** : corpus a cote du paquet -> `Ran 202 tests in 32.903s` / `OK` (0 ignore) ; corpus par `QX_PORTMAP_CORPUS` -> `OK (skipped=1)` ; sans corpus -> `Ran 202 tests in 1.004s` / `OK (skipped=33)`. La contre-epreuve ROUGE donne 11 / 11 avec le corpus. Le « 0.98 s » du champ Devpost P1 se rejoue a 1.004 s ici.
- **Un piege qui merite d'etre publie** : le corpus ne doit jamais etre copie **dans** l'arbre. Le controle anti-fuite scanne tout l'arbre et repond alors `FAILED` sur un depot qui ne contient aucune page QNX. Le corpus de reference reste hors de l'arbre.
- **Le codelab est rejoue par un lecteur sur l'arbre public, apres les corrections** : les neuf commandes du tutoriel sont executees telles qu'elles sont ecrites et chaque sortie annoncee est comparee a la sortie mesuree, puis les trois commandes de la section « How to verify » sont lancees. **13 controles, 13 OK** (les etapes 1 a 9, le verdict sur clone neuf `NO CHECK FAILED - 6/8 OK, 2 NOT CHECKED`, la suite `Ran 202 tests ... OK (skipped=33)`, la contre-epreuve rouge 10 / 10, et le verdict apres les etapes, qui est le `FAILED AND NOT CHECKED - 1 check(s) FAILED` que le codelab annonce pour un arbre sale).
- **Les chiffres que le kit publie sur les medias sont toujours ceux des fichiers publies** : le md5 de chacune des quatre images de la galerie annonce dans le kit est le md5 du fichier du depot, et la video dure toujours 111,04 s (1 min 51 s) et montre a l'ecran `Ran 194 tests in 0.607s` / `OK (skipped=33)` - les deux chiffres que le document de la video date du jour du tournage.
- **Une promesse perimee est corrigee dans le codelab** : il annoncait une demonstration sur une vraie cible QNX 8.0 « to be confirmed on QNX 8.0 on 20 November 2026 ». Cette date est passee et la licence SDP 8.0 manque toujours, donc le codelab dit desormais ce qui est vrai : **not done as of 22 November 2026**. Rien d'autre du codelab n'a ete touche, et la « Next step » est toujours d'une phrase.
