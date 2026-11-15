# Mesure J4 - taux de resolution de QX PORTMAP sur de vrais depots QNX publics

Mesure faite le 2026-11-14 par `tools/mesure_j4.py` (reproductible : voir la section Reproduire plus bas).

## Le chiffre

**Taux J4 = 93 % (93 symboles resolus et cites sur 100).**

| etat | nombre | compte dans le critere J4 ? |
|---|---:|---|
| resolu et cite | 93 | oui |
| resolu mais decrit ailleurs | 3 | **non** |
| non resolu | 4 | **non** |

Cumul des trois etats : 100. Le seuil J4 de la fiche est 80 % : **le seuil est franchi**.

Les 7 symboles qui ne comptent pas comme resolus le sont pour une raison precise et verifiable, et l'outil la dit :

- **decrit ailleurs** (3) : la documentation QNX 8.0 renvoie explicitement le symbole a une autre source (renvoi "The following are described elsewhere" de l'index 8.0). L'outil cite cette source exacte - il ne pretend pas que le symbole a une page dans la C Library Reference.
- **absent** (4) : le symbole etait dans la C Library Reference 7.1 et ne se trouve plus dans le corpus 8.0. L'outil le signale comme disparu.

## L'echantillon : 5 depots QNX publics, 100 symboles

| depot | URL | commit epingle | fichiers .c/.h retenus | sous-dossier | consulte le |
|---|---|---|---:|---|---|
| `vocho/openqnx` | https://github.com/vocho/openqnx | `cc95df35` | 759 | `trunk/services` | 2026-11-14 |
| `qnx/bsp_raspberrypi-bcm2712-rpi5` | https://github.com/qnx/bsp_raspberrypi-bcm2712-rpi5 | `573dda1a` | 350 | `(depot entier)` | 2026-11-14 |
| `varghes/Raspberry-QNX` | https://github.com/varghes/Raspberry-QNX | `043582a9` | 46 | `Bsp_Rasp/src/hardware/devi` | 2026-11-14 |
| `qnx/qnx-posix-publish-subscribe` | https://github.com/qnx/qnx-posix-publish-subscribe | `b5ca892f` | 102 | `(depot entier)` | 2026-11-14 |
| `qnx/socketcan` | https://github.com/qnx/socketcan | `9db62b47` | 45 | `(depot entier)` | 2026-11-14 |

Clones : `git clone --depth 1` (superficiels), un seul sous-dossier utile pour les depots gros. Les clones ont ete supprimes a la fin de la mesure : seuls les extraits de symboles sont conserves.

## La methode, etape par etape

1. **Extraction.** Dans chaque depot, on releve tous les identifiants appeles comme fonctions dans les fichiers `.c`/`.h` retenus (les commentaires et le code des preprocesseurs sont retires).
2. **Purge.** Les symboles definis par le projet lui-meme (fonctions et macros definees dans le depot) sont ecartes : ce ne sont pas des symboles QNX.
3. **Selection.** Un symbole est retenu s'il figure dans la C Library Reference QNX (index 8.0 ou 7.1) : c'est la definition d'un symbole d'API QNX. On retient **les 20 symboles les plus appeles de chaque depot**, et on privilegie les symboles **specifiques a QNX** (`io_open`, `resmgr_attach`, `iofunc_read_default`, `ThreadCtl`, `ConnectAttach`...) avant les symboles standards C/POSIX. Un symbole deja retenu par un depot precedent n'est pas repris : l'echantillon compte exactement **100 symboles distincts**.
4. **Separation des familles.** Un symbole est dit "standard" s'il figure dans `tools/posix-base.txt` (liste C standard + POSIX/XSI, **independante du corpus QNX**), sinon il est dit "specifique a QNX".
5. **Mesure.** QX PORTMAP classe les 100 symboles sur le corpus fige (hors ligne, aucun acces reseau) et l'on releve pour chacun : statut, page officielle, citation.
6. **Citation verifiable.** Une citation compte si la page citee existe dans le corpus fige (empreinte SHA-256 verifiable) et si la citation n'est pas vide.

## Repartition par famille

| famille | resolus et cites | total | taux |
|---|---:|---:|---:|
| specifiques a QNX | 85 | 91 | 93.4 % |
| standards C/POSIX | 8 | 9 | 88.9 % |

## Contre-mesure : un second echantillon plus large

Le meme protocole, mais sans privilegier les symboles specifiques a QNX (les 20 symboles les plus appeles de chaque depot, toutes familles confondues) donne **96 % (96 / 100)**.
Les deux echantillons franchissent le seuil de 80 %.

## Les 100 symboles mesures

Une ligne par symbole : nom, depot, statut, page/source. La citation litterale de chaque symbole est dans `docs/mesure-J4/citations-*.txt` (une page par depot), avec l'URL de la page source, la date de consultation et son empreinte SHA-256.

| # | symbole | depot | famille | statut | etat J4 | appels dans le depot | page citee | source de la citation | sha256 de la page |
|---:|---|---|---|---|---|---:|---|---|---|
| 1 | `GETIOVLEN` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 117 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/g/getiovlen.html | index C Library Reference 8.0 | `a1e106f35eab225a` |
| 2 | `SETIOV` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 115 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/setiov.html | index C Library Reference 8.0 | `909ddab8c18ea668` |
| 3 | `GETIOVBASE` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 86 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/g/getiovbase.html | index C Library Reference 8.0 | `8f12e5c4f9034ab1` |
| 4 | `_RESMGR_PTR` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 71 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/_resmgr_ptr.html | index C Library Reference 8.0 | `e37dd7f893343f86` |
| 5 | `ENDIAN_SWAP32` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 64 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/endian_swap32.html | index C Library Reference 8.0 | `4a50fde39cbfec8a` |
| 6 | `resmgr_attach` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 39 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/resmgr_attach.html | index C Library Reference 8.0 | `407c212bd880a3fe` |
| 7 | `TraceEvent` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 34 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/traceevent.html | index C Library Reference 8.0 | `bfbb392bc0209748` |
| 8 | `iofunc_attr_init` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 30 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_attr_init.html | index C Library Reference 8.0 | `c4fdfb6dc60da4a3` |
| 9 | `ND_NODE_CMP` | `vocho/openqnx` | qnx | `absent` | non_resolu | 29 | https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/n/nd_node_cmp.html | index C Library Reference 7.1 | `4c078087f43932b0` |
| 10 | `ENDIAN_SWAP16` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 28 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/endian_swap16.html | index C Library Reference 8.0 | `cfb3a0b66ff7454b` |
| 11 | `ThreadDestroy` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 28 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/threaddestroy.html | index C Library Reference 8.0 | `6ce030eb595328cc` |
| 12 | `MsgError` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 27 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgerror.html | index C Library Reference 8.0 | `be8b201b6e24ef63` |
| 13 | `MsgReply` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 26 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgreply.html | index C Library Reference 8.0 | `d64b033bdbdb8cc4` |
| 14 | `devctl` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 23 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/devctl.html | index C Library Reference 8.0 | `01b7ceef60a6e28d` |
| 15 | `slogf` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 19 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/slogf.html | index C Library Reference 8.0 | `10e537c4cf1c4b4f` |
| 16 | `ConnectAttach` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 18 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/connectattach.html | index C Library Reference 8.0 | `f75baa440ea1cce0` |
| 17 | `iofunc_func_init` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 18 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_func_init.html | index C Library Reference 8.0 | `58b304930c31820b` |
| 18 | `iofunc_attr_unlock` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 17 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_attr_unlock.html | index C Library Reference 8.0 | `bab3e30b02d60f99` |
| 19 | `iofunc_open` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 16 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_open.html | index C Library Reference 8.0 | `e4a53fb4eda16799` |
| 20 | `out32` | `vocho/openqnx` | qnx | `documented` | resolu_et_cite | 16 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/o/out32.html | index C Library Reference 8.0 | `51946456f3b60380` |
| 21 | `in32` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 76 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/in32.html | index C Library Reference 8.0 | `52fd92e3fc91cffc` |
| 22 | `ENDIAN_BE32` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 20 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/endian_be32.html | index C Library Reference 8.0 | `862b23e0cff76c86` |
| 23 | `atomic_set` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 20 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/atomic_set.html | index C Library Reference 8.0 | `0dba614063aa5dd7` |
| 24 | `mmap_device_memory` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 16 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/mmap_device_memory.html | index C Library Reference 8.0 | `ffd3343ca7889950` |
| 25 | `atomic_clr` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 15 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/a/atomic_clr.html | index C Library Reference 8.0 | `ba5cfe6d9cf30f83` |
| 26 | `hwi_tag_find` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 13 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/h/hwi_tag_find.html | index C Library Reference 8.0 | `b1e1761376708aa0` |
| 27 | `munmap_device_memory` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 13 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/munmap_device_memory.html | index C Library Reference 8.0 | `f3ff83efae0775e5` |
| 28 | `UNALIGNED_RET32` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 9 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/u/unaligned_ret32.html | index C Library Reference 8.0 | `e637f8f2d1cdf8b0` |
| 29 | `hwi_tag2off` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 9 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/h/hwi_tag2off.html | index C Library Reference 8.0 | `f476fc22f8636727` |
| 30 | `hwi_find_item` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 8 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/h/hwi_find_item.html | index C Library Reference 8.0 | `8443c6623e26669d` |
| 31 | `pthread_sleepon_lock` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `absent` | non_resolu | 8 | https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_sleepon_lock.html | index C Library Reference 7.1 | `8f47fc9125b3343d` |
| 32 | `pthread_sleepon_unlock` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `absent` | non_resolu | 8 | https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_sleepon_unlock.html | index C Library Reference 7.1 | `f8250699a0c87c83` |
| 33 | `ENDIAN_BE16` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 6 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/endian_be16.html | index C Library Reference 8.0 | `8bd3bd12bcf7ae97` |
| 34 | `MsgSendPulse` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 6 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgsendpulse.html | index C Library Reference 8.0 | `7d46e9e9fca2528d` |
| 35 | `in8` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 6 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/in8.html | index C Library Reference 8.0 | `390c807411348e20` |
| 36 | `out8` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 6 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/o/out8.html | index C Library Reference 8.0 | `a55b7914b3054076` |
| 37 | `ChannelCreate` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 5 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/channelcreate.html | index C Library Reference 8.0 | `e1c83f6a6a974281` |
| 38 | `InterruptUnmask` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 5 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptunmask.html | index C Library Reference 8.0 | `97b3ec9904663c14` |
| 39 | `in16` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 5 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/in16.html | index C Library Reference 8.0 | `003496351215a9bc` |
| 40 | `out16` | `qnx/bsp_raspberrypi-bcm2712-rpi5` | qnx | `documented` | resolu_et_cite | 5 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/o/out16.html | index C Library Reference 8.0 | `c271e5bc6e8f0727` |
| 41 | `InterruptMask` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 7 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptmask.html | index C Library Reference 8.0 | `e2599468a82cf786` |
| 42 | `basename` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 5 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/b/basename.html | index C Library Reference 8.0 | `3206dee3df07faae` |
| 43 | `ThreadCtl` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 4 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/threadctl.html | index C Library Reference 8.0 | `62ba371a368bc96a` |
| 44 | `mmap_device_io` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 4 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/mmap_device_io.html | index C Library Reference 8.0 | `947e733be70ed59b` |
| 45 | `InterruptAttach` | `varghes/Raspberry-QNX` | qnx | `described_elsewhere` | resolu_mais_decrit_ailleurs | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/kernel.html | com.qnx.doc.qnxsdp.migration, kernel.html | `a3b329c6f9a04bdd` |
| 46 | `InterruptUnlock` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptunlock.html | index C Library Reference 8.0 | `92d547215685ae36` |
| 47 | `_exit` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/_exit.html | index C Library Reference 8.0 | `bcba6288c4673fd7` |
| 48 | `nanospin_ns` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/n/nanospin_ns.html | index C Library Reference 8.0 | `980664032e70b205` |
| 49 | `InterruptAttachEvent` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptattachevent.html | index C Library Reference 8.0 | `38e413cd205cfce2` |
| 50 | `InterruptLock` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptlock.html | index C Library Reference 8.0 | `e509a9f1662dd23e` |
| 51 | `MsgReplyv` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgreplyv.html | index C Library Reference 8.0 | `f0a7e65c16770fe4` |
| 52 | `MsgSendv` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgsendv.html | index C Library Reference 8.0 | `d5d42b2e499c7e64` |
| 53 | `dispatch_create` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/dispatch_create.html | index C Library Reference 8.0 | `92b15d292a71460f` |
| 54 | `fcfgopen` | `varghes/Raspberry-QNX` | qnx | `absent` | non_resolu | 2 | https://www.qnx.com/developers/docs/7.1/com.qnx.doc.neutrino.lib_ref/topic/f/fcfgopen.html | index C Library Reference 7.1 | `a264611e986dd4b9` |
| 55 | `iofunc_open_default` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_open_default.html | index C Library Reference 8.0 | `12cb23b43041797f` |
| 56 | `iofunc_unblock_default` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_unblock_default.html | index C Library Reference 8.0 | `41316f1da2267e50` |
| 57 | `ionotify` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html | index C Library Reference 8.0 | `e3ba2fd66ae7b31b` |
| 58 | `pulse_attach` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pulse_attach.html | index C Library Reference 8.0 | `2af642bc3c95bbd2` |
| 59 | `rsrcdbmgr_attach` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/rsrcdbmgr_attach.html | index C Library Reference 8.0 | `105ea3ed7cb23a6b` |
| 60 | `strlwr` | `varghes/Raspberry-QNX` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/strlwr.html | index C Library Reference 8.0 | `020d778b364e78bd` |
| 61 | `_RESMGR_NPARTS` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 5 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/_resmgr_nparts.html | index C Library Reference 8.0 | `ffbe0dc88e41c620` |
| 62 | `iofunc_notify_trigger_strict` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_notify_trigger.html | index C Library Reference 8.0 | `3296b370a22aa16b` |
| 63 | `iofunc_read_verify` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_read_verify.html | index C Library Reference 8.0 | `2b71f10d237da190` |
| 64 | `resmgr_msgwrite` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/resmgr_msgwrite.html | index C Library Reference 8.0 | `d3f60a8112bdb797` |
| 65 | `ClockTime_r` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/clocktime.html | index C Library Reference 8.0 | `54d925bb61247042` |
| 66 | `iofunc_notify_trigger` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_notify_trigger.html | index C Library Reference 8.0 | `3296b370a22aa16b` |
| 67 | `iofunc_write_verify` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_write_verify.html | index C Library Reference 8.0 | `720cc573dfa01f73` |
| 68 | `resmgr_msgread` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/resmgr_msgread.html | index C Library Reference 8.0 | `bea514adb9e4771b` |
| 69 | `dispatch_destroy` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/dispatch_destroy.html | index C Library Reference 8.0 | `4ba443f6d052ed10` |
| 70 | `iofunc_attr_lock` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_attr_lock.html | index C Library Reference 8.0 | `dcf74d4a24595463` |
| 71 | `iofunc_close_dup_default` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_close_dup_default.html | index C Library Reference 8.0 | `a90c1be799e1cb0f` |
| 72 | `iofunc_close_ocb_default` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_close_ocb_default.html | index C Library Reference 8.0 | `ed11f069156f11bb` |
| 73 | `iofunc_lseek_default` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_lseek_default.html | index C Library Reference 8.0 | `4b81270d77517b6c` |
| 74 | `iofunc_mknod` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_mknod.html | index C Library Reference 8.0 | `82859d4fd15f4e7a` |
| 75 | `iofunc_notify` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_notify.html | index C Library Reference 8.0 | `256f5e46a89e9f9b` |
| 76 | `iofunc_notify_remove` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_notify_remove.html | index C Library Reference 8.0 | `ea90b0999102312c` |
| 77 | `iofunc_ocb_attach` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_ocb_attach.html | index C Library Reference 8.0 | `250fcb86b6a96cbf` |
| 78 | `iofunc_unlink` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/iofunc_unlink.html | index C Library Reference 8.0 | `3789ef5f89d25384` |
| 79 | `nftw` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/n/nftw.html | index C Library Reference 8.0 | `0129c8bd895c3165` |
| 80 | `resmgr_detach` | `qnx/qnx-posix-publish-subscribe` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/r/resmgr_detach.html | index C Library Reference 8.0 | `809d3e49d196f4f4` |
| 81 | `mtx_lock` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 9 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/mtx_lock.html | index C Library Reference 8.0 | `958d05b20648dd1c` |
| 82 | `mtx_unlock` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 9 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/mtx_unlock.html | index C Library Reference 8.0 | `2390355fe27cdf4f` |
| 83 | `mtx_init` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 3 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/mtx_init.html | index C Library Reference 8.0 | `d9aa0472686b6ba5` |
| 84 | `mtx_destroy` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/mtx_destroy.html | index C Library Reference 8.0 | `98a25f0a79a2ec50` |
| 85 | `ChannelDestroy` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/channeldestroy.html | index C Library Reference 8.0 | `cdf0c7af2864ba2a` |
| 86 | `ConnectDetach` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/connectdetach.html | index C Library Reference 8.0 | `bbd642af24515871` |
| 87 | `InterruptDetach` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptdetach.html | index C Library Reference 8.0 | `3856d1d642175a59` |
| 88 | `MsgReceivePulse` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgreceivepulse.html | index C Library Reference 8.0 | `d05e4b85be7e1f0c` |
| 89 | `if_freenameindex` | `qnx/socketcan` | qnx | `described_elsewhere` | resolu_mais_decrit_ailleurs | 1 | https://man.freebsd.org/cgi/man.cgi?query=if_freenameindex&manpath=FreeBSD+14.4-RELEASE+and+Ports | index C Library Reference 8.0, section "described elsewhere" | `-` |
| 90 | `nanospin` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/n/nanospin.html | index C Library Reference 8.0 | `4b6fd1795c6711e5` |
| 91 | `timespec2nsec` | `qnx/socketcan` | qnx | `documented` | resolu_et_cite | 1 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/timespec2nsec.html | index C Library Reference 8.0 | `a8e6290226dc7b17` |
| 92 | `strerror` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 74 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/strerror.html | index C Library Reference 8.0 | `3f327b1d4e7d3403` |
| 93 | `fprintf` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 69 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/f/fprintf.html | index C Library Reference 8.0 | `fcc9ca0a9f2bc9d4` |
| 94 | `close` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 24 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/close.html | index C Library Reference 8.0 | `7fadabd81e17a978` |
| 95 | `perror` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 23 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/perror.html | index C Library Reference 8.0 | `b1b1dab501078b0e` |
| 96 | `setsockopt` | `qnx/socketcan` | standard | `described_elsewhere` | resolu_mais_decrit_ailleurs | 21 | https://man.freebsd.org/cgi/man.cgi?query=setsockopt&manpath=FreeBSD+14.4-RELEASE+and+Ports | index C Library Reference 8.0, section "described elsewhere" | `-` |
| 97 | `strcmp` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 21 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/strcmp.html | index C Library Reference 8.0 | `b57b6b80b2335b41` |
| 98 | `memcpy` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 20 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/memcpy.html | index C Library Reference 8.0 | `9df70b6d7880a474` |
| 99 | `ioctl` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 19 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ioctl.html | index C Library Reference 8.0 | `8a9e8f3faa2e319d` |
| 100 | `printf` | `qnx/socketcan` | standard | `documented` | resolu_et_cite | 16 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/printf.html | index C Library Reference 8.0 | `d5268b2d2c128211` |

## Ce qui n'est pas resolu, et pourquoi

- `ND_NODE_CMP` (vocho/openqnx) : **absent** - present dans la C Library Reference 7.1, absent de tout le corpus 8.0
- `pthread_sleepon_lock` (qnx/bsp_raspberrypi-bcm2712-rpi5) : **absent** - present dans la C Library Reference 7.1, absent de tout le corpus 8.0
- `pthread_sleepon_unlock` (qnx/bsp_raspberrypi-bcm2712-rpi5) : **absent** - present dans la C Library Reference 7.1, absent de tout le corpus 8.0
- `InterruptAttach` (varghes/Raspberry-QNX) : **described_elsewhere** - appele dans la documentation 8.0 (livre com.qnx.doc.qnxsdp.migration) mais sans page propre dans la C Library Reference
- `fcfgopen` (varghes/Raspberry-QNX) : **absent** - present dans la C Library Reference 7.1, absent de tout le corpus 8.0
- `if_freenameindex` (qnx/socketcan) : **described_elsewhere** - decrit dans la documentation 8.0 mais sans page propre dans la C Library Reference
- `setsockopt` (qnx/socketcan) : **described_elsewhere** - decrit dans la documentation 8.0 mais sans page propre dans la C Library Reference

## Reproduire

```
# 1. cloner les 5 depots (superficiel)
for r in vocho/openqnx qnx/bsp_raspberrypi-bcm2712-rpi5 \
         varghes/Raspberry-QNX qnx/qnx-posix-publish-subscribe \
         qnx/socketcan ; do
  git clone --depth 1 --filter=blob:none --sparse \
      https://github.com/$r.git <dossier>
done
# 2. mesurer (le corpus fige est hors du depot : archive locale)
python3 tools/mesure_j4.py --clones <dossier> \
    --corpus /work/qnx-portmap-corpus-local/corpus \
    --out docs/mesure-J4/mesure-J4.json
```

Le test `tests/test_mesure_j4.py` verifie que le taux calcule par le script est identique au taux compte a la main sur 10 symboles donnes, et que la liste des 100 symboles est bien formee (pas de symbole vide, pas de doublon, pas de depot vide).
