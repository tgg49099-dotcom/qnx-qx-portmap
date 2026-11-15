"""Classification of a QNX symbol: where does it stand in the 8.0 documentation?

Four statuses, from the most favourable to the least favourable:

``documented``
    The symbol has its own page in the 8.0 C Library Reference.
``described_elsewhere``
    The symbol has no page of its own in 8.0 but the 8.0 documentation
    describes it ("The following are described elsewhere" cross reference, or
    a mention in another book).
``absent``
    The symbol was in the 7.1 C Library Reference and is nowhere in the 8.0
    corpus: it has disappeared.
``unknown``
    The symbol is not found in the frozen corpus: it may be a typo, a macro
    of the project, or a symbol added after 14/11/2026. The tool does not
    guess.

Every answer carries the official page and the exact quotation.
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

# Notes and labels emitted with every result, in the two output
# languages. The French strings reproduce exactly the historical
# output of the tool; the console default is English, the French
# strings stay for the `--lang fr` mode.
NOTES = {
    "fr": {
        "present_both": "present en 7.1 et en 8.0",
        "new_in_80": "symbol nouveau en 8.0 (absent de la reference 7.1)",
        "elsewhere_no_page": "decrit dans la documentation %s mais sans page propre "
                             "dans la C Library Reference",
        "called_no_page": "appele dans la documentation %s (livre %s) mais "
                          "sans page propre dans la C Library Reference",
        "mentioned_only": "seulement mentionne dans la documentation %s (livre %s) : "
                          "a verifier, le symbole peut n'etre plus un appel de fonction",
        "absent_note": "present dans la C Library Reference %s, absent de tout "
                       "le corpus %s",
        "unknown_note": "introuvable dans le corpus %s fige : symbole inconnu, "
                        "erreur de saisie, ou ajout posterieur au %s",
        "kind_call": "appel de fonction",
        "kind_bold": "cite en gras",
        "kind_mention": "mention",
        "kind_index": "entree d'index",
    },
    "en": {
        "present_both": "present in 7.1 and in 8.0",
        "new_in_80": "new symbol in 8.0 (absent from the 7.1 reference)",
        "elsewhere_no_page": "described in the %s documentation but without a page "
                             "of its own in the C Library Reference",
        "called_no_page": "called in the %s documentation (book %s) but "
                          "without a page of its own in the C Library Reference",
        "mentioned_only": "only mentioned in the %s documentation (book %s): "
                          "to be checked, the symbol may no longer be a function call",
        "absent_note": "present in the C Library Reference %s, absent from the "
                       "whole %s corpus",
        "unknown_note": "not found in the frozen %s corpus: unknown symbol, "
                        "typo, or added after %s",
        "kind_call": "function call",
        "kind_bold": "cited in bold",
        "kind_mention": "mention",
        "kind_index": "index entry",
    },
}

# An API name almost always contains an upper-case letter or an
# underscore (``pthread_create``, ``MSG_...``): a word written entirely
# in lower case without an underscore ("argument", "any") is an English
# word, not a symbol.
_API_SHAPED = re.compile(r"[A-Z_]")

# Priority of the work list (1 = the most urgent).
WORKLIST_PRIORITY = {
    (ABSENT, True): 1,        # absent and cited by the official migration guide
    (ABSENT, False): 2,       # absent and without any official mention
    (ELSEWHERE, False): 3,    # described elsewhere (index cross-reference)
    (ELSEWHERE, True): 3,
}


class SymbolResult(object):
    """The result for one symbol."""

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
    """Answers the state of a symbol in the QNX 8.0 documentation.

    The corpus is read from the local disk: no network access.
    """

    def __init__(self, corpus, version="8.0", previous="7.1", lang="fr"):
        self.corpus = corpus
        self.version = version
        self.previous = previous
        self.lang = lang if lang in NOTES else "fr"
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

    # -- search in the corpus ---------------------------------------------
    def _article_text(self, page):
        key = (page.version, page.book, page.topic)
        if key not in self._scan_cache:
            html = self.corpus.html(page)
            from .extract import article_of
            self._scan_cache[key] = strip_tags(article_of(html))
        return self._scan_cache[key]

    def _scan_corpus(self, symbols, call_form=True):
        """Searches every symbol in the 8.0 corpus (index pages excluded).

        ``call_form``: keep only the occurrences of the form
        ``symbol(`` (function call). Otherwise, any mention with a
        word boundary is kept.

        In both cases, the symbol must look like an API name (see
        ``_is_api_name``): otherwise it is an English word.

        Returns {symbol: (page, sentence)}.
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
                if sym not in text:      # quick test, without a regular expression
                    continue
                sentences = sentences_with(text, sym, limit=1, call_form=call_form)
                if not sentences:
                    continue
                if not self._is_api_name(sym):
                    # An English word met in a sentence ("argument",
                    # "current") or a parameter name followed by "(" in a
                    # code extract is not a QNX symbol: reporting it as
                    # "described elsewhere" would be wrong.
                    continue
                found[sym] = (page, sentences[0])
        return found

    def _bold_ids(self, page):
        """Identifiers cited in bold on a page (cached)."""
        key = (page.version, page.book, page.topic)
        if key not in self._bold_cache:
            self._bold_cache[key] = bold_identifiers(self.corpus.html(page))
        return self._bold_cache[key]

    def _is_api_name(self, sym):
        """Does the symbol look like an API name rather than a plain word?

        True if the symbol appears in a QNX index (so the documentation
        knows it as a symbol) or if its name contains an upper-case
        letter or an underscore (``pthread_create``, ``MSG_NOTIFY``).
        """
        if sym in self.entries or sym in self.prev_entries:
            return True
        return bool(_API_SHAPED.search(sym))

    def _migration_mentions(self, symbols):
        """Symbols cited by the official migration guide to 8.0."""
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

    # -- classification --------------------------------------------------
    def classify(self, symbols):
        """Classifies a list of symbols and returns a list of SymbolResult."""
        unique = []
        for sym in symbols:
            sym = sym.strip() if isinstance(sym, str) else sym
            if sym and sym not in unique:
                unique.append(sym)

        n = NOTES[self.lang]
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
                res.note = (n["present_both"] if prev is not None
                            else n["new_in_80"])
            elif sym in self.elsewhere:
                info = self.elsewhere[sym]
                res.status = ELSEWHERE
                res.url = info["urls"][0] if info["urls"] else ""
                res.citation = info["text"]
                res.citation_source = "index C Library Reference %s, section \"described elsewhere\"" % self.version
                res.see_urls = list(info["urls"])
                res.note = n["elsewhere_no_page"] % self.version
            else:
                pending.append(sym)
            results.append(res)

        if pending:
            # 1st pass: the symbol is called as a function
            found = self._scan_corpus(pending, call_form=True)
            # 2nd pass: the symbol is only mentioned in the text
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
                    res.citation_kind = n["kind_call"]
                    res.note = n["called_no_page"] % (self.version, page.book)
                elif sym in mentioned:
                    page, sentence = mentioned[sym]
                    res.status = ELSEWHERE
                    res.url = page.url
                    res.citation = sentence
                    res.citation_source = "%s, %s" % (page.book, page.topic)
                    res.citation_kind = (n["kind_bold"] if sym in self._bold_ids(page)
                                         else n["kind_mention"])
                    res.note = n["mentioned_only"] % (self.version, page.book)
                elif res.in_71:
                    res.status = ABSENT
                    prev = self.prev_entries[sym]
                    res.url = prev["url"]
                    res.citation = prev.get("desc", "")
                    res.citation_source = "index C Library Reference %s" % self.previous
                    res.citation_kind = n["kind_index"]
                    res.note = n["absent_note"] % (self.previous, self.version)
                else:
                    res.status = UNKNOWN
                    res.note = n["unknown_note"] % (self.version,
                                                    self.corpus.manifest.get("consulted",
                                                                             "14/11/2026"))

        # the official migration guide is a source of its own: it is
        # consulted for every symbol of the work list
        todo = [r.symbol for r in results if r.status in (ABSENT, ELSEWHERE)]
        migration = self._migration_mentions(todo)
        for res in results:
            if res.symbol in migration:
                res.mentioned_in_migration_guide = True
                res.migration_urls = migration[res.symbol]

        return results

    def _detail(self, url):
        """First sentence of the Description section of the page of the symbol."""
        page = self.corpus.find_url(url)
        if page is None:
            return ""
        parsed = parse_topic_page(self.corpus.html(page))
        return parsed.get("description", "")

    # -- work list --------------------------------------------------------
    @staticmethod
    def worklist(results):
        """Upgrade work list, by decreasing priority."""
        items = [r for r in results if r.status in (ABSENT, ELSEWHERE)]
        items.sort(key=lambda r: (r.priority, r.symbol))
        return items
