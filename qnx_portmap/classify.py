"""Classification d'un symbole QNX : ou en est-il dans la documentation 8.0 ?

Quatre statuts, du plus favorable au plus defavorable :

``documented``
    Le symbole a sa propre page dans la C Library Reference 8.0.
``described_elsewhere``
    Le symbole n'a pas de page propre en 8.0 mais la documentation 8.0 le
    decrit (renvoi "The following are described elsewhere", ou mention dans
    un autre livre).
``absent``
    Le symbole etait dans la C Library Reference 7.1 et ne se trouve nulle
    part dans le corpus 8.0 : il a disparu.
``unknown``
    Le symbole est introuvable dans le corpus fige : il peut s'agir d'une
    faute de frappe, d'une macro du projet, ou d'un symbole ajoute apres
    le 14/11/2026. L'outil ne devine pas.

Chaque reponse porte la page officielle et la citation exacte.
"""

import re

from .corpus import LIB_REF_BOOK
from .extract import (bold_identifiers, parse_index_page, parse_topic_page,
                      sentences_with, strip_tags)

DOCUMENTED = "documented"
ELSEWHERE = "described_elsewhere"
ABSENT = "absent"
UNKNOWN = "unknown"

STATUS_ORDER = {DOCUMENTED: 0, ELSEWHERE: 1, ABSENT: 2, UNKNOWN: 3}

# Un nom d'API contient presque toujours une majuscule ou un tiret bas
# (``pthread_create``, ``MSG_...``) : un mot entierement en minuscules sans
# tiret bas ("argument", "any") est un mot anglais, pas un symbole.
_API_SHAPED = re.compile(r"[A-Z_]")

# Priorite de la liste de travail (1 = le plus urgent).
WORKLIST_PRIORITY = {
    (ABSENT, True): 1,        # absent et cite par le guide de migration officiel
    (ABSENT, False): 2,       # absent et sans aucune mention officielle
    (ELSEWHERE, False): 3,    # decrit ailleurs (renvoi d'index)
    (ELSEWHERE, True): 3,
}


class SymbolResult(object):
    """Le resultat pour un symbole."""

    def __init__(self, symbol):
        self.symbol = symbol
        self.status = UNKNOWN
        self.kind = ""
        self.in_71 = False
        self.in_80 = False
        self.url = ""
        self.citation = ""
        self.citation_source = ""
        self.citation_kind = ""
        self.see_urls = []
        self.mentioned_in_migration_guide = False
        self.migration_urls = []
        self.detail = ""
        self.note = ""

    @property
    def priority(self):
        if self.status == ABSENT:
            return WORKLIST_PRIORITY[(ABSENT, self.mentioned_in_migration_guide)]
        if self.status == ELSEWHERE:
            return WORKLIST_PRIORITY[(ELSEWHERE, False)]
        return 0

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "status": self.status,
            "kind": self.kind,
            "in_71": self.in_71,
            "in_80": self.in_80,
            "url": self.url,
            "citation": self.citation,
            "citation_source": self.citation_source,
            "citation_kind": self.citation_kind,
            "see_urls": list(self.see_urls),
            "mentioned_in_migration_guide": self.mentioned_in_migration_guide,
            "migration_urls": list(self.migration_urls),
            "detail": self.detail,
            "note": self.note,
            "priority": self.priority,
        }


