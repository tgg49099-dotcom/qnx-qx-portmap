# Licence de la documentation QNX et du code de QX PORTMAP

**Date de consultation des sources : 14/11/2026.**

## 1. La documentation QNX n'est pas redistribuee

Les pages de documentation QNX citees par cet outil (C Library Reference,
User's Guide, io-sock User's Guide, Programming Guide, System Tuning Guide,
Migration Guide) sont :

> (c) QNX Software Systems Ltd / BlackBerry Limited.

Elles **ne sont pas redistribuees** avec ce depot. Aucune copie verbatim,
ni complete ni partielle au-dela des 12 extraits courts ranges dans
`tests/fixtures/`, n'est publiee. Voir `CORPUS-NON-PUBLIE.txt` pour le detail
et la procedure de reconstruction.

Page officielle de copyright de la documentation QNX 8.0 (consultee le
14/11/2026) :

  https://www.qnx.com/developers/docs/8.0/com.qnx.doc.copyright/topic/coverpage.html

Cette page indique que l'information de licence propre a chaque fichier se
trouve dans le QNX Software Center, accessible avec un compte myQNX. Elle ne
delivre aucune autorisation de redistribuer les pages de documentation. Aucune
demande d'autorisation n'a ete adressee a QNX ou a BlackBerry : le choix fait
est de ne pas redistribuer.

Les 12 fixtures de `tests/fixtures/` sont des extraits de 1 a 3 lignes, cites
avec leur URL source et la date de consultation, a titre de preuve de
fonctionnement de l'outil sur de la documentation reelle. Chaque fixture porte
aussi l'empreinte SHA-256 de la pageComplete dont elle est extraite.

## 2. Le code est libre (MIT)

Le code de QX PORTMAP (dans `qnx_portmap/`, `tests/`, `tools/`, `scripts/`)
est distribue sous licence MIT : voir le fichier `LICENSE` a la racine du
depot.

Copyright (c) 2026 QX PORTMAP contributors.

Le MIT ne s'applique pas a la documentation QNX : il ne couvre ni les pages
de documentation, ni les fixtures, qui restent la propriete de QNX Software
Systems Ltd / BlackBerry Limited et sont cites a titre d'extrait.

## 3. Les autres sources citees

Les renvois de la documentation QNX pointent vers des pages tierces, citees
sans etre reproduites :

- la documentation FreeBSD (`man.freebsd.org`), citee par la documentation
  QNX elle-meme dans ses renvois "described elsewhere" ;
- le site officiel de documentation QNX (`www.qnx.com/developers/docs/`),
  seule source des pages citees.

## 4. Resume

| Element | Statut |
|---|---|
| Code de l'outil (`qnx_portmap/`, `tests/`, `tools/`, `scripts/`) | MIT, redistribuable |
| Documentation QNX (3 426 pages) | (c) QNX Software Systems Ltd / BlackBerry Limited — **non redistribuee** |
| 12 fixtures (extraits de 1 a 3 lignes) | (c) QNX Software Systems Ltd / BlackBerry Limited — cites avec URL et date |
| Corpus fige (archive locale du slot) | hors du depot, jamais publie |
