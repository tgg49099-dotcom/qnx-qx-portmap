"""Extraction des faits utiles d'une page HTML de documentation QNX.

Le corpus QNX est genere par Oxygen (DITA-OT). Les balises stables sur
toutes les versions (7.1 et 8.0) sont :

- ``<article ...> ... </article>``      : le corps de la page ;
- ``<li role="treeitem">``             : une entree d'index ;
- ``<a href=".../topic/x/y.html">``    : le lien vers la page du symbole ;
- ``<span class="... apiname">``       : un nom de fonction ;
- ``<var class="... varname">``        : un nom de variable ;
- ``<span class="... keyword const">`` : un nom de constante ;
- ``<p class="... shortdesc">``        : la description courte officielle ;
- ``<strong>``                         : un texte en gras.

Rien ici n'est specifique a une version : le meme code lit 7.1 et 8.0.
"""

import html as _html
import re

# --- patrons globaux -------------------------------------------------------

_SCRIPT_STYLE = re.compile(r"(?is)<(script|style)\b.*?</\1>")
_ANY_TAG = re.compile(r"(?s)<[^>]+>")
_WS = re.compile(r"\s+")

# Une page peut contenir plusieurs <article> (sujets imbriques, comme le
# guide de migration) : on prend du premier au dernier.
_ARTICLE = re.compile(r"(?is)<article\b.*</article>")
_ARTICLE_OPEN = re.compile(r"(?is)<article\b")
_ARTICLE_CLOSE = re.compile(r"(?is)</article>")
_TOPIC_ITEM = re.compile(r"(?is)<li\b[^>]*role=\"treeitem\"[^>]*>(.*?)</li>")
_ANCHOR = re.compile(r'(?is)<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>')
_SHORTDESC = re.compile(r'(?is)<p\b[^>]*class="[^"]*shortdesc[^"]*"[^>]*>(.*?)</p>')
_APINAME = re.compile(r'(?is)<span\b[^>]*class="[^"]*\bapiname\b[^"]*"[^>]*>(.*?)</span>')
_VARNAME = re.compile(r'(?is)<var\b[^>]*class="[^"]*\bvarname\b[^"]*"[^>]*>(.*?)</var>')
_CONSTNAME = re.compile(r'(?is)<span\b[^>]*class="[^"]*\bconst\b[^"]*"[^>]*>(.*?)</span>')
_BOLD = re.compile(r"(?is)<(?:strong|b)\b[^>]*>(.*?)</(?:strong|b)>")
_H1 = re.compile(r"(?is)<h1\b[^>]*>(.*?)</h1>")
_H2 = re.compile(r"(?is)<h2\b[^>]*>(.*?)</h2>")
_H2_OPEN = re.compile(r"(?is)<h2\b[^>]*>([^<]*)")
_P = re.compile(r"(?is)<p\b[^>]*>(.*?)</p>")
_ELSEWHERE_HEAD = re.compile(r"(?is)<p\b[^>]*>(.*?)</p>")
_ROW = re.compile(r"(?is)<tr\b[^>]*>(.*?)</tr>")
_CELL = re.compile(r"(?is)<td\b[^>]*>(.*?)</td>")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_*]*")
_SENTENCE = re.compile(r"(?s)([^.!?]*?[A-Za-z_][A-Za-z0-9_]*[^.!?]*?[.!?])")


def strip_tags(fragment):
    """Retire les balises et normalise les espaces. Le texte reste lisible."""
    text = _ANY_TAG.sub(" ", fragment)
    return _WS.sub(" ", _html.unescape(text)).strip()


def article_of(page_html):
    """Retourne le corps <article> de la page (chaine vide si absent)."""
    m = _ARTICLE.search(page_html)
    if m:
        return m.group(0)
    start = _ARTICLE_OPEN.search(page_html)
    if not start:
        return ""
    end = _ARTICLE_CLOSE.search(page_html, start.end())
    return page_html[start.start(): end.end()] if end else page_html[start.start():]


def _inner_names(anchor_inner):
    """Noms de symboles portes par un lien d'index.

    Retourne la liste des noms, dans l'ordre, avec leur nature :
    'function' pour ``nom()``, 'variable' pour ``<var>``, 'constant' pour
    ``<span class="... const">``.
    """
    found = []
    for rx, kind in ((_APINAME, "function"), (_VARNAME, "variable"), (_CONSTNAME, "constant")):
        for m in rx.finditer(anchor_inner):
            raw = strip_tags(m.group(1))
            for name in _IDENTIFIER.findall(raw):
                if name not in [n for n, _ in found]:
                    found.append((name, kind))
    return found


def _names_in_text(text):
    """Noms listes dans un texte court : ``accept(), accept4()``."""
    out = []
    for chunk in re.split(r",(?![^()]*\))", text):
        chunk = chunk.strip()
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(", chunk)
        if m:
            out.append(m.group(1))
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_*]*)$", chunk)
        if m:
            out.append(m.group(1))
    return out


