# Demo sur un projet reel : plibsys

Date de la mesure : **14/11/2026**. Tout ce qui suit est reproductible hors
ligne avec le corpus fige du depot.

## 1. Le projet etudi

| Element | Valeur |
|---|---|
| Depot | <https://github.com/saprykin/plibsys> |
| Commit | `5a3b06b5e43bced95c2bdfc316d78061ecf833af` (2026-07-17) |
| Licence | MIT (`COPYING` du projet) |
| Clone local | `/tmp/demo_plibsys` (git clone, 14/11/2026) |
| Fichiers lus | 101 `.c` + 50 `.h` |

plibsys est une bibliotheque C portable (threads, mutex, semaphores, sockets,
memoire partagee) : c'est le genre de code que l'on veut porter vers QNX 8.0.

## 2. Extraction des symboles (commande exacte)

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

Ce sont les noms appeles ou definis dans le projet, plus les mots anglais qui
apparaissent suivis de `(` dans les commentaires (`address (`, `argument (`).
C'est **volontaire** : c'est exactement le genre de bruit que l'outil doit
savoir ecarter (voir §5).

## 3. Analyse QX PORTMAP (commande exacte et sortie reelle)

```sh
cd /work/qnx-portmap
python3 -m qnx_portmap --corpus corpus --file /tmp/plibsys_symbols_v2.txt --format json
```

Code de sortie : **1** (au moins un symbole absent ou inconnu), en 10 s, sans
reseau.

| Statut | Nombre | Ce que ça veut dire ici |
|---|---|---|
| `documented` | **122** | page officielle dans la C Library Reference 8.0 (`pthread_create`, `malloc`, `sem_wait`, `mmap`, ...) |
| `described_elsewhere` | **20** | sans page propre en 8.0, mais decrit ailleurs (voir §4) |
| `absent` | **0** | aucun symbole du projet n'etait dans la C Library Reference 7.1 et n'existe plus en 8.0 |
| `unknown` | **734** | introuvable dans le corpus fige : 324 environ portent un prefixe interne du projet (`p_*`, `psys*`, `puthread*`...), les 410 autres sont des builtins du compilateur, des API Windows ou des mots anglais |

Extrait reel de la sortie en texte (commande
`python3 -m qnx_portmap --corpus corpus --file sous-ensemble.txt`) :

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

## 4. Le resultat utile : les 19 API socket renvoyees par QNX 8.0

Les 20 symboles `described_elsewhere` sont **presque tous les appels socket
BSD**. La C Library Reference 8.0 ne leur donne pas de page propre : elle les
renvoie explicitement au manuel FreeBSD **et** au guide io-sock :

`accept`, `bind`, `connect`, `freeaddrinfo`, `getaddrinfo`, `getpeername`,
`getsockname`, `getsockopt`, `inet_ntop`, `inet_pton`, `listen`, `recv`,
`recvfrom`, `send`, `sendto`, `setsockopt`, `shutdown`, `socket`, `sysctl`.

Pour un porteur de projet, c'est le signal le plus utile du lot : **sur QNX
8.0, la couche socket n'est plus dans la C Library Reference, elle est dans
`io_sock` et le contrat est celui de FreeBSD.** Chaque ligne du renvoi cite
aussi le guide de migration officiel 8.0.

Le 20e symbole est `__attribute__`, trouve dans un exemple de code de la page
`_register_ioctl_handler.html` : c'est une mention dans la documentation, pas
une API QNX. L'outil le signale comme tel (mention, pas documentation).

## 5. Mesure de la regle "nom d'API" sur ce projet

Meme liste de 876 symboles, regle desactivee dans une **copie** du code
(`/tmp/portmap_sans_regle`, le depot n'est pas touche) :

| | `documented` | `described_elsewhere` | `unknown` |
|---|---|---|---|
| avec la regle (livree) | 122 | **20** | 734 |
| sans la regle (mesure) | 122 | **117** | 637 |

Les **97** symboles ajoutes sont des mots anglais ou des noms de parametres
trouves dans la prose de la documentation :

`address`, `any`, `architectures`, `argument`, `barrier`, `binary`, `bit`,
`blocking`, `brackets`, `bytes`, `capabilities`, `character`, `characters`,
`collisions`, `compiler`, `cores`, `create`, `current`, `deadlock`,
`descriptor`, ... (les 97 sont dans la sortie JSON du run "sans la regle").

Annoncer ces mots comme "decrit ailleurs dans la documentation 8.0" serait
faux : la regle "le symbole doit ressembler a un nom d'API" (present dans un
index QNX, ou ecrit avec une majuscule ou un tiret bas) les ecarte.

## 6. Ce que cette demo ne prouve PAS

- **Elle ne prouve pas que plibsys compile sur QNX 8.0.** L'outil lit la
  documentation ; il ne compile rien, il ne teste rien sur cible, il n'a pas de
  SDP. Un symbole `documented` signifie "la C Library Reference 8.0 a une page
  pour ce nom", pas "ce code fonctionnera".
- **Elle ne mesure pas la compatibilite des structures, des options de socket
  ou des valeurs d'erreur.** Ces details sont dans les pages citees, que
  l'outil designe mais ne resume pas.
- **`unknown` ne veut pas dire "absent de QNX".** 410 symboles standards ou
  builtins du projet (`__atomic_fetch_add`, `_beginthreadex`, ...) ne sont pas
  dans l'index de la C Library Reference : ils sont peut-etre dans un autre
  livre de la documentation, ou supports par le compilateur et non documentes.
  L'outil ne devine pas.
- **Le corpus est un instantane du 14/11/2026.** Une page publiee le lendemain
  ne change rien au resultat.
- **L'extraction des symboles est un prototype.** Un vrai portage utiliserait
  un preprocesseur C (`gcc -E`) ou un parseur ; la commande du §2 prend aussi
  les mots des commentaires, ce qui alimente le bruit mesure au §5.