class Classifier(object):
    """Repond sur l'etat d'un symbole dans la documentation QNX 8.0.

    Le corpus est lu sur disque, en local : aucun acces reseau.
    """

    def __init__(self, corpus, version="8.0", previous="7.1"):
        self.corpus = corpus
        self.version = version
        self.previous = previous
        self.entries = {}
        self.elsewhere = {}
        self.prev_entries = {}
        self.prev_elsewhere = {}
        self._load_indexes()
        self._scan_cache = {}
        self._bold_cache = {}
        self._migration_text = None

    # -- index ------------------------------------------------------------
    def _load_indexes(self):
        for page in self.corpus.index_pages(self.version):
            parsed = parse_index_page(self.corpus.html(page),
                                      self.corpus.manifest["docs_root"][self.version])
            self.entries.update(parsed["entries"])
            self.elsewhere.update(parsed["elsewhere"])
        for page in self.corpus.index_pages(self.previous):
            parsed = parse_index_page(self.corpus.html(page),
                                      self.corpus.manifest["docs_root"][self.previous])
            self.prev_entries.update(parsed["entries"])
            self.prev_elsewhere.update(parsed["elsewhere"])

    def index_stats(self):
        return {
            self.version: {"entries": len(self.entries), "elsewhere": len(self.elsewhere)},
            self.previous: {"entries": len(self.prev_entries), "elsewhere": len(self.prev_elsewhere)},
        }

    # -- recherche dans le corpus -----------------------------------------
    def _article_text(self, page):
        key = (page.version, page.book, page.topic)
        if key not in self._scan_cache:
            html = self.corpus.html(page)
            from .extract import article_of
            self._scan_cache[key] = strip_tags(article_of(html))
        return self._scan_cache[key]

    def _scan_corpus(self, symbols, call_form=True):
        """Cherche chaque symbole dans le corpus 8.0 (hors pages d'index).

        ``call_form`` : ne retenir que les occurrences de la forme
        ``symbole(`` (appel de fonction). Sinon, n'importe quelle mention
        avec frontiere de mot.

        Dans les deux cas, le symbole doit ressembler a un nom d'API (voir
        ``_is_api_name``) : sinon c'est un mot de la langue anglaise.

        Retourne {symbole: (page, phrase)}.
        """
        found = {}
        if not symbols:
            return found
        patterns = {}
        for sym in symbols:
            if call_form:
                body = r"%s\s*\(" % re.escape(sym)
            else:
                body = r"%s" % re.escape(sym)
            patterns[sym] = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % body)
        for page in self.corpus.pages:
            if page.version != self.version:
                continue
            if page.is_index_page:
                continue
            text = self._article_text(page)
            if not text:
                continue
            bold = None
            for sym, rx in patterns.items():
                if sym in found:
                    continue
                if sym not in text:      # test rapide, sans expression reguliere
                    continue
                sentences = sentences_with(text, sym, limit=1, call_form=call_form)
                if not sentences:
                    continue
                if not self._is_api_name(sym):
                    # Un mot anglais rencontre dans une phrase ("argument",
                    # "current") ou un nom de parametre suivi de "(" dans un
                    # extrait de code n'est pas un symbole QNX : l'annoncer
                    # comme "decrit ailleurs" serait faux.
                    continue
                found[sym] = (page, sentences[0])
        return found

    def _bold_ids(self, page):
        """Identifiants cites en gras dans une page (cache)."""
        key = (page.version, page.book, page.topic)
        if key not in self._bold_cache:
            self._bold_cache[key] = bold_identifiers(self.corpus.html(page))
        return self._bold_cache[key]

    def _is_api_name(self, sym):
        """Le symbole ressemble-t-il a un nom d'API plutot qu'a un mot ?

        Vrai si le symbole figure dans un index QNX (donc si la doc le
        connait comme symbole) ou si son nom contient une majuscule ou un
        tiret bas (``pthread_create``, ``MSG_NOTIFY``).
        """
        if sym in self.entries or sym in self.prev_entries:
            return True
        return bool(_API_SHAPED.search(sym))

    def _migration_mentions(self, symbols):
        """Symboles cites par le guide officiel de migration vers 8.0."""
        out = {}
        if self._migration_text is None:
            pages = self.corpus.migration_pages(self.version)
            self._migration_text = [(p, self._article_text(p)) for p in pages]
        for sym in symbols:
            rx = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(sym))
            hits = [p.url for p, text in self._migration_text if rx.search(text)]
            if hits:
                out[sym] = hits
        return out

    # -- classification ---------------------------------------------------
    def classify(self, symbols):
        """Classe une liste de symboles et renvoie une liste de SymbolResult."""
        unique = []
        for sym in symbols:
            sym = sym.strip() if isinstance(sym, str) else sym
            if sym and sym not in unique:
                unique.append(sym)

        results = []
        pending = []
        for sym in unique:
            res = SymbolResult(sym)
            prev = self.prev_entries.get(sym)
            cur = self.entries.get(sym)
            res.in_71 = prev is not None
            res.in_80 = cur is not None
            if cur is not None:
                res.status = DOCUMENTED
                res.kind = cur.get("kind", "")
                res.url = cur["url"]
                res.citation = cur.get("desc", "")
                res.citation_source = "index C Library Reference %s" % self.version
                res.detail = self._detail(cur["url"])
                res.note = ("present en 7.1 et en 8.0" if prev is not None
                            else "symbol nouveau en 8.0 (absent de la reference 7.1)")
            elif sym in self.elsewhere:
                info = self.elsewhere[sym]
                res.status = ELSEWHERE
                res.url = info["urls"][0] if info["urls"] else ""
                res.citation = info["text"]
                res.citation_source = "index C Library Reference %s, section \"described elsewhere\"" % self.version
                res.see_urls = list(info["urls"])
                res.note = ("decrit dans la documentation %s mais sans page propre "
                            "dans la C Library Reference" % self.version)
            else:
                pending.append(sym)
            results.append(res)

        if pending:
            # 1re passe : le symbole est appele comme une fonction
            found = self._scan_corpus(pending, call_form=True)
            # 2e passe : le symbole est seulement mentionne dans le texte
            rest = [s for s in pending if s not in found]
            mentioned = self._scan_corpus(rest, call_form=False)
            for res in results:
                sym = res.symbol
                if sym not in pending:
                    continue
                if sym in found:
                    page, sentence = found[sym]
                    res.status = ELSEWHERE
                    res.url = page.url
                    res.citation = sentence
                    res.citation_source = "%s, %s" % (page.book, page.topic)
                    res.citation_kind = "appel de fonction"
                    res.note = ("appele dans la documentation %s (livre %s) mais "
                                "sans page propre dans la C Library Reference"
                                % (self.version, page.book))
                elif sym in mentioned:
                    page, sentence = mentioned[sym]
                    res.status = ELSEWHERE
                    res.url = page.url
                    res.citation = sentence
                    res.citation_source = "%s, %s" % (page.book, page.topic)
                    res.citation_kind = ("cite en gras" if sym in self._bold_ids(page)
                                         else "mention")
                    res.note = ("seulement mentionne dans la documentation %s (livre %s) : "
                                "a verifier, le symbole peut n'etre plus un appel de fonction"
                                % (self.version, page.book))
                elif res.in_71:
                    res.status = ABSENT
                    prev = self.prev_entries[sym]
                    res.url = prev["url"]
                    res.citation = prev.get("desc", "")
                    res.citation_source = "index C Library Reference %s" % self.previous
                    res.citation_kind = "entree d'index"
                    res.note = ("present dans la C Library Reference %s, absent de tout "
                                "le corpus %s" % (self.previous, self.version))
                else:
                    res.status = UNKNOWN
                    res.note = ("introuvable dans le corpus %s fige : symbole inconnu, "
                                "erreur de saisie, ou ajout posterieur au %s"
                                % (self.version, self.corpus.manifest.get("consulted", "14/11/2026")))

        # le guide de migration officiel est une source a part : on le
        # consulte pour tout symbole de la liste de travail
        todo = [r.symbol for r in results if r.status in (ABSENT, ELSEWHERE)]
        migration = self._migration_mentions(todo)
        for res in results:
            if res.symbol in migration:
                res.mentioned_in_migration_guide = True
                res.migration_urls = migration[res.symbol]

        return results

    def _detail(self, url):
        """Premiere phrase de la section Description de la page du symbole."""
        page = self.corpus.find_url(url)
        if page is None:
            return ""
        parsed = parse_topic_page(self.corpus.html(page))
        return parsed.get("description", "")

    # -- liste de travail -------------------------------------------------
    @staticmethod
    def worklist(results):
        """Liste de travail de mise a niveau, par priorite decroissante."""
        items = [r for r in results if r.status in (ABSENT, ELSEWHERE)]
        items.sort(key=lambda r: (r.priority, r.symbol))
        return items