def parse_index_page(page_html, docs_root):
    """Parse une page d'index A-Z de la C Library Reference.

    Retourne un dict :
      ``entries``   : {nom: {"url":..., "desc":..., "kind":...}}
      ``elsewhere`` : {nom: {"text":..., "urls":[...]}}

    ``docs_root`` est la racine de la documentation, par exemple
    ``https://www.qnx.com/developers/docs/8.0/``.

    Note : dans la documentation QNX, la liste des symboles d'un chapitre se
    trouve dans l'arbre de navigation de la page (et non dans le corps
    ``<article>``), d'ou le parcours de la page entiere.
    """
    entries = {}
    elsewhere = {}
    article = article_of(page_html)

    for anchor in _ANCHOR.finditer(page_html):
        href, inner = anchor.group(1), anchor.group(2)
        names = _inner_names(inner)
        if not names:
            continue
        if "/topic/" not in href:
            continue
        url = _join(docs_root, href)
        desc = ""
        sd = _SHORTDESC.search(page_html, anchor.end(), anchor.end() + 900)
        if sd:
            desc = strip_tags(sd.group(1))
        for name, kind in names:
            entries.setdefault(name, {"url": url, "desc": desc, "kind": kind})

    # section "The following are described elsewhere:" -> tableau a deux colonnes
    for m in _ROW.finditer(article):
        cells = _CELL.findall(m.group(1))
        if len(cells) < 2:
            continue
        left, right = cells[0], cells[1]
        names = []
        for rx in (_APINAME, _VARNAME, _CONSTNAME):
            for mm in rx.finditer(left):
                names.extend(_names_in_text(strip_tags(mm.group(1))))
        if not names:
            names = _names_in_text(strip_tags(left))
        if not names:
            continue
        text = strip_tags(right)
        urls = []
        for a in _ANCHOR.finditer(right):
            u = a.group(1)
            if u.startswith("http"):
                urls.append(_html.unescape(u))
            else:
                urls.append(_join(docs_root, u))
        for name in names:
            elsewhere.setdefault(name, {"text": text, "urls": urls})

    return {"entries": entries, "elsewhere": elsewhere}


def _join(docs_root, href):
    """Fabrique une URL absolue a partir d'un href relatif Oxygen.

    Oxygen ecrit ``../../<livre>/topic/<x>.html`` pour un lien vers un autre
    livre du meme site de documentation, et ``../../../<livre>/topic/...``
    pour un lien vers une racine de documentation differente.
    """
    href = _html.unescape(href)
    if href.startswith("http"):
        return href
    root = docs_root.rstrip("/")
    if href.startswith("../../../"):
        return "%s/%s" % (root, href[len("../../../"):])
    if href.startswith("../../"):
        return "%s/%s" % (root, href[len("../../"):])
    if href.startswith("../"):
        return "%s/%s" % (root.rsplit("/", 1)[0], href[len("../"):])
    return "%s/%s" % (root, href.lstrip("/"))


def parse_topic_page(page_html):
    """Parse une page de symbole (page de manuel).

    Retourne un dict : ``title``, ``shortdesc``, ``description``,
    ``names``, ``bold`` (textes en gras du corps).
    """
    article = article_of(page_html)
    title = ""
    h1 = _H1.search(article)
    if h1:
        title = strip_tags(h1.group(1))
    shortdesc = ""
    sd = _SHORTDESC.search(article)
    if sd:
        shortdesc = strip_tags(sd.group(1))
    names = []
    for rx, scope in ((_APINAME, h1.group(1) if h1 else article),
                      (_VARNAME, h1.group(1) if h1 else article),
                      (_CONSTNAME, h1.group(1) if h1 else article)):
        for mm in rx.finditer(scope):
            raw = strip_tags(mm.group(1))
            for name in _IDENTIFIER.findall(raw):
                if name not in names:
                    names.append(name)
    # premiere phrase de la section Description
    description = ""
    heads = list(_H2_OPEN.finditer(article))
    for i, hm in enumerate(heads):
        if "description" not in strip_tags(hm.group(1)).lower():
            continue
        start = hm.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(article)
        for pm in _P.finditer(article, start, end):
            text = strip_tags(pm.group(1))
            if len(text) > 40:
                description = text
                break
        break
    bold = []
    for bm in _BOLD.finditer(article):
        text = strip_tags(bm.group(1))
        if text and text not in bold:
            bold.append(text)
    return {"title": title, "shortdesc": shortdesc, "description": description,
            "names": names, "bold": bold}


def sentences_with(text, needle, limit=3, max_len=320, call_form=False):
    """Sentences de ``text`` qui contiennent ``needle`` (identifiant exact).

    Utilise une frontiere de mot : ``needle`` ne doit pas matcher un
    identifiant plus long. Si ``call_form`` est vrai, seule la forme
    ``symbole(`` est retenue (appel de fonction). Si la phrase est trop
    longue, une fenetre autour du symbole est rendue, marquee par des
    points de suspension.
    """
    out = []
    if call_form:
        body = r"%s\s*\(" % re.escape(needle)
    else:
        body = r"%s" % re.escape(needle)
    pattern = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % body)
    for m in pattern.finditer(text):
        start = text.rfind(".", 0, m.start())
        start = 0 if start < 0 else start + 1
        end = text.find(".", m.end())
        end = len(text) if end < 0 else end + 1
        chunk = text[start:end].strip()
        if len(chunk) > max_len:
            lo = max(start, m.start() - 140)
            hi = min(end, m.end() + 160)
            piece = text[lo:hi].strip()
            if lo > 0:
                cut = piece.find(" ")
                piece = piece[cut + 1:] if 0 <= cut < 40 else piece
                piece = "... " + piece
            if hi < end:
                cut = piece.rfind(" ")
                piece = piece[:cut] if cut > 0 else piece
                piece = piece + " ..."
            chunk = piece
        if chunk and chunk not in out:
            out.append(chunk)
        if len(out) >= limit:
            break
    return out
