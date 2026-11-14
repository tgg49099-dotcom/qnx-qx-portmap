#!/usr/bin/env bash
# Reconstruit le corpus de documentation QNX depuis le site officiel.
#
# La documentation QNX (c) QNX Software Systems Ltd / BlackBerry Limited
# n'est PAS redistribuee avec le depot : ce script la telecharge depuis
# https://www.qnx.com/developers/docs/ et l'ecrit dans un repertoire de
# travail. Le corpus fige n'est jamais modifie : le script refuse d'ecrire
# dans un repertoire protege.
#
# Usage :
#   bash scripts/bootstrap_corpus.sh --out corpus-downloaded
#   bash scripts/bootstrap_corpus.sh --out corpus-downloaded --max-pages 3
#
# Options :
#   --out DIR        repertoire de sortie (defaut : ./corpus-downloaded)
#   --delay SECONDS  delai entre deux requetes (defaut : 1.0)
#   --max-pages N    nombre maximum de pages par livre (defaut : aucune limite)
#   --versions V     versions a telecharger, separees par des virgules
#                    (defaut : 8.0,7.1)
#   --force          ecrase le contenu du repertoire de sortie
#
# Journal : <out>/download.log (une ligne par page telechargee).
# Code de sortie : 0 si le corpus a ete reconstruit, 1 sinon.

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="corpus-downloaded"
DELAY="1.0"
MAX_PAGES=""
VERSIONS="8.0,7.1"
FORCE=0

usage() {
    sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --out) OUT="$2"; shift 2 ;;
        --delay) DELAY="$2"; shift 2 ;;
        --max-pages) MAX_PAGES="$2"; shift 2 ;;
        --versions) VERSIONS="$2"; shift 2 ;;
        --force) FORCE=1; shift ;;
        -h|--help) usage 0 ;;
        *) echo "option inconnue : $1" >&2; usage 1 ;;
    esac
done

# --- garde-fous : on n'ecrit JAMAIS dans un corpus fige -------------------
OUT_ABS="$(mkdir -p "$OUT" && cd "$OUT" && pwd)"
if [ "$FORCE" -ne 1 ]; then
    if [ -f "$OUT_ABS/MANIFEST.json" ] && [ -f "$OUT_ABS/SHA256SUMS" ]; then
        echo "bootstrap_corpus: refus : $OUT_ABS contient deja un corpus fige." >&2
        echo "  Utilisez --force pour l'ecraser, ou choisissez un autre --out." >&2
        exit 1
    fi
fi
DIR="$(dirname "$OUT_ABS")"
while [ "$DIR" != "/" ]; do
    if [ -f "$DIR/CORPUS-FIGE.txt" ]; then
        echo "bootstrap_corpus: refus : $OUT_ABS est dans un corpus fige" \
             "($DIR/CORPUS-FIGE.txt)." >&2
        exit 1
    fi
    DIR="$(dirname "$DIR")"
done

CACHE="$OUT_ABS/cache"
LOG="$OUT_ABS/download.log"
mkdir -p "$CACHE"

echo "bootstrap_corpus : sortie   $OUT_ABS"
echo "bootstrap_corpus : cache    $CACHE"
echo "bootstrap_corpus : journal  $LOG"
echo "bootstrap_corpus : delai    ${DELAY}s entre deux requetes"
echo "bootstrap_corpus : versions $VERSIONS"

cd "$REPO_ROOT" || exit 1
PYTHONPATH="$REPO_ROOT" python3 - "$CACHE" "$LOG" "$DELAY" "$MAX_PAGES" "$VERSIONS" <<'PY'
import gzip
import hashlib
import os
import sys
import time

from qnx_portmap.refresh import BOOKS, BOOKS_71, Downloader

cache_dir, log_path, delay, max_pages, versions = sys.argv[1:6]
delay = float(delay)
max_pages = int(max_pages) if max_pages else None
wanted = [v.strip() for v in versions.split(",") if v.strip()]

books_by_version = {"8.0": BOOKS, "7.1": BOOKS_71}


class LoggingDownloader(Downloader):
    """Downloader qui journalise chaque page telechargee."""

    def fetch(self, url):
        before = self.fetched
        body = super(LoggingDownloader, self).fetch(url)
        path = self.cache_path(url)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        digest = ""
        if body:
            digest = hashlib.sha256(body.encode("utf-8", "replace")).hexdigest()
        status = "OK" if body else "ECHEC"
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write("%s\t%s\t%s\t%d\t%s\n"
                     % (time.strftime("%Y-%m-%dT%H:%M:%S"), status, url, size, digest))
        if self.fetched > before:
            sys.stderr.write("  telecharge %d pages\n" % self.fetched)
        return body


with open(log_path, "w", encoding="utf-8") as fh:
    fh.write("# date\tstatut\turl\toctets\tsha256\n")

dl = LoggingDownloader(cache_dir, delay=delay)
for version in wanted:
    books = books_by_version.get(version, [])
    sys.stderr.write("bootstrap_corpus : version %s (%d livres)\n"
                     % (version, len(books)))
    dl.crawl(version, books, max_pages,
             progress=lambda line: sys.stderr.write("  %s\n" % line))

sys.stderr.write("bootstrap_corpus : %d page(s) telechargee(s), %d echec(s)\n"
                 % (dl.fetched, len(dl.failed)))
if dl.failed:
    with open(log_path, "a", encoding="utf-8") as fh:
        for url, err in dl.failed:
            fh.write("# ECHEC\t%s\t%s\n" % (url, err))
PY
RC=$?
if [ "$RC" -ne 0 ]; then
    echo "bootstrap_corpus : echec du telechargement (code $RC)" >&2
    exit "$RC"
fi

# --- construction du corpus, avec le meme outil que le corpus fige --------
python3 tools/build_corpus.py --cache "$CACHE" --out "$OUT_ABS" || exit 1

echo
echo "bootstrap_corpus : corpus reconstruit dans $OUT_ABS"
echo "bootstrap_corpus : journal de telechargement : $LOG"
echo -n "bootstrap_corpus : sha256 du fichier SHA256SUMS : "
sha256sum "$OUT_ABS/SHA256SUMS" | cut -d' ' -f1
echo "bootstrap_corpus : pour l'utiliser :"
echo "  QX_PORTMAP_CORPUS=$OUT_ABS qnx-portmap abort accept bzero"
